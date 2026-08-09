# Engineering Contracts v3

## Performance
- Admin/front assets are loaded only on required screens/pages.
- Avoid unbounded queries and N+1 patterns; paginate large datasets.
- Cache repeated remote/expensive reads with explicit TTL and invalidation.
- Do not perform remote calls on every page view when cached data is sufficient.

## Accessibility & Admin UX
- Keyboard navigation, visible focus, labels, semantic controls and sufficient contrast are required.
- Destructive actions require explicit confirmation and appropriate capability/nonce checks.
- Admin notices must be actionable, scoped and dismissible when non-critical.
- Long operations expose progress/working state and prevent duplicate submission.

## REST / AJAX
- REST routes require `permission_callback` and schema/argument validation.
- AJAX mutations require capability + nonce.
- Return consistent success/error payloads; do not expose stack traces/secrets.

## File Uploads
- Validate capability, nonce, extension, MIME, size and expected content type.
- Prefer WordPress media/filesystem APIs.
- Never trust client MIME alone and never execute uploaded content.

## Concurrency / Idempotency
- Expensive or external mutations use lock/idempotency protection.
- Duplicate clicks, retries and cron overlap must not create duplicate records/orders/posts.
- Locks have bounded expiry and safe recovery.

## Feature Flags
- Experimental features default OFF unless a product profile explicitly enables them.
- A feature flag must not bypass security, licensing or release gates.

## Backup / Recovery / Import / Export
- Settings exports include schema/version metadata and no secrets by default.
- Imports validate schema and reject unknown/unsafe fields.
- Migration/import failure must not partially mark success.
- Destructive migrations require an explicit recovery/backup plan.

## Capability Matrix
- Use the minimum capability for each action rather than defaulting all actions to `manage_options`.
- View, edit, publish, delete, update, diagnostic and license actions may use different capabilities.

## Conflict Isolation
- Namespaces, classes, functions, options, transients, cron hooks, REST namespaces and DB tables use canonical plugin prefixes.
- No global CSS/JS leakage outside plugin surfaces.
- Never replace or monkey-patch WordPress core functions.

## Deprecated APIs
- Public/internal contracts in released products receive a documented deprecation path before removal when feasible.
- Migrations preserve backward compatibility long enough for supported upgrade paths.

## Dependencies / Supply Chain
- Production dependencies are declared and version constrained.
- Lock files are committed when the build uses them.
- Dev dependencies are excluded from distribution ZIPs unless runtime-required.
- Release packages are built from trusted CI, not from arbitrary local vendor folders.

## Privacy / Telemetry
- Telemetry default is OFF.
- Analytics/error reporting requires explicit opt-in and documented data fields/endpoints.
- Collect the minimum data required; redact site secrets and personal data.

## License-server failure
- License/update-server outages must not cause WordPress fatal errors.
- Cached valid state and product-specific grace behavior must be explicit; security-sensitive features may fail closed.
- Never silently convert server/network failure into a permanent license revocation.
