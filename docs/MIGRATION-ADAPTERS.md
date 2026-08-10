# NalApps WordPress Plugin Migration Adapters

## Purpose

Existing WordPress products must not be converted by copying the standalone Golden Reference blindly. The migration layer classifies each repository first, selects a compatible adapter, and fails closed when ownership of licensing, updates, backup, data, credentials, or server-side control planes is unclear.

Golden Reference: `Eoingtilab/eo-korean-slide-popup` latest stable release.

## Adapter families

### `standalone`
For independent WordPress plugins that own their own lifecycle.

Common target contract:
- NalApps Admin UI
- License
- Update Center
- Backup & Restore
- System Information
- verified GitHub Release rollback
- activation-state preservation
- EDD product mapping when `edd_paid`

The adapter must preserve the existing plugin slug, plugin basename, namespace/prefix, options, post types, custom tables, APIs and frontend behavior.

### `commerce_family`
For `nalapps-commerce-core` and Core-dependent add-ons.

The Core is the lifecycle control plane. Add-ons must not gain a second independent updater/license controller unless explicitly approved. Common UI may be adopted, but licensing, update, rollback and credential behavior must delegate to or remain compatible with Commerce Core.

Roles:
- `core`
- `addon`

### `specialized`
For server bridges, security/privacy products, credential-sensitive plugins, or products with an established signed updater/control plane.

Roles include:
- `server_bridge`
- `security`
- `credential_sensitive`
- `data_sensitive`

Common UI can be adopted where safe, but updater/license/backup contracts are opt-in only after product-specific review. Existing signature verification, encrypted credential storage and server-side authority must not be replaced by a generic standalone implementation.

## Mandatory fail-closed inputs

A migration is not executable until these are known:
- repository and WordPress plugin identity
- plugin slug and main plugin file
- current version
- architecture family and role
- existing updater/license control plane ownership
- data contract
- secret/credential-sensitive storage
- EDD mapping when applicable
- release asset naming contract
- uninstall policy

Unknown required fields produce `blocked` rather than inferred values.

## Migration stages

1. Inventory only — read-only inspection.
2. Classification — choose adapter family/role.
3. Contract plan — list preserved ownership and allowed mutation scope.
4. Repository branch — never modify main directly.
5. Adapter implementation — minimal changes only.
6. Product QA — existing feature regression + Standard gates.
7. PR and CI.
8. Merge only after all required checks pass.
9. Immutable tag/release/ZIP/SHA256.
10. EDD mapping and external update E2E where applicable.

A failure in one repository must not stop independent repositories, and must not weaken its safety contract to obtain a pass.

## Organization-wide command model

`tools/migration_plan.py` consumes an explicit inventory JSON and generates a deterministic plan. It is read-only: it does not edit repositories, create tags, publish releases, call EDD, or modify customer data.

Example:

`python tools/migration_plan.py profiles/example-migration-inventory.json`

The generated plan identifies:
- adapter family/role
- automatic vs review-required migration status
- preserved control plane
- prohibited changes
- required preconditions

Actual repository migration remains a separate branch/QA/PR operation.

## Golden Reference boundaries

EO Korean Slide Popup defines the canonical standalone UI and commercial lifecycle UX. It is not a source-code template for Commerce Core, add-ons, server bridges, security products, or credential-sensitive products.

Golden Reference behavior to share when compatible:
- canonical NalApps Admin UI/CSS
- License / Update / Backup & Restore / System Information information architecture
- no duplicate page titles/actions
- no internal admin nav scrollbar
- consistent 40px controls and responsive layout
- updater package verification
- update/rollback activation preservation
- rollback centralized in Backup & Restore
- secret-redacted System Information

Product-specific business logic remains owned by each repository.