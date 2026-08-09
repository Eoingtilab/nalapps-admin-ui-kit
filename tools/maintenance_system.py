#!/usr/bin/env python3
"""Generate NalApps redacted system information and maintenance UI."""
from __future__ import annotations

from scaffold_plugin import namespace_suffix, php_const_prefix


def system_info_class(profile: dict) -> str:
    ns = namespace_suffix(profile["slug"])
    slug = profile["slug"]
    prefix = php_const_prefix(slug)
    section = "nalapps_" + slug.replace("-", "_")
    return f'''<?php
/**
 * Redacted system information for diagnostics and Site Health.
 *
 * @package {ns}
 */

namespace EOINGTI\\Plugins\\{ns};

if ( ! defined( 'ABSPATH' ) ) {{
\texit;
}}

final class System_Info {{
\tpublic function __construct() {{
\t\tadd_filter( 'debug_information', array( $this, 'site_health_info' ) );
\t}}

\tpublic static function values() {{
\t\t$theme = wp_get_theme();
\t\treturn array(
\t\t\t'Plugin version'      => {prefix}_VERSION,
\t\t\t'Standard version'    => {prefix}_STANDARD_VERSION,
\t\t\t'WordPress version'   => get_bloginfo( 'version' ),
\t\t\t'PHP version'         => PHP_VERSION,
\t\t\t'Locale'              => get_locale(),
\t\t\t'Multisite'           => is_multisite() ? 'yes' : 'no',
\t\t\t'HTTPS'               => is_ssl() ? 'yes' : 'no',
\t\t\t'Memory limit'        => ini_get( 'memory_limit' ),
\t\t\t'Upload max size'     => ini_get( 'upload_max_filesize' ),
\t\t\t'WP_DEBUG'            => defined( 'WP_DEBUG' ) && WP_DEBUG ? 'on' : 'off',
\t\t\t'DISABLE_WP_CRON'     => defined( 'DISABLE_WP_CRON' ) && DISABLE_WP_CRON ? 'on' : 'off',
\t\t\t'Active theme'        => $theme->get( 'Name' ) . ' ' . $theme->get( 'Version' ),
\t\t\t'Rollback backups'    => (string) count( Rollback_Manager::list_backups() ),
\t\t\t'Data snapshots'      => (string) count( Data_Portability::list_snapshots() ),
\t\t\t'Portable options'    => (string) count( Data_Portability::option_names() ),
\t\t\t'Portable post types' => (string) count( Data_Portability::post_types() ),
\t\t);
\t}}

\tpublic function site_health_info( $debug_info ) {{
\t\t$fields = array();
\t\tforeach ( self::values() as $label => $value ) {{
\t\t\t$fields[ sanitize_key( $label ) ] = array(
\t\t\t\t'label' => $label,
\t\t\t\t'value' => (string) $value,
\t\t\t);
\t\t}}
\t\t$debug_info['{section}'] = array(
\t\t\t'label'  => '{profile["plugin_name"]}',
\t\t\t'fields' => $fields,
\t\t);
\t\treturn $debug_info;
\t}}
}}
'''


def maintenance_page_class(profile: dict) -> str:
    ns = namespace_suffix(profile["slug"])
    slug = profile["slug"]
    action = slug.replace("-", "_")
    policy_option = f"{action}_uninstall_policy"
    default_policy = profile.get("uninstall_policy", "preserve")
    return f'''<?php
/**
 * Common maintenance UI for rollback, backup, diagnostics and uninstall policy.
 *
 * @package {ns}
 */

namespace EOINGTI\\Plugins\\{ns};

if ( ! defined( 'ABSPATH' ) ) {{
\texit;
}}

final class Maintenance_Page {{
\tconst POLICY_OPTION = '{policy_option}';

\tpublic function __construct() {{
\t\tadd_action( 'admin_menu', array( $this, 'register_page' ) );
\t\tadd_action( 'admin_post_{action}_save_uninstall_policy', array( $this, 'save_uninstall_policy' ) );
\t}}

\tpublic function register_page() {{
\t\tadd_options_page(
\t\t\t'{profile["plugin_name"]} Maintenance',
\t\t\t'{profile["plugin_name"]} Maintenance',
\t\t\t'manage_options',
\t\t\t'{slug}-maintenance',
\t\t\tarray( $this, 'render' )
\t\t);
\t}}

\tpublic function render() {{
\t\tif ( ! current_user_can( 'manage_options' ) ) {{
\t\t\twp_die( esc_html( 'Insufficient permissions.' ) );
\t\t}}
\t\t$policy = get_option( self::POLICY_OPTION, '{default_policy}' );
\t\techo '<div class="wrap"><h1>' . esc_html( '{profile["plugin_name"]} Maintenance' ) . '</h1>';
\t\techo '<h2>System Information</h2><table class="widefat striped"><tbody>';
\t\tforeach ( System_Info::values() as $label => $value ) {{
\t\t\techo '<tr><th>' . esc_html( $label ) . '</th><td>' . esc_html( (string) $value ) . '</td></tr>';
\t\t}}
\t\techo '</tbody></table>';

\t\techo '<h2>Data Backup</h2><p>Export a portable JSON backup or import one created by this plugin. A local snapshot is created before import.</p>';
\t\techo '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '"><input type="hidden" name="action" value="{action}_export_data">';
\t\twp_nonce_field( '{action}_export_data' );
\t\tsubmit_button( 'Export data', 'secondary', 'submit', false );
\t\techo '</form>';
\t\techo '<form method="post" enctype="multipart/form-data" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '"><input type="hidden" name="action" value="{action}_import_data">';
\t\twp_nonce_field( '{action}_import_data' );
\t\techo '<input type="file" name="nalapps_backup" accept="application/json,.json" required> ';
\t\tsubmit_button( 'Import data', 'secondary', 'submit', false );
\t\techo '</form>';

\t\techo '<h2>Rollback</h2><p>Code rollback does not automatically reverse database migrations. Restore data separately when required.</p>';
\t\t$backups = Rollback_Manager::list_backups();
\t\tif ( empty( $backups ) ) {{
\t\t\techo '<p>No rollback backup is available yet. One is created automatically before this plugin is updated.</p>';
\t\t}}
\t\tforeach ( $backups as $backup ) {{
\t\t\techo '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '" style="margin-bottom:8px"><input type="hidden" name="action" value="{action}_rollback"><input type="hidden" name="backup" value="' . esc_attr( $backup ) . '">';
\t\t\twp_nonce_field( '{action}_rollback' );
\t\t\techo '<code>' . esc_html( $backup ) . '</code> ';
\t\t\tsubmit_button( 'Rollback', 'secondary', 'submit', false );
\t\t\techo '</form>';
\t\t}}

\t\techo '<h2>Uninstall Data Policy</h2><p>Data is preserved by default. Complete deletion is irreversible and runs only when the plugin is uninstalled.</p>';
\t\techo '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '"><input type="hidden" name="action" value="{action}_save_uninstall_policy">';
\t\twp_nonce_field( '{action}_save_uninstall_policy' );
\t\techo '<label><input type="radio" name="policy" value="preserve" ' . checked( 'preserve', $policy, false ) . '> Preserve data</label><br>';
\t\techo '<label><input type="radio" name="policy" value="delete_all" ' . checked( 'delete_all', $policy, false ) . '> Delete all declared plugin data on uninstall</label>';
\t\tsubmit_button( 'Save uninstall policy' );
\t\techo '</form></div>';
\t}}

\tpublic function save_uninstall_policy() {{
\t\tif ( ! current_user_can( 'manage_options' ) ) {{
\t\t\twp_die( esc_html( 'Insufficient permissions.' ) );
\t\t}}
\t\tcheck_admin_referer( '{action}_save_uninstall_policy' );
\t\t$policy = isset( $_POST['policy'] ) ? sanitize_key( wp_unslash( $_POST['policy'] ) ) : 'preserve';
\t\tif ( ! in_array( $policy, array( 'preserve', 'delete_all' ), true ) ) {{
\t\t\t$policy = 'preserve';
\t\t}}
\t\tupdate_option( self::POLICY_OPTION, $policy, false );
\t\twp_safe_redirect( admin_url( 'options-general.php?page={slug}-maintenance&state=policy_saved' ) );
\t\texit;
\t}}
}}
'''
