#!/usr/bin/env python3
"""Generate NalApps pre-update backup plus verified Release Asset rollback runtime."""
from __future__ import annotations

from scaffold_plugin import namespace_suffix, php_const_prefix


def rollback_manager_class(profile: dict) -> str:
    ns = namespace_suffix(profile["slug"])
    slug = profile["slug"]
    action = slug.replace("-", "_")
    prefix = php_const_prefix(slug)
    return f'''<?php
/**
 * Pre-update code backup and controlled rollback support.
 *
 * @package {ns}
 */

namespace EOINGTI\\Plugins\\{ns};

if ( ! defined( 'ABSPATH' ) ) {{
\texit;
}}

final class Rollback_Manager {{
\tconst MAX_BACKUPS             = 3;
\tconst RELEASES_API            = 'https://api.github.com/repos/Eoingtilab/{slug}/releases?per_page=30';
\tconst ACTIVATION_STATE_OPTION = '{action}_update_activation_state';

\tpublic function __construct() {{
\t\tadd_filter( 'upgrader_pre_install', array( $this, 'backup_before_update' ), 10, 2 );
\t\tadd_action( 'upgrader_process_complete', array( $this, 'restore_activation_after_update' ), 20, 2 );
\t\tadd_action( 'admin_post_{action}_rollback', array( $this, 'rollback' ) );
\t\tadd_action( 'admin_post_{action}_release_rollback', array( $this, 'rollback_release' ) );
\t}}

\tpublic static function backup_directory() {{
\t\t$uploads = wp_upload_dir();
\t\t$token   = substr( hash_hmac( 'sha256', '{slug}|' . home_url(), wp_salt( 'auth' ) ), 0, 32 );
\t\treturn trailingslashit( $uploads['basedir'] ) . '.nalapps-backups-' . $token . '/{slug}/code';
\t}}

\tpublic function backup_before_update( $response, $hook_extra ) {{
\t\tif ( is_wp_error( $response ) ) {{
\t\t\treturn $response;
\t\t}}
\t\t$plugin = isset( $hook_extra['plugin'] ) ? (string) $hook_extra['plugin'] : '';
\t\tif ( plugin_basename( {prefix}_FILE ) !== $plugin ) {{
\t\t\treturn $response;
\t\t}}
\t\trequire_once ABSPATH . 'wp-admin/includes/plugin.php';
\t\tupdate_option(
\t\t\tself::ACTIVATION_STATE_OPTION,
\t\t\tarray(
\t\t\t\t'plugin'  => $plugin,
\t\t\t\t'active'  => is_plugin_active( $plugin ),
\t\t\t\t'network' => is_multisite() && is_plugin_active_for_network( $plugin ),
\t\t\t),
\t\t\tfalse
\t\t);
\t\t$backup = self::create_code_backup( 'pre-update' );
\t\tif ( is_wp_error( $backup ) ) {{
\t\t\treturn $backup;
\t\t}}
\t\t$snapshot = Data_Portability::create_snapshot( 'pre-update' );
\t\tif ( is_wp_error( $snapshot ) ) {{
\t\t\treturn $snapshot;
\t\t}}
\t\treturn $response;
\t}}

\tpublic function restore_activation_after_update( $upgrader, $hook_extra ) {{
\t\tunset( $upgrader );
\t\tif ( empty( $hook_extra['type'] ) || 'plugin' !== $hook_extra['type'] || empty( $hook_extra['action'] ) || 'update' !== $hook_extra['action'] ) {{
\t\t\treturn;
\t\t}}
\t\t$plugin  = plugin_basename( {prefix}_FILE );
\t\t$plugins = array();
\t\tif ( ! empty( $hook_extra['plugins'] ) && is_array( $hook_extra['plugins'] ) ) {{
\t\t\t$plugins = array_map( 'strval', $hook_extra['plugins'] );
\t\t}} elseif ( ! empty( $hook_extra['plugin'] ) ) {{
\t\t\t$plugins = array( (string) $hook_extra['plugin'] );
\t\t}}
\t\tif ( ! in_array( $plugin, $plugins, true ) ) {{
\t\t\treturn;
\t\t}}
\t\t$state = get_option( self::ACTIVATION_STATE_OPTION, array() );
\t\tdelete_option( self::ACTIVATION_STATE_OPTION );
\t\tif ( ! is_array( $state ) || empty( $state['active'] ) || empty( $state['plugin'] ) || $plugin !== $state['plugin'] ) {{
\t\t\treturn;
\t\t}}
\t\trequire_once ABSPATH . 'wp-admin/includes/plugin.php';
\t\tif ( ! is_plugin_active( $plugin ) ) {{
\t\t\tactivate_plugin( $plugin, '', ! empty( $state['network'] ), true );
\t\t}}
\t}}

\tpublic static function create_code_backup( $reason = 'manual' ) {{
\t\t$dir = self::backup_directory();
\t\tif ( ! wp_mkdir_p( $dir ) ) {{
\t\t\treturn new \\WP_Error( 'nalapps_rollback_dir', 'Could not create the rollback directory.' );
\t\t}}
\t\trequire_once ABSPATH . 'wp-admin/includes/class-pclzip.php';
\t\t$filename = sanitize_file_name( gmdate( 'Ymd-His' ) . '-' . {prefix}_VERSION . '-' . sanitize_key( $reason ) . '.zip' );
\t\t$path     = trailingslashit( $dir ) . $filename;
\t\t$archive  = new \\PclZip( $path );
\t\t$source   = untrailingslashit( {prefix}_PATH );
\t\t$created  = $archive->create( $source, PCLZIP_OPT_REMOVE_PATH, dirname( $source ) );
\t\tif ( 0 === $created ) {{
\t\t\treturn new \\WP_Error( 'nalapps_rollback_zip', 'Could not create the rollback package.' );
\t\t}}
\t\tself::protect_directory();
\t\tself::prune_backups();
\t\treturn $filename;
\t}}

\tpublic static function list_backups() {{
\t\t$dir = self::backup_directory();
\t\tif ( ! is_dir( $dir ) ) {{
\t\t\treturn array();
\t\t}}
\t\t$files = glob( trailingslashit( $dir ) . '*.zip' );
\t\tif ( ! is_array( $files ) ) {{
\t\t\treturn array();
\t\t}}
\t\t$names = array_map( 'basename', $files );
\t\trsort( $names, SORT_STRING );
\t\treturn $names;
\t}}

\tpublic static function list_release_versions() {{
\t\t$cache_key = '{action}_release_rollback_versions';
\t\t$cached    = get_transient( $cache_key );
\t\tif ( is_array( $cached ) ) {{
\t\t\treturn $cached;
\t\t}}
\t\t$response = wp_remote_get(
\t\t\tself::RELEASES_API,
\t\t\tarray(
\t\t\t\t'timeout' => 10,
\t\t\t\t'headers' => array( 'Accept' => 'application/vnd.github+json' ),
\t\t\t)
\t\t);
\t\tif ( is_wp_error( $response ) || 200 !== wp_remote_retrieve_response_code( $response ) ) {{
\t\t\treturn array();
\t\t}}
\t\t$releases = json_decode( wp_remote_retrieve_body( $response ), true );
\t\tif ( ! is_array( $releases ) ) {{
\t\t\treturn array();
\t\t}}
\t\t$versions = array();
\t\tforeach ( $releases as $release ) {{
\t\t\tif ( ! empty( $release['draft'] ) || ! empty( $release['prerelease'] ) || empty( $release['tag_name'] ) || empty( $release['assets'] ) || ! is_array( $release['assets'] ) ) {{
\t\t\t\tcontinue;
\t\t\t}}
\t\t\t$version = ltrim( sanitize_text_field( (string) $release['tag_name'] ), 'vV' );
\t\t\tif ( ! preg_match( '/^\\d+\\.\\d+\\.\\d+$/', $version ) || ! version_compare( $version, {prefix}_VERSION, '<' ) ) {{
\t\t\t\tcontinue;
\t\t\t}}
\t\t\t$expected = '{slug}-' . $version . '.zip';
\t\t\tforeach ( $release['assets'] as $asset ) {{
\t\t\t\tif ( isset( $asset['name'], $asset['browser_download_url'] ) && $expected === $asset['name'] ) {{
\t\t\t\t\t$versions[ $version ] = esc_url_raw( (string) $asset['browser_download_url'] );
\t\t\t\t\tbreak;
\t\t\t\t}}
\t\t\t}}
\t\t}}
\t\tuksort(
\t\t\t$versions,
\t\t\tstatic function ( $a, $b ) {{
\t\t\t\treturn version_compare( $b, $a );
\t\t\t}}
\t\t);
\t\tset_transient( $cache_key, $versions, HOUR_IN_SECONDS );
\t\treturn $versions;
\t}}

\tpublic function rollback() {{
\t\tif ( ! current_user_can( 'update_plugins' ) ) {{
\t\t\twp_die( esc_html( 'Insufficient permissions.' ) );
\t\t}}
\t\tcheck_admin_referer( '{action}_rollback' );
\t\t$requested = isset( $_POST['backup'] ) ? sanitize_file_name( wp_unslash( $_POST['backup'] ) ) : '';
\t\tif ( ! in_array( $requested, self::list_backups(), true ) ) {{
\t\t\t$this->redirect( 'rollback_error' );
\t\t}}
\t\t$this->perform_rollback( trailingslashit( self::backup_directory() ) . $requested );
\t}}

\tpublic function rollback_release() {{
\t\tif ( ! current_user_can( 'update_plugins' ) ) {{
\t\t\twp_die( esc_html( 'Insufficient permissions.' ) );
\t\t}}
\t\tcheck_admin_referer( '{action}_release_rollback' );
\t\t$requested = isset( $_POST['version'] ) ? sanitize_text_field( wp_unslash( $_POST['version'] ) ) : '';
\t\t$versions  = self::list_release_versions();
\t\tif ( ! isset( $versions[ $requested ] ) || ! version_compare( $requested, {prefix}_VERSION, '<' ) ) {{
\t\t\t$this->redirect( 'rollback_error' );
\t\t}}
\t\t$this->perform_rollback( $versions[ $requested ] );
\t}}

\tprivate function perform_rollback( $package ) {{
\t\t$current_backup = self::create_code_backup( 'pre-rollback' );
\t\t$data_snapshot  = Data_Portability::create_snapshot( 'pre-rollback' );
\t\tif ( is_wp_error( $current_backup ) || is_wp_error( $data_snapshot ) ) {{
\t\t\t$this->redirect( 'rollback_error' );
\t\t}}
\t\trequire_once ABSPATH . 'wp-admin/includes/plugin.php';
\t\t$plugin     = plugin_basename( {prefix}_FILE );
\t\t$was_active = is_plugin_active( $plugin );
\t\trequire_once ABSPATH . 'wp-admin/includes/file.php';
\t\trequire_once ABSPATH . 'wp-admin/includes/class-wp-upgrader.php';
\t\t$upgrader = new \\Plugin_Upgrader( new \\Automatic_Upgrader_Skin() );
\t\t$result   = $upgrader->install( $package, array( 'overwrite_package' => true ) );
\t\tdelete_site_transient( 'update_plugins' );
\t\tdelete_transient( '{action}_release_rollback_versions' );
\t\tif ( is_wp_error( $result ) || false === $result ) {{
\t\t\t$this->redirect( 'rollback_error' );
\t\t}}
\t\tif ( $was_active && ! is_plugin_active( $plugin ) ) {{
\t\t\tactivate_plugin( $plugin, '', false, true );
\t\t}}
\t\t$this->redirect( 'rolled_back' );
\t}}

\tprivate static function protect_directory() {{
\t\trequire_once ABSPATH . 'wp-admin/includes/file.php';
\t\tglobal $wp_filesystem;
\t\tif ( WP_Filesystem() ) {{
\t\t\t$dir = self::backup_directory();
\t\t\t$wp_filesystem->put_contents( trailingslashit( $dir ) . 'index.php', "<?php\\n// Silence is golden.\\n" );
\t\t\t$wp_filesystem->put_contents( trailingslashit( $dir ) . '.htaccess', "Deny from all\\n" );
\t\t}}
\t}}

\tprivate static function prune_backups() {{
\t\t$files = self::list_backups();
\t\tforeach ( array_slice( $files, self::MAX_BACKUPS ) as $name ) {{
\t\t\twp_delete_file( trailingslashit( self::backup_directory() ) . $name );
\t\t}}
\t}}

\tprivate function redirect( $state ) {{
\t\twp_safe_redirect( admin_url( 'options-general.php?page={slug}-maintenance&state=' . sanitize_key( $state ) ) );
\t\texit;
\t}}
}}
'''
