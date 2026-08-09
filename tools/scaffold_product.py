#!/usr/bin/env python3
"""Canonical NalApps product scaffolder, including EDD paid runtime integration."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scaffold_complete import complete_scaffold
from scaffold_plugin import namespace_suffix, php_const_prefix, write_file
from validate_profile import validate_profile

EDD_SDK_REPOSITORY = "https://github.com/awesomemotive/edd-sl-sdk"
EDD_SDK_PACKAGE = "easy-digital-downloads/edd-sl-sdk"
EDD_SDK_VERSION = "^1.0.2"


def license_class(profile: dict) -> str:
    ns = namespace_suffix(profile["slug"])
    # The EDD SL SDK derives option names from the registered id verbatim.
    # Keep hyphens in the canonical slug so the generated adapter reads the
    # same options that the SDK writes.
    option_prefix = profile["slug"]
    return f'''<?php
/**
 * EDD Software Licensing state adapter.
 *
 * @package {ns}
 */

namespace EOINGTI\\Plugins\\{ns};

if ( ! defined( 'ABSPATH' ) ) {{
\texit;
}}

final class License {{
\tconst KEY_OPTION    = '{option_prefix}_license_key';
\tconst STATUS_OPTION = '{option_prefix}_license';

\tpublic static function key() {{
\t\treturn trim( (string) get_option( self::KEY_OPTION, '' ) );
\t}}

\tpublic static function status() {{
\t\t$data = get_option( self::STATUS_OPTION );
\t\tif ( is_object( $data ) && isset( $data->license ) ) {{
\t\t\treturn sanitize_key( (string) $data->license );
\t\t}}
\t\tif ( is_array( $data ) && isset( $data['license'] ) ) {{
\t\t\treturn sanitize_key( (string) $data['license'] );
\t\t}}
\t\treturn 'inactive';
\t}}

\tpublic static function is_valid() {{
\t\treturn in_array( self::status(), array( 'valid', 'active' ), true );
\t}}

\tprivate function __construct() {{
\t}}
}}
'''


def update_manager_class(profile: dict) -> str:
    ns = namespace_suffix(profile["slug"])
    slug = profile["slug"]
    prefix = php_const_prefix(slug)
    action_prefix = slug.replace("-", "_")
    page_slug = f"{slug}-updates"
    cache_key = f"{action_prefix}_edd_version_info"
    checked_option = f"{action_prefix}_update_last_checked"
    return f'''<?php
/**
 * EDD hybrid updater.
 *
 * @package {ns}
 */

namespace EOINGTI\\Plugins\\{ns};

if ( ! defined( 'ABSPATH' ) ) {{
\texit;
}}

final class Update_Manager {{
\tconst CACHE_KEY = '{cache_key}';
\tconst CACHE_TTL = 6 * HOUR_IN_SECONDS;

\tpublic function __construct() {{
\t\tadd_filter( 'pre_set_site_transient_update_plugins', array( $this, 'inject_update' ) );
\t\tadd_action( 'admin_menu', array( $this, 'register_page' ) );
\t\tadd_action( 'admin_post_{action_prefix}_check_updates', array( $this, 'manual_check' ) );
\t\tadd_action( 'admin_post_{action_prefix}_install_update', array( $this, 'install_update' ) );
\t}}

\tpublic function register_page() {{
\t\tadd_options_page(
\t\t\t'{profile["plugin_name"]} Updates',
\t\t\t'{profile["plugin_name"]} Updates',
\t\t\t'update_plugins',
\t\t\t'{page_slug}',
\t\t\tarray( $this, 'render_page' )
\t\t);
\t}}

\tpublic function inject_update( $transient ) {{
\t\tif ( ! is_object( $transient ) ) {{
\t\t\t$transient = new \\stdClass();
\t\t}}
\t\tif ( ! isset( $transient->response ) || ! is_array( $transient->response ) ) {{
\t\t\t$transient->response = array();
\t\t}}

\t\t$info = $this->remote_version( false );
\t\tif ( is_wp_error( $info ) || ! $this->has_update( $info ) ) {{
\t\t\treturn $transient;
\t\t}}

\t\t$plugin                         = plugin_basename( {prefix}_FILE );
\t\t$transient->response[ $plugin ] = $this->update_object( $info, $plugin );
\t\treturn $transient;
\t}}

\tpublic function render_page() {{
\t\tif ( ! current_user_can( 'update_plugins' ) ) {{
\t\t\twp_die( esc_html( 'Insufficient permissions.' ) );
\t\t}}

\t\t$info           = $this->remote_version( false );
\t\t$error          = is_wp_error( $info ) ? $info->get_error_message() : '';
\t\t$latest         = ( ! $error && ! empty( $info['new_version'] ) ) ? (string) $info['new_version'] : 'Unavailable';
\t\t$available      = ! $error && $this->has_update( $info );
\t\t$download_ready = $available && License::is_valid() && ! empty( $info['download_link'] );
\t\t$last_checked   = (string) get_option( '{checked_option}', '' );
\t\t$checked_label  = '' !== $last_checked ? $last_checked : '-';

\t\techo '<div class="wrap"><h1>' . esc_html( '{profile["plugin_name"]} Updates' ) . '</h1>';
\t\techo '<p>' . esc_html( 'Current: ' . {prefix}_VERSION . ' / Latest: ' . $latest ) . '</p>';
\t\techo '<p>' . esc_html( 'License: ' . License::status() . ' / Last checked: ' . $checked_label ) . '</p>';

\t\tif ( $error ) {{
\t\t\techo '<div class="notice notice-error inline"><p>' . esc_html( $error ) . '</p></div>';
\t\t}} elseif ( $available ) {{
\t\t\techo '<div class="notice notice-info inline"><p>' . esc_html( 'A new version is available.' ) . '</p></div>';
\t\t}} else {{
\t\t\techo '<div class="notice notice-success inline"><p>' . esc_html( 'The plugin is up to date.' ) . '</p></div>';
\t\t}}

\t\techo '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '">';
\t\techo '<input type="hidden" name="action" value="{action_prefix}_check_updates">';
\t\twp_nonce_field( '{action_prefix}_check_updates' );
\t\tsubmit_button( 'Check for updates', 'secondary', 'submit', false );
\t\techo '</form>';

\t\tif ( $download_ready ) {{
\t\t\techo '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '">';
\t\t\techo '<input type="hidden" name="action" value="{action_prefix}_install_update">';
\t\t\twp_nonce_field( '{action_prefix}_install_update' );
\t\t\tsubmit_button( 'Update now', 'primary', 'submit', false );
\t\t\techo '</form>';
\t\t}}
\t\techo '</div>';
\t}}

\tpublic function manual_check() {{
\t\tif ( ! current_user_can( 'update_plugins' ) ) {{
\t\t\twp_die( esc_html( 'Insufficient permissions.' ) );
\t\t}}
\t\tcheck_admin_referer( '{action_prefix}_check_updates' );
\t\tdelete_transient( self::CACHE_KEY );
\t\tdelete_site_transient( 'update_plugins' );
\t\t$this->remote_version( true );
\t\twp_update_plugins();
\t\twp_safe_redirect( admin_url( 'options-general.php?page={page_slug}&checked=1' ) );
\t\texit;
\t}}

\tpublic function install_update() {{
\t\tif ( ! current_user_can( 'update_plugins' ) ) {{
\t\t\twp_die( esc_html( 'Insufficient permissions.' ) );
\t\t}}
\t\tcheck_admin_referer( '{action_prefix}_install_update' );

\t\tif ( ! License::is_valid() ) {{
\t\t\twp_safe_redirect( admin_url( 'options-general.php?page={page_slug}&license_required=1' ) );
\t\t\texit;
\t\t}}

\t\t$info = $this->remote_version( true );
\t\tif ( is_wp_error( $info ) || ! $this->has_update( $info ) || empty( $info['download_link'] ) ) {{
\t\t\twp_safe_redirect( admin_url( 'options-general.php?page={page_slug}&update_error=1' ) );
\t\t\texit;
\t\t}}

\t\t$plugin  = plugin_basename( {prefix}_FILE );
\t\t$updates = get_site_transient( 'update_plugins' );
\t\tif ( ! is_object( $updates ) ) {{
\t\t\t$updates = new \\stdClass();
\t\t}}
\t\tif ( ! isset( $updates->response ) || ! is_array( $updates->response ) ) {{
\t\t\t$updates->response = array();
\t\t}}
\t\t$updates->response[ $plugin ] = $this->update_object( $info, $plugin );
\t\tset_site_transient( 'update_plugins', $updates );

\t\trequire_once ABSPATH . 'wp-admin/includes/file.php';
\t\trequire_once ABSPATH . 'wp-admin/includes/class-wp-upgrader.php';
\t\t$upgrader = new \\Plugin_Upgrader( new \\Automatic_Upgrader_Skin() );
\t\t$result   = $upgrader->upgrade( $plugin );

\t\tdelete_transient( self::CACHE_KEY );
\t\tdelete_site_transient( 'update_plugins' );
\t\t$state = ( is_wp_error( $result ) || false === $result ) ? 'update_error=1' : 'updated=1';
\t\twp_safe_redirect( admin_url( 'options-general.php?page={page_slug}&' . $state ) );
\t\texit;
\t}}

\tprivate function remote_version( $force ) {{
\t\tif ( ! $force ) {{
\t\t\t$cached = get_transient( self::CACHE_KEY );
\t\t\tif ( is_array( $cached ) ) {{
\t\t\t\treturn $cached;
\t\t\t}}
\t\t}}

\t\t$params = array(
\t\t\t'edd_action'  => 'get_version',
\t\t\t'item_id'     => EDD_Config::DOWNLOAD_ID,
\t\t\t'url'         => home_url(),
\t\t\t'php_version' => PHP_VERSION,
\t\t\t'wp_version'  => get_bloginfo( 'version' ),
\t\t);
\t\tif ( '' !== License::key() ) {{
\t\t\t$params['license'] = License::key();
\t\t}}

\t\t$response = wp_remote_get(
\t\t\tadd_query_arg( $params, EDD_Config::STORE_URL ),
\t\t\tarray(
\t\t\t\t'timeout'     => 15,
\t\t\t\t'sslverify'   => true,
\t\t\t\t'redirection' => 3,
\t\t\t)
\t\t);
\t\tupdate_option( '{checked_option}', current_time( 'mysql' ), false );

\t\tif ( is_wp_error( $response ) ) {{
\t\t\treturn $response;
\t\t}}
\t\t$code = wp_remote_retrieve_response_code( $response );
\t\tif ( $code < 200 || $code >= 300 ) {{
\t\t\treturn new \\WP_Error( 'nalapps_update_http', 'The update server returned an invalid HTTP status.' );
\t\t}}

\t\t$data = json_decode( wp_remote_retrieve_body( $response ), true );
\t\tif ( ! is_array( $data ) ) {{
\t\t\treturn new \\WP_Error( 'nalapps_update_json', 'The update response could not be parsed.' );
\t\t}}
\t\tif ( ! empty( $data['error'] ) ) {{
\t\t\t$message = 'Update information is unavailable.';
\t\t\tif ( ! empty( $data['msg'] ) ) {{
\t\t\t\t$message = sanitize_text_field( (string) $data['msg'] );
\t\t\t}}
\t\t\treturn new \\WP_Error( 'nalapps_update_api', $message );
\t\t}}

\t\tset_transient( self::CACHE_KEY, $data, self::CACHE_TTL );
\t\treturn $data;
\t}}

\tprivate function has_update( $info ) {{
\t\treturn is_array( $info )
\t\t\t&& ! empty( $info['new_version'] )
\t\t\t&& version_compare( (string) $info['new_version'], {prefix}_VERSION, '>' );
\t}}

\tprivate function update_object( $info, $plugin ) {{
\t\treturn (object) array(
\t\t\t'id'          => '{slug}',
\t\t\t'slug'        => dirname( $plugin ),
\t\t\t'plugin'      => $plugin,
\t\t\t'new_version' => sanitize_text_field( (string) $info['new_version'] ),
\t\t\t'url'         => EDD_Config::STORE_URL,
\t\t\t'package'     => ! empty( $info['download_link'] ) ? esc_url_raw( $info['download_link'] ) : '',
\t\t);
\t}}
}}
'''


def augment_composer(target: Path) -> None:
    path = target / "composer.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["repositories"] = [{"type": "vcs", "url": EDD_SDK_REPOSITORY}]
    data["require"] = {EDD_SDK_PACKAGE: EDD_SDK_VERSION}
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def augment_main(target: Path, profile: dict) -> None:
    slug = profile["slug"]
    ns = namespace_suffix(slug)
    prefix = php_const_prefix(slug)
    path = target / f"{slug}.php"
    text = path.read_text(encoding="utf-8")
    marker = "// NalApps EDD runtime integration."
    if marker in text:
        return
    block = f'''\n\n{marker}\nadd_action(\n\t'edd_sl_sdk_registry',\n\tstatic function ( $registry ) {{\n\t\t$registry->register(\n\t\t\tarray(\n\t\t\t\t'id'      => '{slug}',\n\t\t\t\t'url'     => \\EOINGTI\\Plugins\\{ns}\\EDD_Config::STORE_URL,\n\t\t\t\t'item_id' => \\EOINGTI\\Plugins\\{ns}\\EDD_Config::DOWNLOAD_ID,\n\t\t\t\t'version' => {prefix}_VERSION,\n\t\t\t\t'file'    => {prefix}_FILE,\n\t\t\t)\n\t\t);\n\t}}\n);\n\n$nalapps_edd_sdk = {prefix}_PATH . 'vendor/easy-digital-downloads/edd-sl-sdk/edd-sl-sdk.php';\nif ( file_exists( $nalapps_edd_sdk ) ) {{\n\trequire_once $nalapps_edd_sdk;\n}}\n\nrequire_once {prefix}_PATH . 'includes/class-license.php';\nrequire_once {prefix}_PATH . 'includes/class-update-manager.php';\nnew \\EOINGTI\\Plugins\\{ns}\\Update_Manager();\n'''
    path.write_text(text + block, encoding="utf-8")


def product_scaffold(profile_path: Path, output: Path, clean: bool = False) -> Path:
    profile = validate_profile(profile_path)
    target = complete_scaffold(profile_path, output, clean=clean)
    if profile["product_type"] == "edd_paid":
        augment_composer(target)
        write_file(target, "includes/class-license.php", license_class(profile))
        write_file(target, "includes/class-update-manager.php", update_manager_class(profile))
        augment_main(target, profile)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--output", default=Path("build/scaffold"), type=Path)
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    target = product_scaffold(args.profile, args.output, args.clean)
    print(f"PASS product_scaffold={target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
