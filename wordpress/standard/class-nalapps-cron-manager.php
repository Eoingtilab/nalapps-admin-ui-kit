<?php
/**
 * NalApps Cron Manager template.
 */
namespace NalApps\Standard;

if (!defined('ABSPATH')) {
	exit;
}

final class Cron_Manager {
	private $hooks;

	/**
	 * @param array $hooks hook => recurrence, e.g. array('my_plugin_sync' => 'hourly').
	 */
	public function __construct(array $hooks) {
		$this->hooks = $hooks;
	}

	public function ensure_scheduled() {
		foreach ($this->hooks as $hook => $recurrence) {
			$hook = sanitize_key($hook);
			$recurrence = sanitize_key($recurrence);
			if (!$hook || !$recurrence || !wp_get_schedule($hook)) {
				if ($hook && $recurrence && !wp_next_scheduled($hook)) {
					wp_schedule_event(time() + MINUTE_IN_SECONDS, $recurrence, $hook);
				}
			}
		}
	}

	public function unschedule_all() {
		Plugin_Standard::unschedule_hooks(array_keys($this->hooks));
	}

	public function get_status() {
		$status = array();
		foreach ($this->hooks as $hook => $recurrence) {
			$hook = sanitize_key($hook);
			if (!$hook) {
				continue;
			}
			$status[$hook] = array(
				'recurrence' => wp_get_schedule($hook) ?: sanitize_key($recurrence),
				'next_run'   => wp_next_scheduled($hook) ?: false,
			);
		}
		return $status;
	}
}
