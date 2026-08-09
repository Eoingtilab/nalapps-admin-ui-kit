# ISO/IEC/IEEE 29119 & ISO/IEC 25010 Quality Test Plan

## 1. Purpose

This plan defines the release-quality verification process for NalApps WordPress Plugin Standard. It uses the public process concepts of ISO/IEC/IEEE 29119 as a testing framework and ISO/IEC 25010 as the product-quality evaluation model. It is an engineering conformance aid, not an ISO certification claim.

## 2. Normative framework used

- ISO/IEC/IEEE 29119-2:2021 — test processes: governance, management and implementation of software testing.
- ISO/IEC/IEEE 29119-3:2021 — test documentation and traceable test outputs.
- ISO/IEC/IEEE 29119-4:2021 — test design techniques.
- ISO/IEC 25010:2023 — product quality model used to define quality objectives, acceptance criteria and evaluation coverage.

## 3. Test objects

1. Canonical company/profile metadata.
2. Plugin profile JSON Schema and validator.
3. Product scaffold generators and canonical CLI.
4. Generated free, EDD-paid and full-capability representative plugins.
5. EDD licensing and hybrid updater generation.
6. Security/public-repository controls.
7. WordPress compatibility and coding standards.
8. CI, immutable release and provenance workflows.
9. Documentation and cross-reference consistency.

## 4. Risk priorities

| Priority | Risk | Required response |
|---|---|---|
| P0 | Generated plugin cannot activate, corrupts data, exposes credentials, bypasses capability/license controls, or release gate can tag invalid code | Release blocked; defect fixed and regression test added |
| P1 | Updater/license integration mismatch, unsupported PHP syntax, invalid package/release, broken CI gate | Release blocked; fix before version bump |
| P2 | Maintainability, documentation drift, inefficient CI, recoverable UX/compatibility issue | Fix where practical before release; otherwise document residual risk |
| P3 | Cosmetic/documentation improvement with no functional or security impact | May be scheduled after release |

## 5. Test design techniques

The automated and manual test portfolio uses:

- equivalence partitioning for free / EDD-paid / private product types;
- boundary and invalid-input testing for slug, version, URLs and conditional profile fields;
- decision-table style testing for capability flags and conditional module selection;
- negative testing for unknown fields, invalid telemetry configuration and missing EDD metadata;
- state/transition testing for release mode, immutable tag state, license/update availability and lifecycle hooks;
- regression testing for every corrected high-risk defect;
- static analysis using PHP syntax checks, WPCS/PHPCS and WordPress Plugin Check;
- compatibility testing across supported PHP versions;
- security testing for capability/nonce contracts, secret leakage, unsafe repository files and update transport;
- package/release verification for canonical ZIP root, production dependencies, checksums and immutable tags.

## 6. ISO/IEC 25010 quality coverage

The standard evaluates all nine product-quality characteristic areas from ISO/IEC 25010:2023 at the level appropriate to a plugin-development toolkit.

| Quality area | Verification in this repository |
|---|---|
| Functional suitability | profile validation, scaffold matrix, generated module wiring, EDD regression contracts |
| Performance efficiency | bounded HTTP timeouts/cache policy, conditional asset/loading contracts, Plugin Check performance category |
| Compatibility | PHP 7.4/8.1/8.3/8.4/8.5 syntax matrix, WordPress Plugin Check runtime activation |
| Interaction capability | Admin UI/accessibility contracts, Plugin Check accessibility category, Human Final Gate |
| Reliability | fail-closed profile validation, immutable releases, retry limits, lifecycle/recovery contracts |
| Security | capability/nonce rules, secret scan, HTTPS/SSL verification, Plugin Check security category |
| Maintainability | namespace/prefix isolation, WPCS, deterministic scaffold, self-test, canonical audit, CODEOWNERS |
| Flexibility | profile-driven conditional modules, free/paid/private variants, explicit multisite/API/DB/Cron capabilities |
| Safety | destructive-action safeguards, preserve-by-default uninstall policy, fail-closed release and migration contracts |

## 7. Automated test suite

The primary CI must execute:

1. `tools/standard_audit.py`
2. `tools/self_test.py`
3. `tools/quality_contract_test.py`
4. `tools/public_repo_guard.sh`
5. official WordPress Plugin Check on representative generated plugins
6. Composer dependency audit
7. PHP syntax checks
8. WordPress Coding Standards / PHPCS
9. supported PHP compatibility matrix
10. release provenance/hash smoke test

The free and EDD-paid official Plugin Check executions are isolated into separate workflow runs where needed because the upstream action uploads a fixed artifact name.

## 8. Human Final Gate

Automation does not certify business correctness. Before a generated product release, a human must still verify where applicable:

- real WordPress admin/front-end UX and responsive behavior;
- actual feature requirements and content semantics;
- accessibility flow with keyboard/focus/screen-reader considerations;
- real previous-version to new-version upgrade with preserved data;
- real EDD license activate/deactivate/expire/revoke and update E2E;
- external-service terms/privacy disclosures;
- destructive actions, backup/recovery and rollback behavior.

## 9. Entry criteria

- all intended source/document changes are committed;
- `VERSION` has not yet been bumped for the target release;
- no known P0/P1 defect remains intentionally open;
- test fixtures use synthetic/non-secret data.

## 10. Exit criteria

A standard release may be tagged only when:

- all mandatory automated gates pass;
- every discovered P0/P1 defect is fixed and regression-covered;
- P2/P3 residual risks are documented;
- Human Final Gate items applicable to the release are completed or explicitly identified as product-specific follow-up;
- version bump is the final release change;
- the immutable tag is created only after validation.

## 11. Defect recording

Each defect report records: identifier, source/test case, severity, affected quality area, root cause, corrective change, commit/reference, regression coverage and retest result. Final execution evidence is recorded in `docs/ISO-29119-25010-TEST-REPORT.md`.
