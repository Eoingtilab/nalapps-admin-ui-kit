# NalApps Runtime, License, and Release Safety Contract

This contract is mandatory for NalApps WordPress plugins.

## 1. Public runtime and license entitlement are separate

A missing, inactive, expired, malformed, or temporarily unreachable license must not disable or hide already configured public frontend behavior.

License state may control update entitlement, explicitly licensed premium capabilities, and administrator license-management UX. It must not be used as a blanket frontend runtime gate.

License API timeout, HTTP failure, or invalid cached license data must degrade only license/update status. Public runtime must remain available from local saved configuration.

## 2. Context-aware WordPress output escaping

Use escaping that matches the output context:

- plain text: `esc_html()`
- attributes: `esc_attr()`
- URLs: `esc_url()`
- textarea text: `esc_textarea()`
- intentionally allowed markup: `wp_kses()` or `wp_kses_post()` with the narrowest practical allowlist
- WordPress-generated media markup: prefer structural WordPress APIs such as `wp_get_attachment_image()`

Do not apply `esc_html()` to markup merely to silence Plugin Check or PHPCS; that converts valid markup into visible text and is a functional regression. Do not use blanket PHPCS ignores as a substitute for correct output handling.

## 3. Current-HEAD release hard gate

A release may be tagged or packaged only from the exact release HEAD after all required checks for that HEAD succeed. Historical green runs do not satisfy this gate.

Required evidence includes WordPress Plugin Check, NalApps quality gate/regression checks, and production package verification.

Quality controls must not be weakened to obtain green status. Disabling workflows, excluding failing production files, hardcoding success, suppressing warnings, or adding blanket ignores is prohibited.

## 4. Production ZIP gate

The release ZIP must contain one installable top-level plugin directory with the main plugin file and required production/runtime dependencies. The plugin version inside the package must match the release version.

Development-only material such as `.git`, `.github`, tests, `node_modules`, temporary files, CI artifacts, IDE files, and source-only debris must not be shipped unless explicitly required at runtime.

## 5. Data retention safety

Default behavior:

- deactivation: retain user data
- uninstall: retain user data
- destructive cleanup: only after explicit user opt-in

Destructive cleanup must fail safe when explicit intent cannot be proven.

## 6. Regression contract

Every NalApps plugin release review must cover at least:

1. activation
2. deactivation
3. administrator settings save
4. public runtime
5. public runtime with missing license
6. public runtime with inactive/expired/unreachable license
7. update entitlement behavior
8. uninstall retention
9. explicit cleanup opt-in
10. WordPress Plugin Check
11. NalApps Quality Gate
12. production package verification

The standard quality contract includes a generated paid-plugin regression that rejects a public main runtime which returns early based on license/serial state. WordPress Coding Standards and Plugin Check remain the automated output-escaping enforcement layer, while package/release tooling remains responsible for installable artifact verification.
