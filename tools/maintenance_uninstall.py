#!/usr/bin/env python3
"""Generate NalApps preserve/delete-all uninstall runtime."""
from __future__ import annotations

from maintenance_data import php_array


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
    post_types_php = php_array(post_types)
    table_lines = "\n".join(
        f"$wpdb->query( 'DROP TABLE IF EXISTS ' . $wpdb->prefix . '{table}' ); // phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.SchemaChange, WordPress.DB.PreparedSQL.NotPrepared"
        for table in tables
    )
    wpdb_line = "$wpdb = $GLOBALS['wpdb'];" if tables else ""

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

{wpdb_line}
{table_lines}

do_action( '{action}_delete_all_data' );
'''
