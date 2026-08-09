<?php
/**
 * NalApps Admin UI — refined commercial workspace adapter template.
 *
 * Copy this file into the plugin and rename namespace/class/config values.
 * Keep product business logic outside this presentation adapter.
 */
namespace MyPlugin;

defined( 'ABSPATH' ) || exit;

final class NalApps_Admin_UI {
	private const PAGE_PREFIX  = 'my-plugin';
	private const POST_TYPE    = 'my_plugin_item';
	private const STYLE_HANDLE = 'my-plugin-nalapps-ui';

	public function __construct() {
		add_action( 'admin_enqueue_scripts', array( $this, 'enqueue_assets' ), 20 );
		add_filter( 'admin_body_class', array( $this, 'admin_body_class' ) );
		add_action( 'in_admin_header', array( $this, 'render_header' ), 20 );
	}

	public function enqueue_assets( $hook ) {
		if ( ! $this->is_target_screen( $hook ) ) {
			return;
		}
		wp_enqueue_style( self::STYLE_HANDLE, plugins_url( 'assets/css/nalapps-admin-ui.css', MY_PLUGIN_FILE ), array(), MY_PLUGIN_VERSION );
		wp_enqueue_style( self::STYLE_HANDLE . '-typography', plugins_url( 'assets/css/nalapps-admin-typography.css', MY_PLUGIN_FILE ), array( self::STYLE_HANDLE ), MY_PLUGIN_VERSION );
		wp_enqueue_script( self::STYLE_HANDLE, plugins_url( 'assets/js/nalapps-admin-ui.js', MY_PLUGIN_FILE ), array(), MY_PLUGIN_VERSION, true );
	}

	public function admin_body_class( $classes ) {
		if ( $this->is_target_screen() ) {
			$classes .= ' nalapps-admin-screen my-plugin-admin-screen';
		}
		return $classes;
	}

	public function render_header() {
		if ( ! $this->is_target_screen() ) {
			return;
		}
		$context = $this->resolve_page_context();
		?>
		<div class="nalapps-shell">
			<div class="nalapps-global-nav">
				<div class="nalapps-brand">
					<span class="nalapps-brand__mark"><span class="dashicons dashicons-admin-generic"></span></span>
					<span class="nalapps-brand__text"><strong>MY PLUGIN NAME</strong><small>NalApps WordPress Plugin Standard</small></span>
				</div>
				<nav class="nalapps-nav" aria-label="플러그인 관리 메뉴">
					<a class="<?php echo 'dashboard' === $context['active'] ? 'is-active' : ''; ?>" href="<?php echo esc_url( admin_url( 'admin.php?page=my-plugin-dashboard' ) ); ?>">관리 홈</a>
					<a class="<?php echo 'list' === $context['active'] ? 'is-active' : ''; ?>" href="<?php echo esc_url( admin_url( 'edit.php?post_type=' . self::POST_TYPE ) ); ?>">목록</a>
					<a class="<?php echo 'new' === $context['active'] ? 'is-active' : ''; ?>" href="<?php echo esc_url( admin_url( 'post-new.php?post_type=' . self::POST_TYPE ) ); ?>">새로 추가</a>
					<a class="<?php echo 'updates' === $context['active'] ? 'is-active' : ''; ?>" href="<?php echo esc_url( admin_url( 'admin.php?page=my-plugin-updates' ) ); ?>">업데이트</a>
					<a class="<?php echo 'maintenance' === $context['active'] ? 'is-active' : ''; ?>" href="<?php echo esc_url( admin_url( 'admin.php?page=my-plugin-maintenance' ) ); ?>">백업/복구</a>
					<a class="<?php echo 'status' === $context['active'] ? 'is-active' : ''; ?>" href="<?php echo esc_url( admin_url( 'admin.php?page=my-plugin-system-status' ) ); ?>">시스템 정보</a>
				</nav>
			</div>
			<div class="nalapps-page-header">
				<div class="nalapps-page-header__copy">
					<span class="nalapps-page-kicker">EOINGTI LAB · NALAPPS</span>
					<h1><?php echo esc_html( $context['title'] ); ?></h1>
					<p><?php echo esc_html( $context['description'] ); ?></p>
				</div>
				<?php if ( ! empty( $context['action_url'] ) && ! empty( $context['action_label'] ) ) : ?>
					<div class="nalapps-page-actions"><a class="button button-primary" href="<?php echo esc_url( $context['action_url'] ); ?>"><?php echo esc_html( $context['action_label'] ); ?></a></div>
				<?php endif; ?>
			</div>
		</div>
		<?php
	}

	private function resolve_page_context() {
		$screen = function_exists( 'get_current_screen' ) ? get_current_screen() : null;
		$page   = isset( $_GET['page'] ) ? sanitize_key( wp_unslash( $_GET['page'] ) ) : '';
		if ( self::PAGE_PREFIX . '-updates' === $page ) {
			return array( 'active' => 'updates', 'title' => '업데이트', 'description' => '새 버전을 확인하고 검증된 설치 패키지로 바로 업데이트합니다.', 'action_url' => '', 'action_label' => '' );
		}
		if ( self::PAGE_PREFIX . '-maintenance' === $page ) {
			return array( 'active' => 'maintenance', 'title' => '백업 및 복구', 'description' => '데이터 백업·가져오기, 코드 롤백, 제거 시 데이터 정책을 관리합니다.', 'action_url' => '', 'action_label' => '' );
		}
		if ( self::PAGE_PREFIX . '-system-status' === $page ) {
			return array( 'active' => 'status', 'title' => '시스템 정보', 'description' => '비밀정보를 노출하지 않고 플러그인과 WordPress 환경을 진단합니다.', 'action_url' => '', 'action_label' => '' );
		}
		if ( $screen && self::POST_TYPE === $screen->post_type ) {
			if ( 'edit' === $screen->base ) {
				return array( 'active' => 'list', 'title' => '목록', 'description' => '등록된 항목을 확인하고 관리합니다.', 'action_url' => admin_url( 'post-new.php?post_type=' . self::POST_TYPE ), 'action_label' => '새로 추가' );
			}
			if ( 'post' === $screen->base ) {
				$is_new = isset( $screen->action ) && 'add' === $screen->action;
				return array( 'active' => $is_new ? 'new' : 'list', 'title' => $is_new ? '새 항목 추가' : '항목 수정', 'description' => $is_new ? '새 항목을 등록합니다.' : '기존 항목을 수정합니다.', 'action_url' => admin_url( 'edit.php?post_type=' . self::POST_TYPE ), 'action_label' => '목록' );
			}
		}
		return array( 'active' => 'dashboard', 'title' => '관리 홈', 'description' => '플러그인 상태와 주요 작업을 한 곳에서 관리합니다.', 'action_url' => admin_url( 'post-new.php?post_type=' . self::POST_TYPE ), 'action_label' => '새로 추가' );
	}

	private function is_target_screen( $hook = '' ) {
		$screen = function_exists( 'get_current_screen' ) ? get_current_screen() : null;
		if ( $screen ) {
			if ( self::POST_TYPE === $screen->post_type ) {
				return true;
			}
			if ( false !== strpos( (string) $screen->id, self::PAGE_PREFIX ) ) {
				return true;
			}
		}
		if ( false !== strpos( (string) $hook, self::PAGE_PREFIX ) ) {
			return true;
		}
		$page      = isset( $_GET['page'] ) ? sanitize_key( wp_unslash( $_GET['page'] ) ) : '';
		$post_type = isset( $_GET['post_type'] ) ? sanitize_key( wp_unslash( $_GET['post_type'] ) ) : '';
		return 0 === strpos( $page, self::PAGE_PREFIX ) || self::POST_TYPE === $post_type;
	}
}
