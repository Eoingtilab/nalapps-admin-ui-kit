<?php
/**
 * NalApps WordPress Plugin Standard bootstrap example.
 * Replace namespace, constants, option names, menu slugs and migrations.
 */

use NalApps\Standard\Cron_Manager;
use NalApps\Standard\DB_Migrator;
use NalApps\Standard\Plugin_Standard;
use NalApps\Standard\Safe_Logger;
use NalApps\Standard\System_Status;

require_once __DIR__ . '/class-nalapps-plugin-standard.php';
require_once __DIR__ . '/class-nalapps-db-migrator.php';
require_once __DIR__ . '/class-nalapps-cron-manager.php';
require_once __DIR__ . '/class-nalapps-safe-logger.php';
require_once __DIR__ . '/class-nalapps-system-status.php';

$nalapps_standard = new Plugin_Standard(array(
	'plugin_file'       => REPLACE_PLUGIN_FILE,
	'plugin_version'    => REPLACE_PLUGIN_VERSION,
	'min_wp'            => '6.0',
	'min_php'           => '7.4',
	'db_version_option' => 'replace_plugin_db_version',
	'db_version'        => '1.0.0',
	'cron_hooks'        => array('replace_plugin_cron'),
));
$nalapps_standard->register();

$nalapps_logger = new Safe_Logger(
	'replace_plugin_logs',
	'replace_plugin_debug_logging',
	100
);

$nalapps_cron = new Cron_Manager(array(
	'replace_plugin_cron' => 'hourly',
));

$nalapps_migrator = new DB_Migrator(
	'replace_plugin_db_version',
	'1.0.0',
	array(
		'1.0.0' => function () {
			// Create/update only plugin-owned schema. Must be idempotent.
			return true;
		},
	)
);

add_action('plugins_loaded', function () use ($nalapps_migrator) {
	$result = $nalapps_migrator->maybe_migrate();
	if (is_wp_error($result)) {
		// Product plugin should fail closed for features that depend on the schema.
		return;
	}
});

register_activation_hook(REPLACE_PLUGIN_FILE, function () use ($nalapps_cron, $nalapps_migrator) {
	$result = $nalapps_migrator->maybe_migrate();
	if (!is_wp_error($result)) {
		$nalapps_cron->ensure_scheduled();
	}
});

register_deactivation_hook(REPLACE_PLUGIN_FILE, function () use ($nalapps_cron) {
	$nalapps_cron->unschedule_all();
});

$nalapps_status = new System_Status(
	'replace-plugin-menu',
	'replace-plugin-system-status',
	'시스템 상태',
	$nalapps_standard
);
$nalapps_status->register();
