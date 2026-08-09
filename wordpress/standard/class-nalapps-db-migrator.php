<?php
/**
 * NalApps deterministic DB migration template.
 *
 * Migrations are explicit, ordered and forward-only. Each callback must be
 * idempotent and must return true on success or WP_Error on failure.
 */
namespace NalApps\Standard;

if (!defined('ABSPATH')) {
	exit;
}

final class DB_Migrator {
	private $option_name;
	private $target_version;
	private $migrations;

	public function __construct($option_name, $target_version, array $migrations) {
		$this->option_name = sanitize_key($option_name);
		$this->target_version = (string) $target_version;
		$this->migrations = $migrations;
	}

	public function maybe_migrate() {
		$current = (string) get_option($this->option_name, '0');
		if ($current !== '0' && version_compare($current, $this->target_version, '>')) {
			return new \WP_Error('nalapps_db_downgrade_blocked', 'DB schema downgrade는 자동 실행하지 않습니다.');
		}
		if (version_compare($current, $this->target_version, '>=')) {
			return true;
		}

		uksort($this->migrations, 'version_compare');
		foreach ($this->migrations as $version => $callback) {
			$version = (string) $version;
			if (version_compare($version, $current, '<=')) {
				continue;
			}
			if (version_compare($version, $this->target_version, '>')) {
				break;
			}
			if (!is_callable($callback)) {
				return new \WP_Error('nalapps_db_migration_not_callable', 'DB migration callback이 유효하지 않습니다.', array('version' => $version));
			}

			$result = call_user_func($callback);
			if (is_wp_error($result)) {
				return $result;
			}
			if ($result !== true) {
				return new \WP_Error('nalapps_db_migration_failed', 'DB migration이 성공 상태를 반환하지 않았습니다.', array('version' => $version));
			}

			update_option($this->option_name, $version, false);
			$current = $version;
		}

		return version_compare($current, $this->target_version, '>=')
			? true
			: new \WP_Error('nalapps_db_target_not_reached', '목표 DB schema version에 도달하지 못했습니다.');
	}
}
