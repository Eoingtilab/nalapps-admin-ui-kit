#!/usr/bin/env python3
"""Generate product-native EDD Software Licensing management UI."""
from __future__ import annotations

from scaffold_plugin import namespace_suffix


def license_management_class(profile: dict) -> str:
    ns = namespace_suffix(profile["slug"])
    slug = profile["slug"]
    action = slug.replace("-", "_")
    page_slug = f"{slug}-license"
    license_mode = profile.get("license_mode", "paid")
    license_label = "무료 (라이선스 등록)" if license_mode == "free_registered" else "유료 (Paid)"
    license_help = (
        "무료 라이선스 등록형 제품입니다. 발급된 라이선스 키를 이 사이트에 등록하고 활성화해야 합니다."
        if license_mode == "free_registered"
        else "유료 라이선스 제품입니다. 구매 후 발급된 시리얼 키를 이 사이트에 등록하고 활성화해야 합니다."
    )
    return f'''<?php
/**
 * Product-native EDD Software Licensing management.
 *
 * @package {ns}
 */

namespace EOINGTI\\Plugins\\{ns};

if ( ! defined( 'ABSPATH' ) ) {{
\texit;
}}

final class License {{
\tconst KEY_OPTION    = '{slug}_license_key';
\tconst STATUS_OPTION = '{slug}_license';

\tpublic function __construct() {{
\t\tadd_action( 'admin_menu', array( $this, 'register_page' ) );
\t\tadd_action( 'admin_post_{action}_activate_license', array( $this, 'activate_license' ) );
\t\tadd_action( 'admin_post_{action}_check_license', array( $this, 'check_license' ) );
\t\tadd_action( 'admin_post_{action}_deactivate_license', array( $this, 'deactivate_license' ) );
\t}}

\tpublic function register_page() {{
\t\tadd_options_page(
\t\t\t'{profile["plugin_name"]} License',
\t\t\t'{profile["plugin_name"]} License',
\t\t\t'manage_options',
\t\t\t'{page_slug}',
\t\t\tarray( $this, 'render_page' )
\t\t);
\t}}

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
\t\treturn '' !== self::key() && in_array( self::status(), array( 'valid', 'active' ), true );
\t}}

\tpublic function render_page() {{
\t\tif ( ! current_user_can( 'manage_options' ) ) {{
\t\t\twp_die( esc_html( 'Insufficient permissions.' ) );
\t\t}}
\t\techo '<div class="wrap nalapps-maintenance-wrap"><div class="nalapps-panel">';
\t\techo '<div class="nalapps-panel-heading"><div><h2>License</h2><p>' . esc_html( '{license_help}' ) . '</p></div></div>';
\t\techo '<p><strong>라이선스:</strong> ' . esc_html( '{license_label}' ) . '</p>';
\t\techo '<p><strong>현재 상태:</strong> ' . esc_html( self::status() ) . '</p>';
\t\techo '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '">';
\t\techo '<input type="hidden" name="action" value="{action}_activate_license">';
\t\twp_nonce_field( '{action}_activate_license' );
\t\techo '<p><label><strong>Serial key</strong><br><input type="text" class="regular-text" name="license_key" maxlength="256" autocomplete="off" value="' . esc_attr( self::key() ) . '"></label></p>';
\t\tsubmit_button( 'Save and activate', 'primary', 'submit', false );
\t\techo '</form>';
\t\tif ( '' !== self::key() ) {{
\t\t\techo '<div class="nalapps-inline-actions">';
\t\t\techo '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '"><input type="hidden" name="action" value="{action}_check_license">';
\t\t\twp_nonce_field( '{action}_check_license' );
\t\t\tsubmit_button( 'Check license', 'secondary', 'submit', false );
\t\t\techo '</form>';
\t\t\techo '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '"><input type="hidden" name="action" value="{action}_deactivate_license">';
\t\t\twp_nonce_field( '{action}_deactivate_license' );
\t\t\tsubmit_button( 'Deactivate on this site', 'secondary', 'submit', false );
\t\t\techo '</form></div>';
\t\t}}
\t\techo '<p class="description">License keys must never be included in diagnostics or portable data exports.</p></div></div>';
\t}}

\tpublic function activate_license() {{
\t\t$this->assert_admin( '{action}_activate_license' );
\t\t$key = isset( $_POST['license_key'] ) ? self::sanitize_license_key( wp_unslash( $_POST['license_key'] ) ) : ''; // phpcs:ignore WordPress.Security.NonceVerification.Missing -- nonce verified immediately above.
\t\tif ( '' === $key ) {{
\t\t\t$this->redirect( 'empty_key' );
\t\t}}
\t\tupdate_option( self::KEY_OPTION, $key, false );
\t\t$data = self::request( 'activate_license', $key );
\t\tself::store_status( $data );
\t\t$this->redirect( self::response_is_valid( $data ) ? 'activated' : 'activation_failed' );
\t}}

\tpublic function check_license() {{
\t\t$this->assert_admin( '{action}_check_license' );
\t\t$key = self::key();
\t\tif ( '' === $key ) {{
\t\t\t$this->redirect( 'empty_key' );
\t\t}}
\t\t$data = self::request( 'check_license', $key );
\t\tself::store_status( $data );
\t\t$this->redirect( self::response_is_valid( $data ) ? 'valid' : 'invalid' );
\t}}

\tpublic function deactivate_license() {{
\t\t$this->assert_admin( '{action}_deactivate_license' );
\t\t$key = self::key();
\t\tif ( '' !== $key ) {{
\t\t\tself::request( 'deactivate_license', $key );
\t\t}}
\t\tupdate_option( self::STATUS_OPTION, (object) array( 'license' => 'inactive' ), false );
\t\tdelete_transient( Update_Manager::CACHE_KEY );
\t\tdelete_site_transient( 'update_plugins' );
\t\t$this->redirect( 'deactivated' );
\t}}

\tprivate static function request( $edd_action, $key ) {{
\t\t$response = wp_remote_post(
\t\t\tEDD_Config::STORE_URL,
\t\t\tarray(
\t\t\t\t'timeout'   => 15,
\t\t\t\t'sslverify' => true,
\t\t\t\t'body'      => array(
\t\t\t\t\t'edd_action' => $edd_action,
\t\t\t\t\t'license'    => $key,
\t\t\t\t\t'item_id'    => EDD_Config::DOWNLOAD_ID,
\t\t\t\t\t'url'        => home_url(),
\t\t\t\t),
\t\t\t)
\t\t);
\t\tif ( is_wp_error( $response ) ) {{
\t\t\treturn $response;
\t\t}}
\t\t$code = wp_remote_retrieve_response_code( $response );
\t\tif ( $code < 200 || $code >= 300 ) {{
\t\t\treturn new \\WP_Error( 'nalapps_license_http', 'The license server returned an invalid HTTP status.' );
\t\t}}
\t\t$data = json_decode( wp_remote_retrieve_body( $response ) );
\t\treturn is_object( $data ) ? $data : new \\WP_Error( 'nalapps_license_json', 'The license response could not be parsed.' );
\t}}

\tprivate static function store_status( $data ) {{
\t\tif ( is_wp_error( $data ) ) {{
\t\t\tupdate_option( self::STATUS_OPTION, (object) array( 'license' => 'error' ), false );
\t\t\treturn;
\t\t}}
\t\tupdate_option( self::STATUS_OPTION, $data, false );
\t\tdelete_transient( Update_Manager::CACHE_KEY );
\t\tdelete_site_transient( 'update_plugins' );
\t}}

\tprivate static function response_is_valid( $data ) {{
\t\treturn is_object( $data ) && isset( $data->license ) && in_array( sanitize_key( (string) $data->license ), array( 'valid', 'active' ), true );
\t}}

\tprivate static function sanitize_license_key( $key ) {{
\t\t$key = preg_replace( '/[^A-Za-z0-9_-]/', '', trim( (string) $key ) );
\t\treturn substr( (string) $key, 0, 256 );
\t}}

\tprivate function assert_admin( $nonce_action ) {{
\t\tif ( ! current_user_can( 'manage_options' ) ) {{
\t\t\twp_die( esc_html( 'Insufficient permissions.' ) );
\t\t}}
\t\tcheck_admin_referer( $nonce_action );
\t}}

\tprivate function redirect( $state ) {{
\t\twp_safe_redirect( admin_url( 'options-general.php?page={page_slug}&state=' . sanitize_key( $state ) ) );
\t\texit;
\t}}
}}
'''
