<?php
/**
 * NalApps Admin UI Kit v2.0.1 — reusable WordPress adapter template.
 *
 * Copy this file into the plugin and rename namespace/class/config values.
 * Do not place product business logic here.
 */
namespace MyPlugin;

defined('ABSPATH') || exit;

final class NalApps_Admin_UI {
    private const PAGE_PREFIX = 'my-plugin';
    private const POST_TYPE = 'my_plugin_item';
    private const STYLE_HANDLE = 'my-plugin-nalapps-ui';

    public function __construct() {
        add_action('admin_enqueue_scripts', array($this, 'enqueue_assets'), 20);
        add_filter('admin_body_class', array($this, 'admin_body_class'));
        add_action('all_admin_notices', array($this, 'render_header'), 1);
    }

    public function enqueue_assets(string $hook): void {
        if (!$this->is_target_screen($hook)) {
            return;
        }

        wp_enqueue_style(
            self::STYLE_HANDLE,
            plugins_url('assets/css/nalapps-admin-ui.css', MY_PLUGIN_FILE),
            array(),
            MY_PLUGIN_VERSION
        );

        wp_enqueue_style(
            self::STYLE_HANDLE . '-typography',
            plugins_url('assets/css/nalapps-admin-typography.css', MY_PLUGIN_FILE),
            array(self::STYLE_HANDLE),
            MY_PLUGIN_VERSION
        );

        wp_enqueue_script(
            self::STYLE_HANDLE,
            plugins_url('assets/js/nalapps-admin-ui.js', MY_PLUGIN_FILE),
            array(),
            MY_PLUGIN_VERSION,
            true
        );
    }

    public function admin_body_class(string $classes): string {
        if ($this->is_target_screen()) {
            $classes .= ' nalapps-admin-screen my-plugin-admin-screen';
        }
        return $classes;
    }

    public function render_header(): void {
        if (!$this->is_target_screen()) {
            return;
        }

        $context = $this->resolve_page_context();
        ?>
        <div class="nalapps-shell">
            <div class="nalapps-global-nav">
                <div class="nalapps-brand">
                    <span class="nalapps-brand__mark"><span class="dashicons dashicons-admin-generic"></span></span>
                    <span class="nalapps-brand__text">
                        <strong>MY PLUGIN NAME</strong>
                        <small>NalApps Admin UI v2.0.1</small>
                    </span>
                </div>
                <nav class="nalapps-nav" aria-label="플러그인 관리 메뉴">
                    <a class="<?php echo $context['active'] === 'dashboard' ? 'is-active' : ''; ?>" href="<?php echo esc_url(admin_url('admin.php?page=my-plugin-dashboard')); ?>">관리 홈</a>
                    <a class="<?php echo $context['active'] === 'list' ? 'is-active' : ''; ?>" href="<?php echo esc_url(admin_url('edit.php?post_type=' . self::POST_TYPE)); ?>">목록</a>
                    <a class="<?php echo $context['active'] === 'new' ? 'is-active' : ''; ?>" href="<?php echo esc_url(admin_url('post-new.php?post_type=' . self::POST_TYPE)); ?>">새로 추가</a>
                </nav>
            </div>
            <div class="nalapps-page-header">
                <span class="nalapps-page-kicker">EOINGTI LAB · NALAPPS</span>
                <h1><?php echo esc_html($context['title']); ?></h1>
                <p><?php echo esc_html($context['description']); ?></p>
            </div>
        </div>
        <?php
    }

    private function resolve_page_context(): array {
        $screen = function_exists('get_current_screen') ? get_current_screen() : null;
        if ($screen && $screen->post_type === self::POST_TYPE) {
            if ($screen->base === 'edit') {
                return array('active' => 'list', 'title' => '목록', 'description' => '등록된 항목을 확인하고 관리합니다.');
            }
            if ($screen->base === 'post') {
                $is_new = isset($screen->action) && $screen->action === 'add';
                return array(
                    'active' => $is_new ? 'new' : 'list',
                    'title' => $is_new ? '새 항목 추가' : '항목 수정',
                    'description' => $is_new ? '새 항목을 등록합니다.' : '기존 항목을 수정합니다.',
                );
            }
        }
        return array('active' => 'dashboard', 'title' => '관리 홈', 'description' => '플러그인 상태와 주요 작업을 한 곳에서 관리합니다.');
    }

    private function is_target_screen(string $hook = ''): bool {
        $screen = function_exists('get_current_screen') ? get_current_screen() : null;
        if ($screen) {
            if ($screen->post_type === self::POST_TYPE) {
                return true;
            }
            if (strpos((string) $screen->id, self::PAGE_PREFIX) !== false) {
                return true;
            }
        }

        if (strpos($hook, self::PAGE_PREFIX) !== false) {
            return true;
        }

        $page = isset($_GET['page']) ? sanitize_key(wp_unslash($_GET['page'])) : '';
        $post_type = isset($_GET['post_type']) ? sanitize_key(wp_unslash($_GET['post_type'])) : '';
        return strpos($page, self::PAGE_PREFIX) === 0 || $post_type === self::POST_TYPE;
    }
}
