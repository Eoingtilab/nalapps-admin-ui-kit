#!/usr/bin/env python3
"""Add the common NalApps rollback, backup, portability and uninstall runtime."""
from __future__ import annotations

import json
from pathlib import Path

from scaffold_plugin import namespace_suffix, php_const_prefix, write_file


def _php_array(values: list[str]) -> str:
    if not values:
        return "array()"
    rendered = ", ".join("'%s'" % value.replace("'", "\\'") for value in values)
    return f"array( {rendered} )"


def data_portability_class(profile: dict) -> str:
    ns = namespace_suffix(profile["slug"])
    slug = profile["slug"]
    action = slug.replace("-", "_")
    contract = profile.get("data_contract") or {}
    options = _php_array(contract.get("options", []))
    site_options = _php_array(contract.get("site_options", []))
    post_types = _php_array(contract.get("post_types", []))
    return f'''<?php
/**
 * Data export, import and local snapshot support.
 *
 * @package {ns}
 */

namespace EOINGTI\\Plugins\\{ns};

if ( ! defined( 'ABSPATH' ) ) {{
\texit;
}}

final class Data_Portability {{
\tconst FORMAT        = 'nalapps-data-backup-v1';
\tconst MAX_FILE_SIZE = 5242880;
\tconst MAX_SNAPSHOTS = 5;

\tpublic function __construct() {{
\t\tadd_action( 'admin_post_{action}_export_data', array( $this, 'export_data' ) );
\t\tadd_action( 'admin_post_{action}_import_data', array( $this, 'import_data' ) );
\t}}

\tpublic static function option_names() {{
\t\treturn {options};
\t}}

\tpublic static function site_option_names() {{
\t\treturn {site_options};
\t}}

\tpublic static function post_types() {{
\t\treturn {post_types};
\t}}

\tpublic static function snapshot_directory() {{
\t\t$uploads = wp_upload_dir();
\t\t$key     = wp_salt( 'auth' );
\t\t$token   = substr( hash_hmac( 'sha256', '{slug}|' . home_url(), $key ), 0, 32 );
\t\treturn trailingslashit( $uploads['basedir'] ) . '.nalapps-backups-' . $token . '/{slug}/data';
\t}}

\tpublic static function build_payload() {{
\t\t$data = array(
\t\t\t'format'           => self::FORMAT,
\t\t\t'plugin_slug'      => '{slug}',
\t\t\t'plugin_version'   => {php_const_prefix(slug)}_VERSION,
\t\t\t'standard_version' => {php_const_prefix(slug)}_STANDARD_VERSION,
\t\t\t'created_at'       => gmdate( 'c' ),
\t\t\t'data'             => array(
\t\t\t\t'options'      => array(),
\t\t\t\t'site_options' => array(),
\t\t\t\t'posts'        => array(),
\t\t\t),
\t\t);

\t\tforeach ( self::option_names() as $name ) {{
\t\t\t$data['data']['options'][ $name ] = get_option( $name );
\t\t}}
\t\tforeach ( self::site_option_names() as $name ) {{
\t\t\t$data['data']['site_options'][ $name ] = get_site_option( $name );
\t\t}}
\t\tforeach ( self::post_types() as $post_type ) {{
\t\t\t$posts = get_posts(
\t\t\t\tarray(
\t\t\t\t\t'post_type'      => $post_type,
\t\t\t\t\t'post_status'    => 'any',
\t\t\t\t\t'posts_per_page' => -1,
\t\t\t\t\t'orderby'        => 'ID',
\t\t\t\t\t'order'          => 'ASC',
\t\t\t\t)
\t\t\t);
\t\t\tforeach ( $posts as $post ) {{
\t\t\t\t$meta = get_post_meta( $post->ID );
\t\t\t\tunset( $meta['_edit_lock'], $meta['_edit_last'] );
\t\t\t\t$data['data']['posts'][] = array(
\t\t\t\t\t'ID'           => (int) $post->ID,
\t\t\t\t\t'post_type'    => $post->post_type,
\t\t\t\t\t'post_status'  => $post->post_status,
\t\t\t\t\t'post_title'   => $post->post_title,
\t\t\t\t\t'post_content' => $post->post_content,
\t\t\t\t\t'post_excerpt' => $post->post_excerpt,
\t\t\t\t\t'post_name'    => $post->post_name,
\t\t\t\t\t'menu_order'   => (int) $post->menu_order,
\t\t\t\t\t'meta'         => $meta,
\t\t\t\t);
\t\t\t}}
\t\t}}

\t\treturn apply_filters( '{action}_export_payload', $data );
\t}}

\tpublic static function create_snapshot( $reason = 'manual' ) {{
\t\t$payload = self::build_payload();
\t\t$dir     = self::snapshot_directory();
\t\t$result  = self::ensure_private_directory( $dir );
\t\tif ( is_wp_error( $result ) ) {{
\t\t\treturn $result;
\t\t}}
\t\tglobal $wp_filesystem;
\t\t$filename = sanitize_file_name( gmdate( 'Ymd-His' ) . '-' . sanitize_key( $reason ) . '.json' );
\t\t$written  = $wp_filesystem->put_contents( trailingslashit( $dir ) . $filename, wp_json_encode( $payload, JSON_PRETTY_PRINT ) );
\t\tif ( ! $written ) {{
\t\t\treturn new \\WP_Error( 'nalapps_snapshot_write', 'Could not write the data snapshot.' );
\t\t}}
\t\tself::prune_snapshots();
\t\treturn $filename;
\t}}

\tpublic static function list_snapshots() {{
\t\t$result = self::ensure_private_directory( self::snapshot_directory() );
\t\tif ( is_wp_error( $result ) ) {{
\t\t\treturn array();
\t\t}}
\t\tglobal $wp_filesystem;
\t\t$items = $wp_filesystem->dirlist( self::snapshot_directory() );
\t\t$files = array();
\t\tif ( is_array( $items ) ) {{
\t\t\tforeach ( $items as $name => $info ) {{
\t\t\t\tif ( 'f' === $info['type'] && preg_match( '/\\.json$/', $name ) ) {{
\t\t\t\t\t$files[] = sanitize_file_name( $name );
\t\t\t\t}}
\t\t\t}}
\t\t}}
\t\trsort( $files, SORT_STRING );
\t\treturn $files;
\t}}

\tpublic function export_data() {{
\t\tif ( ! current_user_can( 'manage_options' ) ) {{
\t\t\twp_die( esc_html( 'Insufficient permissions.' ) );
\t\t}}
\t\tcheck_admin_referer( '{action}_export_data' );
\t\t$payload = self::build_payload();
\t\tnocache_headers();
\t\theader( 'Content-Type: application/json; charset=utf-8' );
\t\theader( 'Content-Disposition: attachment; filename="{slug}-backup-' . gmdate( 'Ymd-His' ) . '.json"' );
\t\techo wp_json_encode( $payload, JSON_PRETTY_PRINT );
\t\texit;
\t}}

\tpublic function import_data() {{
\t\tif ( ! current_user_can( 'manage_options' ) ) {{
\t\t\twp_die( esc_html( 'Insufficient permissions.' ) );
\t\t}}
\t\tcheck_admin_referer( '{action}_import_data' );
\t\tif ( empty( $_FILES['nalapps_backup']['tmp_name'] ) || ! isset( $_FILES['nalapps_backup']['size'], $_FILES['nalapps_backup']['name'] ) ) {{
\t\t\t$this->redirect( 'import_error' );
\t\t}}

\t\t$tmp_name = (string) $_FILES['nalapps_backup']['tmp_name']; // phpcs:ignore WordPress.Security.ValidatedSanitizedInput.InputNotSanitized
\t\t$size     = (int) $_FILES['nalapps_backup']['size'];
\t\t$name     = sanitize_file_name( wp_unslash( (string) $_FILES['nalapps_backup']['name'] ) );
\t\tif ( $size <= 0 || $size > self::MAX_FILE_SIZE || 'json' !== strtolower( pathinfo( $name, PATHINFO_EXTENSION ) ) || ! is_uploaded_file( $tmp_name ) ) {{
\t\t\t$this->redirect( 'import_error' );
\t\t}}

\t\t$raw = file_get_contents( $tmp_name ); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
\t\tif ( false === $raw ) {{
\t\t\t$this->redirect( 'import_error' );
\t\t}}
\t\t$payload = json_decode( $raw, true );
\t\tif ( ! self::valid_payload( $payload ) ) {{
\t\t\t$this->redirect( 'import_error' );
\t\t}}

\t\t$snapshot = self::create_snapshot( 'pre-import' );
\t\tif ( is_wp_error( $snapshot ) ) {{
\t\t\t$this->redirect( 'snapshot_error' );
\t\t}}
\t\t$this->restore_payload( $payload );
\t\tdo_action( '{action}_import_complete', $payload );
\t\t$this->redirect( 'imported' );
\t}}

\tprivate static function valid_payload( $payload ) {{
\t\treturn is_array( $payload )
\t\t\t&& isset( $payload['format'], $payload['plugin_slug'], $payload['data'] )
\t\t\t&& self::FORMAT === $payload['format']
\t\t\t&& '{slug}' === $payload['plugin_slug']
\t\t\t&& is_array( $payload['data'] );
\t}}

\tprivate function restore_payload( $payload ) {{
\t\t$options = isset( $payload['data']['options'] ) && is_array( $payload['data']['options'] ) ? $payload['data']['options'] : array();
\t\tforeach ( self::option_names() as $name ) {{
\t\t\tif ( array_key_exists( $name, $options ) ) {{
\t\t\t\tupdate_option( $name, $options[ $name ], false );
\t\t\t}}
\t\t}}
\t\t$site_options = isset( $payload['data']['site_options'] ) && is_array( $payload['data']['site_options'] ) ? $payload['data']['site_options'] : array();
\t\tforeach ( self::site_option_names() as $name ) {{
\t\t\tif ( array_key_exists( $name, $site_options ) ) {{
\t\t\t\tupdate_site_option( $name, $site_options[ $name ] );
\t\t\t}}
\t\t}}

\t\t$posts = isset( $payload['data']['posts'] ) && is_array( $payload['data']['posts'] ) ? $payload['data']['posts'] : array();
\t\tforeach ( $posts as $record ) {{
\t\t\tif ( ! is_array( $record ) || empty( $record['post_type'] ) || ! in_array( $record['post_type'], self::post_types(), true ) ) {{
\t\t\t\tcontinue;
\t\t\t}}
\t\t\t$post_id = isset( $record['ID'] ) ? absint( $record['ID'] ) : 0;
\t\t\t$args    = array(
\t\t\t\t'post_type'    => sanitize_key( $record['post_type'] ),
\t\t\t\t'post_status'  => isset( $record['post_status'] ) ? sanitize_key( $record['post_status'] ) : 'draft',
\t\t\t\t'post_title'   => isset( $record['post_title'] ) ? sanitize_text_field( $record['post_title'] ) : '',
\t\t\t\t'post_content' => isset( $record['post_content'] ) ? wp_kses_post( $record['post_content'] ) : '',
\t\t\t\t'post_excerpt' => isset( $record['post_excerpt'] ) ? wp_kses_post( $record['post_excerpt'] ) : '',
\t\t\t\t'post_name'    => isset( $record['post_name'] ) ? sanitize_title( $record['post_name'] ) : '',
\t\t\t\t'menu_order'   => isset( $record['menu_order'] ) ? (int) $record['menu_order'] : 0,
\t\t\t);
\t\t\t$existing = $post_id ? get_post( $post_id ) : null;
\t\t\tif ( $existing && $record['post_type'] === $existing->post_type ) {{
\t\t\t\t$args['ID'] = $post_id;
\t\t\t\t$saved      = wp_update_post( $args, true );
\t\t\t}} else {{
\t\t\t\tif ( $post_id ) {{
\t\t\t\t\t$args['import_id'] = $post_id;
\t\t\t\t}}
\t\t\t\t$saved = wp_insert_post( $args, true );
\t\t\t}}
\t\t\tif ( is_wp_error( $saved ) || ! $saved ) {{
\t\t\t\tcontinue;
\t\t\t}}
\t\t\tif ( isset( $record['meta'] ) && is_array( $record['meta'] ) ) {{
\t\t\t\tforeach ( $record['meta'] as $meta_key => $values ) {{
\t\t\t\t\tif ( in_array( $meta_key, array( '_edit_lock', '_edit_last' ), true ) ) {{
\t\t\t\t\t\tcontinue;
\t\t\t\t\t}}
\t\t\t\t\tdelete_post_meta( $saved, sanitize_key( $meta_key ) );
\t\t\t\t\tforeach ( (array) $values as $value ) {{
\t\t\t\t\t\tadd_post_meta( $saved, sanitize_key( $meta_key ), maybe_unserialize( $value ) );
\t\t\t\t\t}}
\t\t\t\t}}
\t\t\t}}
\t\t}}
\t}}

\tprivate static function ensure_private_directory( $dir ) {{
\t\trequire_once ABSPATH . 'wp-admin/includes/file.php';
\t\tglobal $wp_filesystem;
\t\tif ( ! WP_Filesystem() ) {{
\t\t\treturn new \\WP_Error( 'nalapps_filesystem', 'WordPress filesystem access is unavailable.' );
\t\t}}
\t\tif ( ! $wp_filesystem->is_dir( $dir ) && ! wp_mkdir_p( $dir ) ) {{
\t\t\treturn new \\WP_Error( 'nalapps_backup_dir', 'Could not create the backup directory.' );
\t\t}}
\t\t$wp_filesystem->put_contents( trailingslashit( $dir ) . 'index.php', "<?php\\n// Silence is golden.\\n" );
\t\t$wp_filesystem->put_contents( trailingslashit( $dir ) . '.htaccess', "Deny from all\\n" );
\t\t$wp_filesystem->put_contents( trailingslashit( $dir ) . 'web.config', '<configuration><system.webServer><security><requestFiltering><hiddenSegments><add segment="{slug}" /></hiddenSegments></requestFiltering></security></system.webServer></configuration>' );
\t\treturn true;
\t}}

\tprivate static function prune_snapshots() {{
\t\t$files = self::list_snapshots();
\t\tif ( count( $files ) <= self::MAX_SNAPSHOTS ) {{
\t\t\treturn;
\t\t}}
\t\tglobal $wp_filesystem;
\t\tforeach ( array_slice( $files, self::MAX_SNAPSHOTS ) as $name ) {{
\t\t\t$wp_filesystem->delete( trailingslashit( self::snapshot_directory() ) . $name );
\t\t}}
\t}}

\tprivate function redirect( $state ) {{
\t\twp_safe_redirect( admin_url( 'options-general.php?page={slug}-maintenance&state=' . sanitize_key( $state ) ) );
\t\texit;
\t}}
}}
'''


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
\tconst MAX_BACKUPS = 3;

\tpublic function __construct() {{
\t\tadd_filter( 'upgrader_pre_install', array( $this, 'backup_before_update' ), 10, 2 );
\t\tadd_action( 'admin_post_{action}_rollback', array( $this, 'rollback' ) );
\t}}

\tpublic static function backup_directory() {{
\t\t$uploads = wp_upload_dir();
\t\t$key     = wp_salt( 'auth' );
\t\t$token   = substr( hash_hmac( 'sha256', '{slug}|' . home_url(), $key ), 0, 32 );
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
\t\treturn array_values( array_filter( $names, 'sanitize_file_name' ) );
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
\t\t$current_backup = self::create_code_backup( 'pre-rollback' );
\t\t$data_snapshot  = Data_Portability::create_snapshot( 'pre-rollback' );
\t\tif ( is_wp_error( $current_backup ) || is_wp_error( $data_snapshot ) ) {{
\t\t\t$this->redirect( 'rollback_error' );
\t\t}}

\t\trequire_once ABSPATH . 'wp-admin/includes/file.php';
\t\trequire_once ABSPATH . 'wp-admin/includes/class-wp-upgrader.php';
\t\t$package  = trailingslashit( self::backup_directory() ) . $requested;
\t\t$upgrader = new \\Plugin_Upgrader( new \\Automatic_Upgrader_Skin() );
\t\t$result   = $upgrader->install( $package, array( 'overwrite_package' => true ) );
\t\tdelete_site_transient( 'update_plugins' );
\t\tif ( is_wp_error( $result ) || false === $result ) {{
\t\t\t$this->redirect( 'rollback_error' );
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


def system_info_class(profile: dict) -> str:
    ns = namespace_suffix(profile["slug"])
    slug = profile["slug"]
    prefix = php_const_prefix(slug)
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
\t\t\t'Plugin version'     => {prefix}_VERSION,
\t\t\t'Standard version'   => {prefix}_STANDARD_VERSION,
\t\t\t'WordPress version'  => get_bloginfo( 'version' ),
\t\t\t'PHP version'        => PHP_VERSION,
\t\t\t'Locale'             => get_locale(),
\t\t\t'Multisite'          => is_multisite() ? 'yes' : 'no',
\t\t\t'HTTPS'              => is_ssl() ? 'yes' : 'no',
\t\t\t'Memory limit'       => ini_get( 'memory_limit' ),
\t\t\t'Upload max size'    => ini_get( 'upload_max_filesize' ),
\t\t\t'WP_DEBUG'           => defined( 'WP_DEBUG' ) && WP_DEBUG ? 'on' : 'off',
\t\t\t'DISABLE_WP_CRON'    => defined( 'DISABLE_WP_CRON' ) && DISABLE_WP_CRON ? 'on' : 'off',
\t\t\t'Active theme'       => $theme->get( 'Name' ) . ' ' . $theme->get( 'Version' ),
\t\t\t'Rollback backups'   => (string) count( Rollback_Manager::list_backups() ),
\t\t\t'Data snapshots'     => (string) count( Data_Portability::list_snapshots() ),
\t\t\t'Portable options'   => (string) count( Data_Portability::option_names() ),
\t\t\t'Portable post types'=> (string) count( Data_Portability::post_types() ),
\t\t);
\t}}

\tpublic function site_health_info( $debug_info ) {{
\t\t$fields = array();
\t\tforeach ( self::values() as $label => $value ) {{
\t\t\t$key            = sanitize_key( $label );
\t\t\t$fields[ $key ] = array(
\t\t\t\t'label' => $label,
\t\t\t\t'value' => (string) $value,
\t\t\t);
\t\t}}
\t\t$debug_info['{action_key(slug)}'] = array(
\t\t\t'label'  => '{profile["plugin_name"]}',
\t\t\t'fields' => $fields,
\t\t);
\t\treturn $debug_info;
\t}}
}}
'''


def action_key(slug: str) -> str:
    return "nalapps_" + slug.replace("-", "_")


def maintenance_page_class(profile: dict) -> str:
    ns = namespace_suffix(profile["slug"])
    slug = profile["slug"]
    action = slug.replace("-", "_")
    policy_option = f"{action}_uninstall_policy"
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
\t\t$policy = get_option( self::POLICY_OPTION, '{profile.get("uninstall_policy", "preserve")}' );
\t\techo '<div class="wrap"><h1>' . esc_html( '{profile["plugin_name"]} Maintenance' ) . '</h1>';
\t\techo '<h2>System Information</h2><table class="widefat striped"><tbody>';
\t\tforeach ( System_Info::values() as $label => $value ) {{
\t\t\techo '<tr><th>' . esc_html( $label ) . '</th><td>' . esc_html( (string) $value ) . '</td></tr>';
\t\t}}
\t\techo '</tbody></table>';

\t\techo '<h2>Data Backup</h2><p>Export a portable JSON backup or import a backup created by this plugin. A local snapshot is created before every import.</p>';
\t\techo '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '"><input type="hidden" name="action" value="{action}_export_data">';
\t\twp_nonce_field( '{action}_export_data' );
\t\tsubmit_button( 'Export data', 'secondary', 'submit', false );
\t\techo '</form>';
\t\techo '<form method="post" enctype="multipart/form-data" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '"><input type="hidden" name="action" value="{action}_import_data">';
\t\twp_nonce_field( '{action}_import_data' );
\t\techo '<input type="file" name="nalapps_backup" accept="application/json,.json" required> ';
\t\tsubmit_button( 'Import data', 'secondary', 'submit', false );
\t\techo '</form>';

\t\techo '<h2>Rollback</h2><p>Code rollback restores a previous plugin package. Database migrations are not reversed automatically; use a data backup when data restoration is required.</p>';
\t\tforeach ( Rollback_Manager::list_backups() as $backup ) {{
\t\t\techo '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '" style="margin-bottom:8px"><input type="hidden" name="action" value="{action}_rollback"><input type="hidden" name="backup" value="' . esc_attr( $backup ) . '">';
\t\t\twp_nonce_field( '{action}_rollback' );
\t\t\techo '<code>' . esc_html( $backup ) . '</code> ';
\t\t\tsubmit_button( 'Rollback', 'secondary', 'submit', false );
\t\t\techo '</form>';
\t\t}}

\t\techo '<h2>Uninstall Data Policy</h2><p>Data is preserved by default. Select complete deletion only when you intentionally want this plugin to remove its declared data during uninstall.</p>';
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


def uninstall_php(profile: dict) -> str:
    slug = profile["slug"]
    action = slug.replace("-", "_")
    policy = f"{action}_uninstall_policy"
    contract = profile.get("data_contract") or {}
    options = list(contract.get("options", []))
    site_options = list(contract.get("site_options", []))
    post_types = list(contract.get("post_types", []))
    tables = list(contract.get("custom_tables", []))
    owned_options = options + [policy, f"{action}_update_last_checked"]
    if profile.get("product_type") == "edd_paid":
        owned_options += [f"{slug}_license_key", f"{slug}_license"]
    delete_option_lines = "\n".join(f"delete_option( '{name}' );" for name in owned_options)
    delete_site_lines = "\n".join(f"delete_site_option( '{name}' );" for name in site_options)
    post_types_php = _php_array(post_types)
    table_lines = "\n".join(
        f"$wpdb->query( 'DROP TABLE IF EXISTS ' . $wpdb->prefix . '{table}' ); // phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.SchemaChange"
        for table in tables
    )
    return f'''<?php
/**
 * NalApps uninstall policy handler.
 *
 * Data is preserved unless the site owner explicitly selected delete_all.
 */

if ( ! defined( 'WP_UNINSTALL_PLUGIN' ) ) {{
\texit;
}}

$nalapps_policy = get_option( '{policy}', 'preserve' );
if ( 'delete_all' !== $nalapps_policy ) {{
\treturn;
}}

{delete_option_lines}
{delete_site_lines}

$nalapps_post_types = {post_types_php};
foreach ( $nalapps_post_types as $nalapps_post_type ) {{
\t$nalapps_ids = get_posts(
\t\tarray(
\t\t\t'post_type'      => $nalapps_post_type,
\t\t\t'post_status'    => 'any',
\t\t\t'posts_per_page' => -1,
\t\t\t'fields'         => 'ids',
\t\t)
\t);
\tforeach ( $nalapps_ids as $nalapps_id ) {{
\t\twp_delete_post( $nalapps_id, true );
\t}}
}}

{('$wpdb = $GLOBALS[\'wpdb\'];' if tables else '')}
{table_lines}

do_action( '{action}_delete_all_data' );
'''


def augment_main(target: Path, profile: dict) -> None:
    slug = profile["slug"]
    prefix = php_const_prefix(slug)
    ns = namespace_suffix(slug)
    path = target / f"{slug}.php"
    text = path.read_text(encoding="utf-8")
    marker = "// NalApps common maintenance runtime."
    if marker in text:
        return
    block = f'''\n\n{marker}\nrequire_once {prefix}_PATH . 'includes/class-data-portability.php';\nrequire_once {prefix}_PATH . 'includes/class-rollback-manager.php';\nrequire_once {prefix}_PATH . 'includes/class-system-info.php';\nrequire_once {prefix}_PATH . 'includes/class-maintenance-page.php';\nnew \\EOINGTI\\Plugins\\{ns}\\Data_Portability();\nnew \\EOINGTI\\Plugins\\{ns}\\Rollback_Manager();\nnew \\EOINGTI\\Plugins\\{ns}\\System_Info();\nnew \\EOINGTI\\Plugins\\{ns}\\Maintenance_Page();\n'''
    path.write_text(text + block, encoding="utf-8")


def augment_manifest(target: Path) -> None:
    path = target / "nalapps-standard-manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for module in ("rollback", "data_portability", "safe_uninstall", "system_info"):
        if module not in data["required_modules"]:
            data["required_modules"].append(module)
    for gate in ("rollback_backup_contract", "data_backup_import_export", "uninstall_delete_gate", "system_info_redaction"):
        if gate not in data["release_gates"]:
            data["release_gates"].append(gate)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_maintenance_runtime(target: Path, profile: dict) -> Path:
    write_file(target, "includes/class-data-portability.php", data_portability_class(profile))
    write_file(target, "includes/class-rollback-manager.php", rollback_manager_class(profile))
    write_file(target, "includes/class-system-info.php", system_info_class(profile))
    write_file(target, "includes/class-maintenance-page.php", maintenance_page_class(profile))
    write_file(target, "uninstall.php", uninstall_php(profile))
    augment_main(target, profile)
    augment_manifest(target)
    return target
