<?php
/**
 * NalApps System Status page template.
 *
 * Never expose secrets. Product plugins may add non-sensitive checks through
 * the nalapps_standard_status_rows filter.
 */
namespace NalApps\Standard;

if (!defined('ABSPATH')) {
	exit;
}

final class System_Status {
	private $parent_slug;
	private $page_slug;
	private $title;
	private $standard;

	public function __construct($parent_slug, $page_slug, $title, Plugin_Standard $standard) {
		$this->parent_slug = sanitize_key($parent_slug);
		$this->page_slug = sanitize_key($page_slug);
		$this->title = sanitize_text_field($title);
		$this->standard = $standard;
	}

	public function register() {
		add_action('admin_menu', array($this, 'register_menu'), 90);
	}

	public function register_menu() {
		add_submenu_page(
			$this->parent_slug,
			$this->title,
			$this->title,
			'manage_options',
			$this->page_slug,
			array($this, 'render')
		);
	}

	public function render() {
		if (!current_user_can('manage_options')) {
			wp_die(esc_html__('권한이 없습니다.', 'nalapps'));
		}

		$snapshot = $this->standard->get_status_snapshot();
		$rows = array(
			'플러그인 버전' => $snapshot['plugin_version'],
			'WordPress'      => $snapshot['wordpress'],
			'PHP'            => $snapshot['php'],
			'DB Schema'      => $snapshot['db_version'] !== '' ? $snapshot['db_version'] : '사용 안 함',
			'DB Target'      => $snapshot['db_target'] !== '' ? $snapshot['db_target'] : '사용 안 함',
			'HTTPS'          => $snapshot['https'] ? '예' : '아니오',
		);

		foreach ($snapshot['cron'] as $hook => $timestamp) {
			$rows['Cron: ' . $hook] = $timestamp ? wp_date('Y-m-d H:i:s', $timestamp) : '예약 없음';
		}

		$rows = apply_filters('nalapps_standard_status_rows', $rows, $snapshot);
		?>
		<div class="wrap nalapps-system-status">
			<h1><?php echo esc_html($this->title); ?></h1>
			<p>고객지원 및 운영 점검용 읽기 전용 상태 정보입니다. 시리얼키, API 키, 토큰, 비밀번호는 표시하지 않습니다.</p>
			<table class="widefat striped" role="table">
				<tbody>
				<?php foreach ($rows as $label => $value) : ?>
					<tr>
						<th scope="row" style="width:240px;"><?php echo esc_html((string) $label); ?></th>
						<td><?php echo esc_html(is_scalar($value) ? (string) $value : wp_json_encode($value)); ?></td>
					</tr>
				<?php endforeach; ?>
				</tbody>
			</table>
		</div>
		<?php
	}
}
