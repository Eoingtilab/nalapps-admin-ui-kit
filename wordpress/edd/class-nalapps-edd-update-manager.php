<?php
/**
 * NalApps EDD hybrid update manager template.
 *
 * Purpose:
 * - Query an Easy Digital Downloads + Software Licensing store with get_version.
 * - Surface updates in the normal WordPress Plugins screen.
 * - Provide the same update status inside the plugin's own admin screen.
 *
 * Replace all MY_PLUGIN_* constants and option names before use.
 */
namespace MyPlugin;

defined('ABSPATH') || exit;

final class NalApps_EDD_Update_Manager {
    private const CACHE_KEY = 'my_plugin_edd_version_info';
    private const CACHE_TTL = 6 * HOUR_IN_SECONDS;

    public function __construct() {
        add_filter('pre_set_site_transient_update_plugins', array($this, 'inject_wordpress_update'));
        add_action('admin_menu', array($this, 'register_update_page'), 40);
        add_action('admin_post_my_plugin_check_updates', array($this, 'handle_manual_check'));
        add_action('admin_post_my_plugin_install_update', array($this, 'handle_install_update'));
    }

    public function register_update_page(): void {
        add_submenu_page(
            'my-plugin-dashboard',
            '업데이트',
            '업데이트',
            'update_plugins',
            'my-plugin-update',
            array($this, 'render_update_page')
        );
    }

    public function inject_wordpress_update($transient) {
        if (!is_object($transient)) {
            $transient = new \stdClass();
        }
        if (!isset($transient->response) || !is_array($transient->response)) {
            $transient->response = array();
        }

        $info = $this->get_remote_version(false);
        if (is_wp_error($info) || empty($info['new_version'])) {
            return $transient;
        }

        if (!version_compare((string) $info['new_version'], MY_PLUGIN_VERSION, '>')) {
            return $transient;
        }

        $plugin = plugin_basename(MY_PLUGIN_FILE);
        $transient->response[$plugin] = (object) array(
            'id'          => 'my-plugin',
            'slug'        => dirname($plugin),
            'plugin'      => $plugin,
            'new_version' => sanitize_text_field((string) $info['new_version']),
            'url'         => MY_PLUGIN_STORE_URL,
            'package'     => !empty($info['download_link']) ? esc_url_raw($info['download_link']) : '',
        );

        return $transient;
    }

    public function render_update_page(): void {
        if (!current_user_can('update_plugins')) {
            wp_die('권한이 없습니다.');
        }

        $info = $this->get_remote_version(false);
        $latest = is_wp_error($info) || empty($info['new_version']) ? '확인할 수 없음' : (string) $info['new_version'];
        $available = !is_wp_error($info) && !empty($info['new_version']) && version_compare((string) $info['new_version'], MY_PLUGIN_VERSION, '>');
        ?>
        <div class="wrap nalapps-update-page">
            <div class="nalapps-panel">
                <div class="nalapps-panel-heading">
                    <div>
                        <h2>제품 업데이트</h2>
                        <p>현재 버전과 EDD에 등록된 최신 버전을 비교합니다.</p>
                    </div>
                </div>
                <p><strong>현재 버전:</strong> <?php echo esc_html(MY_PLUGIN_VERSION); ?></p>
                <p><strong>최신 버전:</strong> <?php echo esc_html($latest); ?></p>
                <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" style="display:inline-block;margin-right:8px;">
                    <input type="hidden" name="action" value="my_plugin_check_updates">
                    <?php wp_nonce_field('my_plugin_check_updates'); ?>
                    <button class="button" type="submit">업데이트 확인</button>
                </form>
                <?php if ($available && !empty($info['download_link'])) : ?>
                    <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" style="display:inline-block;">
                        <input type="hidden" name="action" value="my_plugin_install_update">
                        <?php wp_nonce_field('my_plugin_install_update'); ?>
                        <button class="button button-primary" type="submit">지금 업데이트</button>
                    </form>
                <?php endif; ?>
            </div>
        </div>
        <?php
    }

    public function handle_manual_check(): void {
        if (!current_user_can('update_plugins')) {
            wp_die('권한이 없습니다.');
        }
        check_admin_referer('my_plugin_check_updates');
        delete_transient(self::CACHE_KEY);
        delete_site_transient('update_plugins');
        wp_update_plugins();
        wp_safe_redirect(admin_url('admin.php?page=my-plugin-update&checked=1'));
        exit;
    }

    public function handle_install_update(): void {
        if (!current_user_can('update_plugins')) {
            wp_die('권한이 없습니다.');
        }
        check_admin_referer('my_plugin_install_update');

        $info = $this->get_remote_version(true);
        if (is_wp_error($info) || empty($info['download_link'])) {
            wp_safe_redirect(admin_url('admin.php?page=my-plugin-update&update_error=1'));
            exit;
        }

        $plugin = plugin_basename(MY_PLUGIN_FILE);
        $updates = get_site_transient('update_plugins');
        if (!is_object($updates)) {
            $updates = new \stdClass();
        }
        if (!isset($updates->response) || !is_array($updates->response)) {
            $updates->response = array();
        }
        $updates->response[$plugin] = (object) array(
            'id'          => 'my-plugin',
            'slug'        => dirname($plugin),
            'plugin'      => $plugin,
            'new_version' => sanitize_text_field((string) $info['new_version']),
            'url'         => MY_PLUGIN_STORE_URL,
            'package'     => esc_url_raw($info['download_link']),
        );
        set_site_transient('update_plugins', $updates);

        require_once ABSPATH . 'wp-admin/includes/class-wp-upgrader.php';
        require_once ABSPATH . 'wp-admin/includes/file.php';
        $upgrader = new \Plugin_Upgrader(new \Automatic_Upgrader_Skin());
        $result = $upgrader->upgrade($plugin);

        delete_transient(self::CACHE_KEY);
        delete_site_transient('update_plugins');

        $state = is_wp_error($result) || $result === false ? 'update_error=1' : 'updated=1';
        wp_safe_redirect(admin_url('admin.php?page=my-plugin-update&' . $state));
        exit;
    }

    private function get_remote_version(bool $force) {
        if (!$force) {
            $cached = get_transient(self::CACHE_KEY);
            if (is_array($cached)) {
                return $cached;
            }
        }

        $license = trim((string) get_option('my-plugin_license_key', ''));
        $params = array(
            'edd_action'  => 'get_version',
            'item_id'     => MY_PLUGIN_EDD_ITEM_ID,
            'url'         => home_url(),
            'php_version' => PHP_VERSION,
            'wp_version'  => get_bloginfo('version'),
        );
        if ($license !== '') {
            $params['license'] = $license;
        }

        $response = wp_remote_get(add_query_arg($params, MY_PLUGIN_STORE_URL), array('timeout' => 15, 'sslverify' => true));
        if (is_wp_error($response)) {
            return $response;
        }
        $data = json_decode(wp_remote_retrieve_body($response), true);
        if (!is_array($data)) {
            return new \WP_Error('nalapps_edd_invalid_response', '업데이트 서버 응답을 해석할 수 없습니다.');
        }

        set_transient(self::CACHE_KEY, $data, self::CACHE_TTL);
        return $data;
    }
}
