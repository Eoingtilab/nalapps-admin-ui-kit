# NalApps WordPress Plugin Standard v4

이 문서는 NalApps WordPress 플러그인의 최상위 개발 계약이다. 제품별 요구사항이 이 문서와 충돌하지 않는 한 본 표준을 기본값으로 적용한다.

## 1. 적용 원칙

- 새 플러그인은 `profiles/company-profile.json`과 제품별 `plugin-profile.json`에서 시작한다.
- canonical scaffold entrypoint는 `tools/scaffold_complete.py`다.
- 제품 특성에 따라 필요한 모듈만 활성화하되 보안, 메타데이터, public-repository safety, 품질 게이트는 항상 적용한다.
- 기존 제품 기능을 공통 표준 적용을 이유로 임의 변경하지 않는다.
- 실제로 존재하지 않는 URL, API, 제품 페이지, 지원 채널, 기능을 추측해 만들지 않는다.
- 기계적으로 검증 가능한 항목은 CI가 직접 판정하고 사람이 임의 PASS 처리하지 않는다.

## 2. 자동 적용 영역

- EOINGTI Lab / 어잉티연구소 회사 메타데이터
- WordPress plugin header, README, readme.txt, CHANGELOG, SECURITY, CONTRIBUTING
- NalApps Admin UI
- Security, capability, nonce, validation, sanitization, escaping
- Performance budget, conditional asset loading, query/cache policy
- Accessibility and admin UX
- Privacy, telemetry, diagnostics redaction
- REST/AJAX and file upload contracts
- Database schema migration and lifecycle
- Cron, concurrency lock, idempotency and retry limits
- External HTTP policy and graceful degradation
- Logging, System Status, support diagnostics
- Feature flags, import/export, backup/recovery and rollback guidance
- Namespace/prefix/conflict isolation
- Dependency and supply-chain policy
- EDD licensing and hybrid updates for paid products
- WPCS/PHPCS, PHP compatibility matrix, secret scan, package validation
- scaffold self-test and standard consistency audit
- immutable release/tag protocol and release provenance/checksum

## 3. Product Profile Resolution

`product_type`과 boolean capability 값으로 적용 모듈을 결정한다.

- `free`: EDD 모듈 제외, 나머지 공통 품질 계약 적용
- `edd_paid`: EDD store/download metadata 필수, EDD license/update/release gate 필수
- `private`: 배포 채널을 제품별로 명시하며 public-store 가정을 하지 않음
- `database=true`: DB migration 계약 필수
- `cron=true`: Cron manager와 중복 실행 방지 필수
- `rest_api=true`: REST permission/schema 계약 필수
- `external_api=true`: HTTP/cache/failure/redaction 계약 필수
- `file_upload=true`: MIME/extension/size/capability 검증 필수
- `multisite=true`: site/network option scope와 activation semantics 명시 필수
- `telemetry=opt_in`: external communication 및 명시적 사용자 동의/수집필드 문서화 필수

알 수 없는 profile field는 허용하지 않는다. `edd_paid`에서 `edd_download_id` 또는 `edd_store_url`이 없으면 profile validation은 실패해야 한다.

## 4. Standard Self-Test Contract

표준 저장소의 변경은 최소 다음 synthetic product를 자동 생성해 검증한다.

1. Free/basic
2. EDD paid + external API
3. Full-capability private plugin

Self-test는 필수 파일, 조건부 모듈, manifest, standard version, unresolved placeholder, PHP syntax를 검증한다. CI는 추가로 WPCS, dependency audit, public-repository safety, PHP matrix를 검증한다.

## 5. Release PASS 조건

Release는 다음이 모두 PASS일 때만 허용한다.

1. 제품 profile 유효
2. 회사/플러그인 메타데이터 일치
3. security/privacy/public-repository gate 통과
4. scaffold/self-test/standard audit 통과
5. PHP syntax/WPCS/support matrix 통과
6. dependency audit 통과
7. 기존 데이터 및 실제 upgrade regression 통과
8. package root/runtime dependency 검증 통과
9. version/header/readme/tag/release/store metadata 일치
10. secret/customer data 없음
11. 새 tag는 검증 이후에만 생성되고 기존 tag는 immutable

## 6. Automation vs Human Gate

자동화가 대신할 수 없는 항목은 Human Final Gate로 남긴다.

- 실제 제품 요구사항 적합성
- WordPress 관리자/프런트 UX E2E
- 실제 접근성 흐름
- 실제 구버전 → 최신버전 upgrade regression
- 실제 EDD license activation/deactivation/update E2E
- 외부 서비스 약관/개인정보 고지 적합성

`docs/ACCEPTANCE-CHECKLIST.md`가 최종 release gate다.
