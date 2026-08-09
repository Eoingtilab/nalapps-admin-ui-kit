<?php
/**
 * NalApps WordPress Plugin Standard core template.
 *
 * Copy this file into a product plugin and change namespace/config values.
 * Business logic must remain in the product plugin; this class only provides
 * reusable operational safeguards and status helpers.
 */
namespace NalApps\Standard;

if (!defined('ABSPATH')) {
	exit;
}

final class Plugin_Standard {
	private $config;

	public function __construct(array $config) {
		$defaults = array(
			'plugin_file'       => '',
			'plugin_version'    => '',
			'min_wp'            => '6.0',
			'min_php'           => '7.4',
			'db_version_option' => '',
			'db_version'        => '',
			'cron_hooks'        => array(),
		);
		$this->config = wp_parse_args($config, $defaults);
	}

	public function register() {
		add_action('admin_init', array($this, 'check_compatibility'));
	}

	public function check_compatibility() {
		if (!current_user_can('activate_plugins')) {
			return;
		}

		$problems = array();
		global $wp_version;

		if ($this->config['min_wp'] && version_compare((string) $wp_version, (string) $this->config['min_wp'], '<')) {
			$problems[] = sprintf('WordPress %s 이상이 필요합니다.', $this->config['min_wp']);
		}
		if ($this->config['min_php'] && version_compare(PHP_VERSION, (string) $this->config['min_php'], '<')) {
			$problems[] = sprintf('PHP %s 이상이 필요합니다.', $this->config['min_php']);
		}

		if ($problems) {
			add_action('admin_notices', function () use ($problems) {
				echo '<div class="notice notice-error"><p><strong>NalApps Plugin Compatibility:</strong> ';
				echo esc_html(implode(' ', $problems));
				echo '</p></div>';
			});
		}
	}

	public function get_status_snapshot() {
		global $wp_version;
		$db_version = '';
		if ($this->config['db_version_option']) {
			$db_version = (string) get_option($this->config['db_version_option'], '');
		}

		$cron = array();
		foreach ((array) $this->config['cron_hooks'] as $hook) {
			$hook = sanitize_key($hook);
			if (!$hook) {
				continue;
			}
			$cron[$hook] = wp_next_scheduled($hook);
		}

		return array(
			'plugin_version' => (string) $this->config['plugin_version'],
			'wordpress'      => (string) $wp_version,
			'php'            => PHP_VERSION,
			'db_version'     => $db_version,
			'db_target'      => (string) $this->config['db_version'],
			'https'          => is_ssl(),
			'cron'           => $cron,
		);
	}

	public static function verify_admin_action($capability, $nonce_action, $nonce_field = '_wpnonce') {
		if (!current_user_can($capability)) {
			wp_die(esc_html__('권한이 없습니다.', 'nalapps'));
		}
		check_admin_referer($nonce_action, $nonce_field);
	}

	public static function unschedule_hooks(array $hooks) {
		foreach ($hooks as $hook) {
			$hook = sanitize_key($hook);
			if (!$hook) {
				continue;
			}
			$timestamp = wp_next_scheduled($hook);
			while ($timestamp) {
				wp_unschedule_event($timestamp, $hook);
				$timestamp = wp_next_scheduled($hook);
			}
		}
	}
}
