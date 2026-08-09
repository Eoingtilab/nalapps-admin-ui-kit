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
    # EDD SL SDK derives option names from the registered id verbatim.
    # Keep hyphens in the canonical slug; replacing them with underscores
    # would make the generated plugin read different options than the SDK.
    option_prefix = profile["slug"]
    return f'''<?php
/** EDD Software Licensing state adapter. @package {ns} */
namespace EOINGTI\\Plugins\\{ns};
if ( ! defined( 'ABSPATH' ) ) {{ exit; }}
final class License {{
    const KEY_OPTION = '{option_prefix}_license_key';
    const STATUS_OPTION = '{option_prefix}_license';
    public static function key() {{ return trim( (string) get_option( self::KEY_OPTION, '' ) ); }}
    public static function status() {{
        $data = get_option( self::STATUS_OPTION );
        if ( is_object( $data ) && isset( $data->license ) ) {{ return sanitize_key( (string) $data->license ); }}
        if ( is_array( $data ) && isset( $data['license'] ) ) {{ return sanitize_key( (string) $data['license'] ); }}
        return 'inactive';
    }}
    public static function is_valid() {{ return in_array( self::status(), array( 'valid', 'active' ), true ); }}
    private function __construct() {{}}
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
/** EDD hybrid updater. @package {ns} */
namespace EOINGTI\\Plugins\\{ns};
if ( ! defined( 'ABSPATH' ) ) {{ exit; }}
final class Update_Manager {{
    const CACHE_KEY = '{cache_key}';
    const CACHE_TTL = 6 * HOUR_IN_SECONDS;
    public function __construct() {{
        add_filter( 'pre_set_site_transient_update_plugins', array( $this, 'inject_update' ) );
        add_action( 'admin_menu', array( $this, 'register_page' ) );
        add_action( 'admin_post_{action_prefix}_check_updates', array( $this, 'manual_check' ) );
        add_action( 'admin_post_{action_prefix}_install_update', array( $this, 'install_update' ) );
    }}
    public function register_page() {{
        add_options_page( '{profile["plugin_name"]} Updates', '{profile["plugin_name"]} Updates', 'update_plugins', '{page_slug}', array( $this, 'render_page' ) );
    }}
    public function inject_update( $transient ) {{
        if ( ! is_object( $transient ) ) {{ $transient = new \\stdClass(); }}
        if ( ! isset( $transient->response ) || ! is_array( $transient->response ) ) {{ $transient->response = array(); }}
        $info = $this->remote_version( false );
        if ( is_wp_error( $info ) || ! $this->has_update( $info ) ) {{ return $transient; }}
        $plugin = plugin_basename( {prefix}_FILE );
        $transient->response[ $plugin ] = $this->update_object( $info, $plugin );
        return $transient;
    }}
    public function render_page() {{
        if ( ! current_user_can( 'update_plugins' ) ) {{ wp_die( esc_html( 'Insufficient permissions.' ) ); }}
        $info = $this->remote_version( false );
        $error = is_wp_error( $info ) ? $info->get_error_message() : '';
        $latest = ( ! $error && ! empty( $info['new_version'] ) ) ? (string) $info['new_version'] : 'Unavailable';
        $available = ! $error && $this->has_update( $info );
        $download_ready = $available && License::is_valid() && ! empty( $info['download_link'] );
        $last_checked = (string) get_option( '{checked_option}', '' );
        echo '<div class="wrap"><h1>' . esc_html( '{profile["plugin_name"]} Updates' ) . '</h1>';
        echo '<p>' . esc_html( 'Current: ' . {prefix}_VERSION . ' / Latest: ' . $latest ) . '</p>';
        echo '<p>' . esc_html( 'License: ' . License::status() . ' / Last checked: ' . ( $last_checked ?: '-' ) ) . '</p>';
        if ( $error ) {{ echo '<div class="notice notice-error inline"><p>' . esc_html( $error ) . '</p></div>'; }}
        elseif ( $available ) {{ echo '<div class="notice notice-info inline"><p>' . esc_html( 'A new version is available.' ) . '</p></div>'; }}
        else {{ echo '<div class="notice notice-success inline"><p>' . esc_html( 'The plugin is up to date.' ) . '</p></div>'; }}
        echo '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '">';
        echo '<input type="hidden" name="action" value="{action_prefix}_check_updates">';
        wp_nonce_field( '{action_prefix}_check_updates' );
        submit_button( 'Check for updates', 'secondary', 'submit', false );
        echo '</form>';
        if ( $download_ready ) {{
            echo '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '">';
            echo '<input type="hidden" name="action" value="{action_prefix}_install_update">';
            wp_nonce_field( '{action_prefix}_install_update' );
            submit_button( 'Update now', 'primary', 'submit', false );
            echo '</form>';
        }}
        echo '</div>';
    }}
    public function manual_check() {{
        if ( ! current_user_can( 'update_plugins' ) ) {{ wp_die( esc_html( 'Insufficient permissions.' ) ); }}
        check_admin_referer( '{action_prefix}_check_updates' );
        delete_transient( self::CACHE_KEY );
        delete_site_transient( 'update_plugins' );
        $this->remote_version( true );
        wp_update_plugins();
        wp_safe_redirect( admin_url( 'options-general.php?page={page_slug}&checked=1' ) );
        exit;
    }}
    public function install_update() {{
        if ( ! current_user_can( 'update_plugins' ) ) {{ wp_die( esc_html( 'Insufficient permissions.' ) ); }}
        check_admin_referer( '{action_prefix}_install_update' );
        if ( ! License::is_valid() ) {{ wp_safe_redirect( admin_url( 'options-general.php?page={page_slug}&license_required=1' ) ); exit; }}
        $info = $this->remote_version( true );
        if ( is_wp_error( $info ) || ! $this->has_update( $info ) || empty( $info['download_link'] ) ) {{ wp_safe_redirect( admin_url( 'options-general.php?page={page_slug}&update_error=1' ) ); exit; }}
        $plugin = plugin_basename( {prefix}_FILE );
        $updates = get_site_transient( 'update_plugins' );
        if ( ! is_object( $updates ) ) {{ $updates = new \\stdClass(); }}
        if ( ! isset( $updates->response ) || ! is_array( $updates->response ) ) {{ $updates->response = array(); }}
        $updates->response[ $plugin ] = $this->update_object( $info, $plugin );
        set_site_transient( 'update_plugins', $updates );
        require_once ABSPATH . 'wp-admin/includes/file.php';
        require_once ABSPATH . 'wp-admin/includes/class-wp-upgrader.php';
        $upgrader = new \\Plugin_Upgrader( new \\Automatic_Upgrader_Skin() );
        $result = $upgrader->upgrade( $plugin );
        delete_transient( self::CACHE_KEY );
        delete_site_transient( 'update_plugins' );
        $state = ( is_wp_error( $result ) || false === $result ) ? 'update_error=1' : 'updated=1';
        wp_safe_redirect( admin_url( 'options-general.php?page={page_slug}&' . $state ) );
        exit;
    }}
    private function remote_version( $force ) {{
        if ( ! $force ) {{ $cached = get_transient( self::CACHE_KEY ); if ( is_array( $cached ) ) {{ return $cached; }} }}
        $params = array( 'edd_action' => 'get_version', 'item_id' => EDD_Config::DOWNLOAD_ID, 'url' => home_url(), 'php_version' => PHP_VERSION, 'wp_version' => get_bloginfo( 'version' ) );
        if ( '' !== License::key() ) {{ $params['license'] = License::key(); }}
        $response = wp_remote_get( add_query_arg( $params, EDD_Config::STORE_URL ), array( 'timeout' => 15, 'sslverify' => true, 'redirection' => 3 ) );
        update_option( '{checked_option}', current_time( 'mysql' ), false );
        if ( is_wp_error( $response ) ) {{ return $response; }}
        $code = wp_remote_retrieve_response_code( $response );
        if ( $code < 200 || $code >= 300 ) {{ return new \\WP_Error( 'nalapps_update_http', 'The update server returned an invalid HTTP status.' ); }}
        $data = json_decode( wp_remote_retrieve_body( $response ), true );
        if ( ! is_array( $data ) ) {{ return new \\WP_Error( 'nalapps_update_json', 'The update response could not be parsed.' ); }}
        if ( ! empty( $data['error'] ) ) {{ return new \\WP_Error( 'nalapps_update_api', ! empty( $data['msg'] ) ? sanitize_text_field( (string) $data['msg'] ) : 'Update information is unavailable.' ); }}
        set_transient( self::CACHE_KEY, $data, self::CACHE_TTL );
        return $data;
    }}
    private function has_update( $info ) {{ return is_array( $info ) && ! empty( $info['new_version'] ) && version_compare( (string) $info['new_version'], {prefix}_VERSION, '>' ); }}
    private function update_object( $info, $plugin ) {{
        return (object) array( 'id' => '{slug}', 'slug' => dirname( $plugin ), 'plugin' => $plugin, 'new_version' => sanitize_text_field( (string) $info['new_version'] ), 'url' => EDD_Config::STORE_URL, 'package' => ! empty( $info['download_link'] ) ? esc_url_raw( $info['download_link'] ) : '' );
    }}
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
    block = f'''\n\n{marker}\nadd_action(\n    'edd_sl_sdk_registry',\n    static function ( $registry ) {{\n        $registry->register( array( 'id' => '{slug}', 'url' => \\EOINGTI\\Plugins\\{ns}\\EDD_Config::STORE_URL, 'item_id' => \\EOINGTI\\Plugins\\{ns}\\EDD_Config::DOWNLOAD_ID, 'version' => {prefix}_VERSION, 'file' => {prefix}_FILE ) );\n    }}\n);\n$nalapps_edd_sdk = {prefix}_PATH . 'vendor/easy-digital-downloads/edd-sl-sdk/edd-sl-sdk.php';\nif ( file_exists( $nalapps_edd_sdk ) ) {{ require_once $nalapps_edd_sdk; }}\nrequire_once {prefix}_PATH . 'includes/class-license.php';\nrequire_once {prefix}_PATH . 'includes/class-update-manager.php';\nnew \\EOINGTI\\Plugins\\{ns}\\Update_Manager();\n'''
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
