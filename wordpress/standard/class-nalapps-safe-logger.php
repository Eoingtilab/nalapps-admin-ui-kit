<?php
/**
 * NalApps privacy-safe bounded logger template.
 *
 * Logging is opt-in. Secret-looking keys are redacted recursively. The logger
 * stores a bounded ring buffer in a non-autoloaded option; product plugins may
 * replace storage while preserving the same redaction/retention contract.
 */
namespace NalApps\Standard;

if (!defined('ABSPATH')) {
	exit;
}

final class Safe_Logger {
	private $option_name;
	private $enabled_option;
	private $max_entries;

	public function __construct($option_name, $enabled_option, $max_entries = 100) {
		$this->option_name = sanitize_key($option_name);
		$this->enabled_option = sanitize_key($enabled_option);
		$this->max_entries = max(10, min(500, absint($max_entries)));
	}

	public function log($level, $message, array $context = array()) {
		if (!get_option($this->enabled_option, false)) {
			return;
		}

		$entries = get_option($this->option_name, array());
		if (!is_array($entries)) {
			$entries = array();
		}

		$entries[] = array(
			'time'    => current_time('mysql', true),
			'level'   => sanitize_key($level),
			'message' => sanitize_text_field((string) $message),
			'context' => $this->redact($context),
		);
		$entries = array_slice($entries, -$this->max_entries);
		update_option($this->option_name, $entries, false);
	}

	public function clear() {
		delete_option($this->option_name);
	}

	public function get_entries() {
		$entries = get_option($this->option_name, array());
		return is_array($entries) ? $entries : array();
	}

	private function redact($value, $key = '') {
		$secret_patterns = array('password', 'passwd', 'secret', 'token', 'api_key', 'apikey', 'license', 'serial', 'authorization', 'cookie');
		$key_lc = strtolower((string) $key);
		foreach ($secret_patterns as $pattern) {
			if ($key_lc !== '' && strpos($key_lc, $pattern) !== false) {
				return '[REDACTED]';
			}
		}

		if (is_array($value)) {
			$out = array();
			foreach ($value as $child_key => $child_value) {
				$out[$child_key] = $this->redact($child_value, $child_key);
			}
			return $out;
		}
		if (is_object($value)) {
			return $this->redact((array) $value, $key);
		}
		if (is_bool($value) || is_int($value) || is_float($value) || $value === null) {
			return $value;
		}

		$text = sanitize_text_field((string) $value);
		return strlen($text) > 1000 ? substr($text, 0, 1000) . '…' : $text;
	}
}
