#!/usr/bin/env python3
"""Generate NalApps data portability and snapshot runtime."""
from __future__ import annotations

from scaffold_plugin import namespace_suffix, php_const_prefix


def php_array(values: list[str]) -> str:
    if not values:
        return "array()"
    rendered = ", ".join("'%s'" % value.replace("'", "\\'") for value in values)
    return f"array( {rendered} )"


def data_portability_class(profile: dict) -> str:
    ns = namespace_suffix(profile["slug"])
    slug = profile["slug"]
    action = slug.replace("-", "_")
    prefix = php_const_prefix(slug)
    contract = profile.get("data_contract") or {}
    options = php_array(contract.get("options", []))
    site_options = php_array(contract.get("site_options", []))
    post_types = php_array(contract.get("post_types", []))
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
\t\t$token   = substr( hash_hmac( 'sha256', '{slug}|' . home_url(), wp_salt( 'auth' ) ), 0, 32 );
\t\treturn trailingslashit( $uploads['basedir'] ) . '.nalapps-backups-' . $token . '/{slug}/data';
\t}}

\tpublic static function build_payload() {{
\t\t$data = array(
\t\t\t'format'           => self::FORMAT,
\t\t\t'plugin_slug'      => '{slug}',
\t\t\t'plugin_version'   => {prefix}_VERSION,
\t\t\t'standard_version' => {prefix}_STANDARD_VERSION,
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
\t\t$dir    = self::snapshot_directory();
\t\t$result = self::ensure_private_directory( $dir );
\t\tif ( is_wp_error( $result ) ) {{
\t\t\treturn $result;
\t\t}}
\t\tglobal $wp_filesystem;
\t\t$filename = sanitize_file_name( gmdate( 'Ymd-His' ) . '-' . sanitize_key( $reason ) . '.json' );
\t\t$written  = $wp_filesystem->put_contents(
\t\t\ttrailingslashit( $dir ) . $filename,
\t\t\twp_json_encode( self::build_payload(), JSON_PRETTY_PRINT )
\t\t);
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
\t\tnocache_headers();
\t\theader( 'Content-Type: application/json; charset=utf-8' );
\t\theader( 'Content-Disposition: attachment; filename="{slug}-backup-' . gmdate( 'Ymd-His' ) . '.json"' );
\t\techo wp_json_encode( self::build_payload(), JSON_PRETTY_PRINT );
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
\t\t\t$post_id  = isset( $record['ID'] ) ? absint( $record['ID'] ) : 0;
\t\t\t$post_type = sanitize_key( $record['post_type'] );
\t\t\t$args     = array(
\t\t\t\t'post_type'    => $post_type,
\t\t\t\t'post_status'  => isset( $record['post_status'] ) ? sanitize_key( $record['post_status'] ) : 'draft',
\t\t\t\t'post_title'   => isset( $record['post_title'] ) ? sanitize_text_field( $record['post_title'] ) : '',
\t\t\t\t'post_content' => isset( $record['post_content'] ) ? wp_kses_post( $record['post_content'] ) : '',
\t\t\t\t'post_excerpt' => isset( $record['post_excerpt'] ) ? wp_kses_post( $record['post_excerpt'] ) : '',
\t\t\t\t'post_name'    => isset( $record['post_name'] ) ? sanitize_title( $record['post_name'] ) : '',
\t\t\t\t'menu_order'   => isset( $record['menu_order'] ) ? (int) $record['menu_order'] : 0,
\t\t\t);
\t\t\t$existing = $post_id ? get_post( $post_id ) : null;
\t\t\tif ( $existing && $post_type === $existing->post_type ) {{
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
\t\t\t\t\t$meta_key = sanitize_key( $meta_key );
\t\t\t\t\tif ( in_array( $meta_key, array( '_edit_lock', '_edit_last' ), true ) ) {{
\t\t\t\t\t\tcontinue;
\t\t\t\t\t}}
\t\t\t\t\tdelete_post_meta( $saved, $meta_key );
\t\t\t\t\tforeach ( (array) $values as $value ) {{
\t\t\t\t\t\tadd_post_meta( $saved, $meta_key, maybe_unserialize( $value ) );
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
