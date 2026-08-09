# NalApps WordPress Plugin Standard v3

EOINGTI Lab / 어잉티연구소의 WordPress 플러그인 공통 개발 표준입니다. 관리자 UI만이 아니라 **메타데이터, 보안, 성능, 접근성, 개인정보, 라이선스, 업데이트, 진단, 테스트, CI, 릴리스**까지 한 번에 적용하는 기준 저장소입니다.

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
- Uninstall data policy: 기본 보존

Machine-readable source: `profiles/company-profile.json`

## 한 줄 적용 지시

> `Eoingtilab/nalapps-wordpress-plugin-standard`의 최신 안정 태그 기준으로 NalApps WordPress Plugin Standard 전체를 적용한다. 제품별 `plugin-profile.json`만 정의하고 나머지 회사 메타데이터, Admin UI, 보안, 성능, 접근성, 개인정보, REST/AJAX, 파일 업로드, DB migration, Cron, 동시실행 방지, logging, System Status, lifecycle, EDD 라이선스/업데이트, CI, 테스트, 릴리스 및 public-repository safety gate는 표준에 따라 자동 적용한다. 실제 존재하지 않는 URL이나 기능은 만들지 않는다.

## 제품별 최소 입력

제품마다 가능한 한 `profiles/plugin-profile.schema.json`에 맞는 profile만 작성합니다.

```json
{
  "plugin_name": "Example NalApps Plugin",
  "slug": "example-nalapps-plugin",
  "product_type": "free",
  "frontend": true,
  "database": false,
  "cron": false,
  "rest_api": false,
  "external_api": false,
  "file_upload": false,
  "multisite": false,
  "telemetry": "off",
  "edd_download_id": null,
  "plugin_uri": null,
  "support_uri": null,
  "requires_plugins": []
}
```

## 표준 계층

### Admin UI
Pretendard Variable, NalApps Blue/Navy/Soft Blue/Neutral Gray 디자인 토큰, WordPress 전용 Adapter, Dashboard/List/Add/Edit/Settings UX, 화면 범위 CSS/JS 격리를 적용합니다.

### Security & Runtime
Capability + nonce, validation/sanitization/escaping, SQL 안전성, namespace/prefix isolation, compatibility guard, lifecycle, DB migration, Cron, bounded logging, read-only System Status를 적용합니다.

### Engineering v3
성능 budget, conditional asset loading, accessibility, privacy, telemetry opt-in, REST/AJAX, file upload validation, concurrency/idempotency, feature flags, backup/recovery, import/export, capability matrix, deprecated API, dependency/supply-chain, graceful failure를 적용합니다.

### EDD Paid Products
EDD Software Licensing SDK, WordPress 플러그인 페이지 기본 업데이트 알림, 플러그인 내부 업데이트 화면, 라이선스 상태, `get_version`, production `vendor/` 포함 Release ZIP을 적용합니다.

### Public Repository Safety
EDD/API/GitHub/WordPress/SSH/DB 자격증명, `.env` 실제 값, 고객 DB/백업/개인정보, 비공개 webhook/production dump는 공개 저장소에 커밋하지 않습니다. 예제는 placeholder만 사용합니다.

### Testing / CI / Release
PHP syntax/static checks, WPCS/PHPCS 적용 가능성, unit/integration/admin E2E, capability/nonce tests, migration idempotency, secret scan, WordPress/PHP matrix, package root/vendor 검증, version consistency와 실제 upgrade regression을 release gate로 둡니다.

## 핵심 문서

- `docs/MASTER-STANDARD.md` — 최상위 개발 계약
- `docs/COMPANY-PROFILE.md` — EOINGTI Lab canonical metadata
- `docs/PLUGIN-METADATA-STANDARD.md` — Header/README/readme/GitHub 규칙
- `docs/WORDPRESS-PLUGIN-STANDARD.md` — 운영·보안·DB·Cron·진단 표준
- `docs/ENGINEERING-CONTRACTS-V3.md` — 성능·접근성·privacy·REST·동시성·복구·공급망
- `docs/PUBLIC-REPOSITORY-SAFETY.md` — 공개 저장소 안전 게이트
- `docs/EDD-LICENSE-AND-UPDATES.md` — 유료 제품 라이선스/업데이트
- `docs/ACCEPTANCE-CHECKLIST.md` — 최종 PASS gate

## 저장소 구조

```text
profiles/              회사/제품 profile 및 schema
assets/                Admin UI assets
wordpress/             Admin UI, standard, EDD 재사용 코드
docs/                  개발/운영/보안/release 계약
templates/             신규 플러그인/GitHub/CI 템플릿
VERSION                 안정 표준 버전
```

## Release 원칙

표준 또는 제품 release는 **모든 코드/문서/테스트 변경을 먼저 완료하고 VERSION 또는 제품 버전 bump를 마지막 커밋으로 수행**합니다. Tag가 불완전한 중간 상태를 가리키면 안 됩니다.

## Version Policy

- `3.x`: NalApps WordPress Plugin Standard 전체 개발 체계
- 파괴적 계약 변경: major
- 새 공통 모듈/계약: minor
- 문서/CSS/호환성 수정: patch
