# NalApps WordPress Plugin Standard v4

EOINGTI Lab / 어잉티연구소의 WordPress 플러그인 공통 개발·배포 표준입니다. v4는 **Plugin Profile → Product Scaffold → Runtime Safety → CI Enforcement → Immutable Release Gate**까지 자동화합니다.

## Canonical Company Profile

별도 지시가 없으면 모든 NalApps 플러그인은 다음 값을 상속합니다.

- Developer: `EOINGTI Lab / 어잉티연구소`
- Author: `EOINGTI Lab`
- Developer / Author URI: `https://eoingti.com/`
- GitHub: `https://github.com/Eoingtilab`
- Repository: `https://github.com/Eoingtilab/<plugin-slug>`
- Plugin URI: 실제 제품 페이지가 있으면 그 URL, 없으면 `https://eoingti.com/`
- Public repository: 기본 허용, 단 secret/customer data 금지
- Telemetry: 기본 OFF
- Uninstall data policy: 기본 `preserve`

Machine-readable source: `profiles/company-profile.json`

## 한 줄 적용 지시

> `Eoingtilab/nalapps-wordpress-plugin-standard`의 최신 안정 태그 기준으로 전체 표준을 적용한다. 제품별 `plugin-profile.json`을 정의하고 회사 메타데이터, Admin UI, 보안, 성능, 접근성, 개인정보, REST/AJAX, 파일 업로드, DB migration, Cron, 동시실행 방지, logging, System Status, rollback, data backup/import/export, safe uninstall, system information, lifecycle, EDD 라이선스/업데이트, WPCS, CI, 테스트, immutable release 및 public-repository safety gate를 표준에 따라 적용한다. 실제 존재하지 않는 URL이나 기능은 만들지 않는다.

## 완성형 Product Scaffold

Canonical CLI:

```bash
python tools/nalapps_plugin.py create \
  --profile profiles/example-free.plugin-profile.json \
  --output build/scaffold \
  --clean
```

생성 결과에는 main plugin, 고유 namespace/prefix, System Status, Maintenance, `plugin-profile.json`, `nalapps-standard-manifest.json`, README/readme/SECURITY/CONTRIBUTING, Composer/WPCS 설정, GitHub quality workflow, immutable release workflow, release acceptance checklist가 포함됩니다.

Profile 플래그에 따라 DB migration, Cron, REST, external HTTP, file upload가 조건부 선택됩니다. `edd_paid` 제품은 추가로 EDD SDK runtime dependency, SDK registry/loader, license state adapter, WordPress 기본 updater, 내부 Updates 화면 및 production `vendor/` release contract까지 자동 생성됩니다.

## Plugin Profile

Schema: `profiles/plugin-profile.schema.json`

예제:

- `profiles/example-free.plugin-profile.json`
- `profiles/example-edd-paid.plugin-profile.json`

`edd_paid` 제품은 `edd_download_id`와 `edd_store_url`을 필수로 요구하며 알 수 없는 profile 필드는 fail-closed 처리합니다. 새 프로젝트의 `release_mode` 기본값은 `manual`입니다.

제품 데이터는 선택적으로 `data_contract`에 자신이 실제 소유하는 데이터만 선언합니다.

```json
{
  "uninstall_policy": "preserve",
  "data_contract": {
    "options": ["my_plugin_settings"],
    "site_options": [],
    "post_types": ["my_plugin_item"],
    "custom_tables": ["my_plugin_records"]
  }
}
```

password/secret/token/API key/license key 성격의 option은 자동 백업 대상 선언이 거부됩니다.

## 표준 계층

### Admin UI
Pretendard Variable, NalApps Blue/Navy/Soft Blue/Neutral Gray 디자인 토큰, WordPress 전용 Adapter, Dashboard/List/Add/Edit/Settings UX, 화면 범위 CSS/JS 격리를 적용합니다.

### Security & Runtime
Capability + nonce, validation/sanitization/escaping, SQL 안전성, namespace/prefix isolation, compatibility guard, lifecycle, DB migration, Cron, bounded logging, read-only System Status를 적용합니다.

### Rollback / Backup / Data Lifecycle
모든 생성 제품에 공통으로 다음을 포함합니다.

- 자기 플러그인 업데이트 직전 **코드 ZIP 자동 백업**
- 백업 실패 시 업데이트 fail-closed
- 최근 코드 백업 3개 유지 및 관리자 수동 롤백
- 롤백 직전 현재 코드/데이터 재백업
- portable JSON **데이터 내보내기/가져오기**
- import 직전 데이터 snapshot 자동 생성, 최근 5개 유지
- uninstall 기본 `preserve`
- 관리자가 명시적으로 `delete_all`을 선택한 경우에만 선언된 플러그인 데이터 완전 삭제
- Maintenance 화면과 WordPress Site Health에 **민감정보가 제거된 시스템 정보** 제공

코드 롤백은 DB migration을 자동 역변환하지 않습니다. 데이터/스키마 복원이 필요하면 별도 snapshot/import와 제품별 migration E2E를 사용합니다. 세부 계약은 `docs/ROLLBACK-BACKUP-DATA-LIFECYCLE.md`를 따릅니다.

### Engineering
성능 budget, conditional asset loading, accessibility, privacy, telemetry opt-in, REST/AJAX, file upload validation, concurrency/idempotency, feature flags, backup/recovery, import/export, capability matrix, deprecated API, dependency/supply-chain, graceful failure를 적용합니다.

### EDD Paid Products
EDD Software Licensing SDK, WordPress Plugins 화면 업데이트 알림, 플러그인 내부 Updates 화면, license state adapter, production dependency를 포함한 Release Asset, 실제 라이선스/업데이트 E2E를 제품 release gate로 둡니다. 제품 기능 자체를 라이선스로 잠글지는 제품 요구사항에 따라 명시적으로 결정합니다.

### Public Repository Safety
EDD/API/GitHub/WordPress/SSH/DB 자격증명, 실제 `.env`, 고객 DB/백업/개인정보, private key/certificate, 비공개 webhook/production dump는 공개 저장소에 커밋하지 않습니다. `tools/public_repo_guard.sh`가 기계적으로 검사합니다.

### Testing / CI / Release
`.github/workflows/quality-gate.yml`이 다음을 자동 실행합니다.

- canonical standard audit
- JSON Schema / profile 검증
- free / EDD paid / full-capability product scaffold self-test
- rollback/data portability/safe uninstall/system info scaffold 계약 검증
- 민감 backup option negative test
- EDD paid SDK/updater wiring 검증
- public repository safety scan
- Composer dependency audit
- PHP syntax
- WordPress Coding Standards / PHPCS
- PHP 7.4 / 8.1 / 8.3 / 8.4 / 8.5 syntax matrix
- WordPress Plugin Check
- release provenance/hash generator smoke test

실제 제품의 UI/EDD/live API/data round-trip/upgrade/rollback은 `docs/ACCEPTANCE-CHECKLIST.md`의 Human Final Gate에서 검증합니다.

## Immutable Release Protocol

표준과 제품 모두 **기능/문서/테스트 변경을 먼저 완료하고 버전 bump를 마지막 커밋으로 수행**합니다.

표준의 `.github/workflows/tag-version.yml`은 새 VERSION을 발견해도 self-test, security, dependency, PHP syntax, WPCS gate를 통과한 뒤에만 `v{VERSION}`을 생성하며 기존 tag를 이동하거나 덮어쓰지 않습니다.

Product release workflow도 기존 tag/release를 immutable로 취급하고 ZIP root/체크섬을 확인한 뒤 새 tag/release를 생성합니다. Runtime Composer dependency가 있으면 `vendor/`를 distribution에 포함합니다.

## 핵심 문서

- `docs/MASTER-STANDARD.md` — 최상위 개발 계약
- `docs/COMPANY-PROFILE.md` — EOINGTI Lab canonical metadata
- `docs/PLUGIN-METADATA-STANDARD.md` — Header/README/readme/GitHub 규칙
- `docs/WORDPRESS-PLUGIN-STANDARD.md` — 운영·보안·DB·Cron·진단 표준
- `docs/ENGINEERING-CONTRACTS-V3.md` — 성능·접근성·privacy·REST·동시성·복구·공급망 기본 계약
- `docs/AUTOMATION-AND-SCAFFOLDING.md` — 자동 생성·Self-Test·CI enforcement
- `docs/ROLLBACK-BACKUP-DATA-LIFECYCLE.md` — rollback/data portability/uninstall/system info
- `docs/PUBLIC-REPOSITORY-SAFETY.md` — 공개 저장소 안전 게이트
- `docs/EDD-LICENSE-AND-UPDATES.md` — 유료 제품 라이선스/업데이트
- `docs/ACCEPTANCE-CHECKLIST.md` — Automated + Human Final PASS gate

## 저장소 구조

```text
profiles/              회사/제품 profile, schema, examples
assets/                NalApps Admin UI assets
wordpress/             Admin UI, standard, 재사용 코드
tools/                 validator, scaffold, maintenance runtime, self-test, audit, provenance
docs/                  개발/운영/보안/rollback/release 계약
templates/             추가 GitHub/CI 템플릿
.github/workflows/      standard self-test 및 validated tag workflow
VERSION                 안정 표준 버전
```

## Version Policy

- `4.x`: 자동 생성 + 자동 검증 + 공통 maintenance runtime + EDD paid runtime + immutable release
- 파괴적 계약 변경: major
- 새 공통 모듈/자동화 계약: minor
- 문서/CSS/호환성 수정: patch
