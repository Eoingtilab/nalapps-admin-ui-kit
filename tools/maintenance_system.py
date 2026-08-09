#!/usr/bin/env python3
"""Generate NalApps redacted system information and maintenance center UI."""
from __future__ import annotations

from scaffold_plugin import namespace_suffix, php_const_prefix


def system_info_class(profile: dict) -> str:
    ns = namespace_suffix(profile["slug"])
    slug = profile["slug"]
    prefix = php_const_prefix(slug)
    section = "nalapps_" + slug.replace("-", "_")
    return f'''<?php
/** Redacted system information for diagnostics and Site Health. @package {ns} */
namespace EOINGTI\\Plugins\\{ns};
if ( ! defined( 'ABSPATH' ) ) {{ exit; }}
final class System_Info {{
\tpublic function __construct() {{ add_filter( 'debug_information', array( $this, 'site_health_info' ) ); }}
\tpublic static function values() {{
\t\t$theme = wp_get_theme();
\t\treturn array(
\t\t\t'Plugin version' => {prefix}_VERSION,
\t\t\t'Standard version' => {prefix}_STANDARD_VERSION,
\t\t\t'WordPress version' => get_bloginfo( 'version' ),
\t\t\t'PHP version' => PHP_VERSION,
\t\t\t'Locale' => get_locale(),
\t\t\t'Multisite' => is_multisite() ? 'yes' : 'no',
\t\t\t'HTTPS' => is_ssl() ? 'yes' : 'no',
\t\t\t'Memory limit' => ini_get( 'memory_limit' ),
\t\t\t'Upload max size' => ini_get( 'upload_max_filesize' ),
\t\t\t'WP_DEBUG' => defined( 'WP_DEBUG' ) && WP_DEBUG ? 'on' : 'off',
\t\t\t'Active theme' => $theme->get( 'Name' ) . ' ' . $theme->get( 'Version' ),
\t\t\t'Rollback backups' => (string) count( Rollback_Manager::list_backups() ),
\t\t\t'Rollback releases' => (string) count( Rollback_Manager::list_release_versions() ),
\t\t\t'Data snapshots' => (string) count( Data_Portability::list_snapshots() ),
\t\t);
\t}}
\tpublic function site_health_info( $debug_info ) {{
\t\t$fields = array();
\t\tforeach ( self::values() as $label => $value ) {{
\t\t\t$fields[ sanitize_key( $label ) ] = array( 'label' => $label, 'value' => (string) $value );
\t\t}}
\t\t$debug_info['{section}'] = array( 'label' => '{profile["plugin_name"]}', 'fields' => $fields );
\t\treturn $debug_info;
\t}}
}}
'''


def maintenance_page_class(profile: dict) -> str:
    ns = namespace_suffix(profile["slug"])
    slug = profile["slug"]
    prefix = php_const_prefix(slug)
    action = slug.replace("-", "_")
    policy_option = f"{action}_uninstall_policy"
    default_policy = profile.get("uninstall_policy", "preserve")
    return f'''<?php
/** Common maintenance center for backup, restore, rollback and uninstall policy. @package {ns} */
namespace EOINGTI\\Plugins\\{ns};
if ( ! defined( 'ABSPATH' ) ) {{ exit; }}
final class Maintenance_Page {{
\tconst POLICY_OPTION = '{policy_option}';
\tpublic function __construct() {{
\t\tadd_action( 'admin_menu', array( $this, 'register_page' ) );
\t\tadd_action( 'admin_enqueue_scripts', array( $this, 'enqueue_assets' ) );
\t\tadd_action( 'admin_post_{action}_save_uninstall_policy', array( $this, 'save_uninstall_policy' ) );
\t}}
\tpublic function register_page() {{
\t\tadd_options_page( '{profile["plugin_name"]} Maintenance', '{profile["plugin_name"]} Maintenance', 'manage_options', '{slug}-maintenance', array( $this, 'render' ) );
\t}}
\tpublic function enqueue_assets( $hook ) {{
\t\tif ( 'settings_page_{slug}-maintenance' !== $hook ) {{ return; }}
\t\twp_enqueue_style( '{slug}-nalapps-admin-ui', {prefix}_URL . 'assets/css/nalapps-admin-ui.css', array(), {prefix}_VERSION );
\t\twp_enqueue_style( '{slug}-nalapps-admin-typography', {prefix}_URL . 'assets/css/nalapps-admin-typography.css', array( '{slug}-nalapps-admin-ui' ), {prefix}_VERSION );
\t\tadd_filter( 'admin_body_class', array( $this, 'body_class' ) );
\t}}
\tpublic function body_class( $classes ) {{ return $classes . ' nalapps-admin-screen'; }}
\tpublic function render() {{
\t\tif ( ! current_user_can( 'manage_options' ) ) {{ wp_die( esc_html( 'Insufficient permissions.' ) ); }}
\t\t$delete           = 'delete_all' === get_option( self::POLICY_OPTION, '{default_policy}' );
\t\t$backups          = Rollback_Manager::list_backups();
\t\t$release_versions = Rollback_Manager::list_release_versions();
\t\t$snapshots        = Data_Portability::list_snapshots();
\t\techo '<div class="wrap nalapps-maintenance">';
\t\techo '<div class="nalapps-page-header"><div class="nalapps-page-header__copy"><span class="nalapps-page-kicker">EOINGTI LAB · NALAPPS</span><h1>{profile["plugin_name"]} Maintenance</h1><p>Backup, restore and verified version rollback in one place.</p></div></div>';

\t\techo '<div class="nalapps-panel"><div class="nalapps-panel-heading"><div><h2>Data backup and restore</h2><p>Export declared plugin data or restore a compatible JSON backup. License secrets are never exported.</p></div></div><div class="nalapps-inline-actions">';
\t\techo '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '"><input type="hidden" name="action" value="{action}_export_data">';
\t\twp_nonce_field( '{action}_export_data' ); submit_button( 'Download data backup', 'primary', 'submit', false ); echo '</form>';
\t\techo '<form method="post" enctype="multipart/form-data" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '"><input type="hidden" name="action" value="{action}_import_data">';
\t\twp_nonce_field( '{action}_import_data' ); echo '<input type="file" name="nalapps_backup" accept="application/json,.json" required> '; submit_button( 'Restore backup', 'secondary', 'submit', false ); echo '</form></div>';
\t\techo '<p class="description">A local data snapshot is created before restore. Snapshots: ' . esc_html( (string) count( $snapshots ) ) . '</p></div>';

\t\techo '<div class="nalapps-panel"><div class="nalapps-panel-heading"><div><h2>Version rollback</h2><p>Select a previous verified GitHub Release Asset. Source Code archives are never accepted. Current code and data are backed up before rollback.</p></div></div>';
\t\tif ( $release_versions ) {{
\t\t\techo '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '" class="nalapps-inline-actions"><input type="hidden" name="action" value="{action}_release_rollback">';
\t\t\twp_nonce_field( '{action}_release_rollback' );
\t\t\techo '<label><strong>Rollback version</strong> <select name="version" required><option value="">Select version</option>';
\t\t\tforeach ( array_keys( $release_versions ) as $version ) {{ echo '<option value="' . esc_attr( $version ) . '">' . esc_html( $version ) . '</option>'; }}
\t\t\techo '</select></label> '; submit_button( 'Rollback to selected version', 'secondary', 'submit', false ); echo '</form>';
\t\t}} else {{ echo '<div class="nalapps-notice">No verified previous Release Asset is currently available.</div>'; }}
\t\techo '</div>';

\t\techo '<div class="nalapps-panel"><div class="nalapps-panel-heading"><div><h2>Local safety backups</h2><p>Emergency code backups created automatically before update or rollback.</p></div></div><div class="nalapps-stack">';
\t\tif ( empty( $backups ) ) {{ echo '<div class="nalapps-notice">No local code backup exists yet.</div>'; }}
\t\tforeach ( $backups as $backup ) {{
\t\t\techo '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '" class="nalapps-inline-actions"><input type="hidden" name="action" value="{action}_rollback"><input type="hidden" name="backup" value="' . esc_attr( $backup ) . '">';
\t\t\twp_nonce_field( '{action}_rollback' ); echo '<code>' . esc_html( $backup ) . '</code> '; submit_button( 'Restore local backup', 'secondary', 'submit', false ); echo '</form>';
\t\t}}
\t\techo '</div></div>';

\t\techo '<div class="nalapps-panel nalapps-danger-zone"><div class="nalapps-panel-heading"><div><h2>Uninstall data policy</h2><p>Preserve is the default. Complete deletion is explicit and irreversible.</p></div></div><form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '"><input type="hidden" name="action" value="{action}_save_uninstall_policy">';
\t\twp_nonce_field( '{action}_save_uninstall_policy' );
\t\techo '<div class="nalapps-toggle-row"><div class="nalapps-toggle-copy"><strong>Delete all plugin data on uninstall</strong><span>Only plugin-owned data may be deleted.</span></div><label class="nalapps-switch"><input type="checkbox" name="delete_all" value="1" ' . checked( true, $delete, false ) . '><span class="nalapps-switch__track"></span></label></div>';
\t\tsubmit_button( 'Save uninstall policy', 'secondary' ); echo '</form></div>';

\t\techo '<div class="nalapps-panel"><div class="nalapps-panel-heading"><div><h2>System information</h2><p>Redacted diagnostic values only.</p></div></div><table class="widefat striped"><tbody>';
\t\tforeach ( System_Info::values() as $label => $value ) {{ echo '<tr><th>' . esc_html( $label ) . '</th><td>' . esc_html( (string) $value ) . '</td></tr>'; }}
\t\techo '</tbody></table></div></div>';
\t}}
\tpublic function save_uninstall_policy() {{
\t\tif ( ! current_user_can( 'manage_options' ) ) {{ wp_die( esc_html( 'Insufficient permissions.' ) ); }}
\t\tcheck_admin_referer( '{action}_save_uninstall_policy' );
\t\t$policy = isset( $_POST['delete_all'] ) && '1' === sanitize_text_field( wp_unslash( $_POST['delete_all'] ) ) ? 'delete_all' : 'preserve';
\t\tupdate_option( self::POLICY_OPTION, $policy, false );
\t\twp_safe_redirect( admin_url( 'options-general.php?page={slug}-maintenance&state=policy_saved' ) ); exit;
\t}}
}}
'''
