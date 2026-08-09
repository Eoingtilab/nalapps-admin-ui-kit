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
\t\t\t'Plugin version'    => {prefix}_VERSION,
\t\t\t'Standard version'  => {prefix}_STANDARD_VERSION,
\t\t\t'WordPress version' => get_bloginfo( 'version' ),
\t\t\t'PHP version'       => PHP_VERSION,
\t\t\t'Locale'            => get_locale(),
\t\t\t'Multisite'         => is_multisite() ? 'yes' : 'no',
\t\t\t'HTTPS'             => is_ssl() ? 'yes' : 'no',
\t\t\t'Memory limit'      => ini_get( 'memory_limit' ),
\t\t\t'Upload max size'   => ini_get( 'upload_max_filesize' ),
\t\t\t'WP_DEBUG'          => defined( 'WP_DEBUG' ) && WP_DEBUG ? 'on' : 'off',
\t\t\t'Active theme'      => $theme->get( 'Name' ) . ' ' . $theme->get( 'Version' ),
\t\t\t'Rollback backups'  => (string) count( Rollback_Manager::list_backups() ),
\t\t\t'Rollback releases' => (string) count( Rollback_Manager::list_release_versions() ),
\t\t\t'Data snapshots'    => (string) count( Data_Portability::list_snapshots() ),
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
    prefix = php_const_prefix(slug)
    action = slug.replace("-", "_")
    policy_option = f"{action}_uninstall_policy"
    default_policy = profile.get("uninstall_policy", "preserve")
    return f'''<?php
/**
 * Common maintenance center for backup, restore, rollback and uninstall policy.
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
\t\tadd_action( 'admin_enqueue_scripts', array( $this, 'enqueue_assets' ) );
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

\tpublic function enqueue_assets( $hook ) {{
\t\tif ( 'settings_page_{slug}-maintenance' !== $hook ) {{
\t\t\treturn;
\t\t}}
\t\twp_enqueue_style( '{slug}-nalapps-admin-ui', {prefix}_URL . 'assets/css/nalapps-admin-ui.css', array(), {prefix}_VERSION );
\t\twp_enqueue_style( '{slug}-nalapps-admin-typography', {prefix}_URL . 'assets/css/nalapps-admin-typography.css', array( '{slug}-nalapps-admin-ui' ), {prefix}_VERSION );
\t\tadd_filter( 'admin_body_class', array( $this, 'body_class' ) );
\t}}

\tpublic function body_class( $classes ) {{
\t\treturn $classes . ' nalapps-admin-screen';
\t}}

\tpublic function render() {{
\t\tif ( ! current_user_can( 'manage_options' ) ) {{
\t\t\twp_die( esc_html( 'Insufficient permissions.' ) );
\t\t}}

\t\t$delete           = 'delete_all' === get_option( self::POLICY_OPTION, '{default_policy}' );
\t\t$backups          = Rollback_Manager::list_backups();
\t\t$release_versions = Rollback_Manager::list_release_versions();
\t\t$snapshots        = Data_Portability::list_snapshots();
\t\t?>
\t\t<div class="wrap nalapps-maintenance">
\t\t\t<div class="nalapps-page-header">
\t\t\t\t<div class="nalapps-page-header__copy">
\t\t\t\t\t<span class="nalapps-page-kicker">EOINGTI LAB · NALAPPS</span>
\t\t\t\t\t<h1><?php echo esc_html( '{profile["plugin_name"]} Maintenance' ); ?></h1>
\t\t\t\t\t<p>Backup, restore and verified version rollback in one place.</p>
\t\t\t\t</div>
\t\t\t</div>

\t\t\t<div class="nalapps-panel">
\t\t\t\t<div class="nalapps-panel-heading">
\t\t\t\t\t<div>
\t\t\t\t\t\t<h2>Data backup and restore</h2>
\t\t\t\t\t\t<p>Export declared plugin data or restore a compatible JSON backup. License secrets are never exported.</p>
\t\t\t\t\t</div>
\t\t\t\t</div>
\t\t\t\t<div class="nalapps-inline-actions">
\t\t\t\t\t<form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
\t\t\t\t\t\t<input type="hidden" name="action" value="{action}_export_data">
\t\t\t\t\t\t<?php wp_nonce_field( '{action}_export_data' ); ?>
\t\t\t\t\t\t<?php submit_button( 'Download data backup', 'primary', 'submit', false ); ?>
\t\t\t\t\t</form>
\t\t\t\t\t<form method="post" enctype="multipart/form-data" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
\t\t\t\t\t\t<input type="hidden" name="action" value="{action}_import_data">
\t\t\t\t\t\t<?php wp_nonce_field( '{action}_import_data' ); ?>
\t\t\t\t\t\t<input type="file" name="nalapps_backup" accept="application/json,.json" required>
\t\t\t\t\t\t<?php submit_button( 'Restore backup', 'secondary', 'submit', false ); ?>
\t\t\t\t\t</form>
\t\t\t\t</div>
\t\t\t\t<p class="description">A local data snapshot is created before restore. Snapshots: <?php echo esc_html( (string) count( $snapshots ) ); ?></p>
\t\t\t</div>

\t\t\t<div class="nalapps-panel">
\t\t\t\t<div class="nalapps-panel-heading">
\t\t\t\t\t<div>
\t\t\t\t\t\t<h2>Version rollback</h2>
\t\t\t\t\t\t<p>Select a previous verified GitHub Release Asset. Source Code archives are never accepted. Current code and data are backed up before rollback.</p>
\t\t\t\t\t</div>
\t\t\t\t</div>
\t\t\t\t<?php if ( $release_versions ) : ?>
\t\t\t\t\t<form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>" class="nalapps-inline-actions">
\t\t\t\t\t\t<input type="hidden" name="action" value="{action}_release_rollback">
\t\t\t\t\t\t<?php wp_nonce_field( '{action}_release_rollback' ); ?>
\t\t\t\t\t\t<label>
\t\t\t\t\t\t\t<strong>Rollback version</strong>
\t\t\t\t\t\t\t<select name="version" required>
\t\t\t\t\t\t\t\t<option value="">Select version</option>
\t\t\t\t\t\t\t\t<?php foreach ( array_keys( $release_versions ) as $version ) : ?>
\t\t\t\t\t\t\t\t\t<option value="<?php echo esc_attr( $version ); ?>"><?php echo esc_html( $version ); ?></option>
\t\t\t\t\t\t\t\t<?php endforeach; ?>
\t\t\t\t\t\t\t</select>
\t\t\t\t\t\t</label>
\t\t\t\t\t\t<?php submit_button( 'Rollback to selected version', 'secondary', 'submit', false ); ?>
\t\t\t\t\t</form>
\t\t\t\t<?php else : ?>
\t\t\t\t\t<div class="nalapps-notice">No verified previous Release Asset is currently available.</div>
\t\t\t\t<?php endif; ?>
\t\t\t</div>

\t\t\t<div class="nalapps-panel">
\t\t\t\t<div class="nalapps-panel-heading">
\t\t\t\t\t<div>
\t\t\t\t\t\t<h2>Local safety backups</h2>
\t\t\t\t\t\t<p>Emergency code backups created automatically before update or rollback.</p>
\t\t\t\t\t</div>
\t\t\t\t</div>
\t\t\t\t<div class="nalapps-stack">
\t\t\t\t\t<?php if ( empty( $backups ) ) : ?>
\t\t\t\t\t\t<div class="nalapps-notice">No local code backup exists yet.</div>
\t\t\t\t\t<?php endif; ?>
\t\t\t\t\t<?php foreach ( $backups as $backup ) : ?>
\t\t\t\t\t\t<form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>" class="nalapps-inline-actions">
\t\t\t\t\t\t\t<input type="hidden" name="action" value="{action}_rollback">
\t\t\t\t\t\t\t<input type="hidden" name="backup" value="<?php echo esc_attr( $backup ); ?>">
\t\t\t\t\t\t\t<?php wp_nonce_field( '{action}_rollback' ); ?>
\t\t\t\t\t\t\t<code><?php echo esc_html( $backup ); ?></code>
\t\t\t\t\t\t\t<?php submit_button( 'Restore local backup', 'secondary', 'submit', false ); ?>
\t\t\t\t\t\t</form>
\t\t\t\t\t<?php endforeach; ?>
\t\t\t\t</div>
\t\t\t</div>

\t\t\t<div class="nalapps-panel nalapps-danger-zone">
\t\t\t\t<div class="nalapps-panel-heading">
\t\t\t\t\t<div>
\t\t\t\t\t\t<h2>Uninstall data policy</h2>
\t\t\t\t\t\t<p>Preserve is the default. Complete deletion is explicit and irreversible.</p>
\t\t\t\t\t</div>
\t\t\t\t</div>
\t\t\t\t<form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
\t\t\t\t\t<input type="hidden" name="action" value="{action}_save_uninstall_policy">
\t\t\t\t\t<?php wp_nonce_field( '{action}_save_uninstall_policy' ); ?>
\t\t\t\t\t<div class="nalapps-toggle-row">
\t\t\t\t\t\t<div class="nalapps-toggle-copy">
\t\t\t\t\t\t\t<strong>Delete all plugin data on uninstall</strong>
\t\t\t\t\t\t\t<span>Only plugin-owned data may be deleted.</span>
\t\t\t\t\t\t</div>
\t\t\t\t\t\t<label class="nalapps-switch">
\t\t\t\t\t\t\t<input type="checkbox" name="delete_all" value="1" <?php checked( $delete ); ?>>
\t\t\t\t\t\t\t<span class="nalapps-switch__track"></span>
\t\t\t\t\t\t</label>
\t\t\t\t\t</div>
\t\t\t\t\t<?php submit_button( 'Save uninstall policy', 'secondary' ); ?>
\t\t\t\t</form>
\t\t\t</div>

\t\t\t<div class="nalapps-panel">
\t\t\t\t<div class="nalapps-panel-heading">
\t\t\t\t\t<div>
\t\t\t\t\t\t<h2>System information</h2>
\t\t\t\t\t\t<p>Redacted diagnostic values only.</p>
\t\t\t\t\t</div>
\t\t\t\t</div>
\t\t\t\t<table class="widefat striped">
\t\t\t\t\t<tbody>
\t\t\t\t\t\t<?php foreach ( System_Info::values() as $label => $value ) : ?>
\t\t\t\t\t\t\t<tr><th><?php echo esc_html( $label ); ?></th><td><?php echo esc_html( (string) $value ); ?></td></tr>
\t\t\t\t\t\t<?php endforeach; ?>
\t\t\t\t\t</tbody>
\t\t\t\t</table>
\t\t\t</div>
\t\t</div>
\t\t<?php
\t}}

\tpublic function save_uninstall_policy() {{
\t\tif ( ! current_user_can( 'manage_options' ) ) {{
\t\t\twp_die( esc_html( 'Insufficient permissions.' ) );
\t\t}}
\t\tcheck_admin_referer( '{action}_save_uninstall_policy' );
\t\t$policy = isset( $_POST['delete_all'] ) && '1' === sanitize_text_field( wp_unslash( $_POST['delete_all'] ) ) ? 'delete_all' : 'preserve';
\t\tupdate_option( self::POLICY_OPTION, $policy, false );
\t\twp_safe_redirect( admin_url( 'options-general.php?page={slug}-maintenance&state=policy_saved' ) );
\t\texit;
\t}}
}}
'''
