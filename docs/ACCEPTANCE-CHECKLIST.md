# NalApps WordPress Plugin Standard v3 Acceptance Gate

모든 해당 항목이 PASS여야 release 완료로 판단합니다. 제품 profile에서 사용하지 않는 기능만 N/A 처리할 수 있습니다.

## Company / Metadata
- [ ] `plugin-profile.json`이 schema에 맞고 실제 제품 특성과 일치한다.
- [ ] Author=`EOINGTI Lab`, Author URI=`https://eoingti.com/` 기본값이 유지된다.
- [ ] GitHub owner=`Eoingtilab`, repository=`Eoingtilab/<plugin-slug>` 규칙을 따른다.
- [ ] Plugin URI는 실제 제품 페이지 또는 `https://eoingti.com/`이며 가짜 URL이 없다.
- [ ] README/readme.txt에 개발사, 홈페이지, source, 요구환경, 설치, 사용, 지원, privacy, license, changelog가 필요한 범위에서 포함된다.
- [ ] Version / Stable tag / Git tag / Release / EDD version이 출시 시 일치한다.

## Public Repository Safety
- [ ] EDD/API/GitHub/WordPress/SSH/DB secret이 없다.
- [ ] 실제 `.env`, private key/certificate, DB/backup dump가 없다.
- [ ] 고객 이메일/전화번호/주문/DB/비공개 계약자료가 없다.
- [ ] fixture/example은 placeholder 또는 synthetic data만 사용한다.
- [ ] release ZIP도 별도 secret/customer-data scan을 통과한다.

## Admin UI / Accessibility / UX
- [ ] NalApps 디자인 토큰과 화면 범위 CSS/JS 격리를 지킨다.
- [ ] 플러그인 외 관리자/프런트 화면에 style/script가 불필요하게 로드되지 않는다.
- [ ] 키보드, visible focus, label, semantic control, contrast가 적절하다.
- [ ] destructive action은 확인 단계가 있고 mutation 보안 검사를 통과한다.
- [ ] non-critical notice는 남발하지 않고 필요 시 dismiss할 수 있다.
- [ ] 긴 작업은 진행 상태와 중복 제출 방지가 있다.
- [ ] 1440/1024/mobile 관리자 레이아웃 회귀가 없다.

## Security
- [ ] 모든 mutation은 최소 capability + nonce를 함께 검사한다.
- [ ] 입력은 타입/범위 validate 후 sanitize한다.
- [ ] 출력은 HTML/attribute/URL/JS 등 context별 escape한다.
- [ ] SQL은 안전한 WP API 또는 `$wpdb->prepare()`를 사용한다.
- [ ] REST는 `permission_callback`과 argument/schema validation이 있다.
- [ ] AJAX mutation은 capability + nonce를 검증한다.
- [ ] file upload는 extension/MIME/size/capability/nonce 검증을 수행한다.
- [ ] 업로드 파일을 실행 가능한 코드로 신뢰하지 않는다.

## Performance
- [ ] 필요한 화면/페이지에서만 assets와 remote calls를 실행한다.
- [ ] unbounded query/N+1을 피하고 대량 목록은 pagination 한다.
- [ ] 반복 원격/고비용 조회는 TTL과 invalidation이 정의된 cache를 사용한다.
- [ ] 매 page view마다 불필요한 업데이트/API 호출을 하지 않는다.

## Privacy / Telemetry / Diagnostics
- [ ] telemetry 기본값은 OFF다.
- [ ] telemetry/error reporting이 있으면 명시적 opt-in이고 수집 필드/endpoint를 문서화한다.
- [ ] 최소 데이터만 수집하고 개인정보/secret은 redaction한다.
- [ ] System Status/지원 진단 패키지에 credential 원문이 없다.
- [ ] 로그는 opt-in 또는 최소화, bounded retention, secret redaction을 지킨다.

## Compatibility / Naming / Lifecycle
- [ ] canonical slug/folder/namespace/function/option/transient/cron/REST prefix가 충돌 없이 일관된다.
- [ ] Plugin Header와 runtime 최소 WordPress/PHP 버전이 일치한다.
- [ ] 필요한 dependency와 `Requires Plugins`/runtime guard 정책이 명확하다.
- [ ] 활성화/비활성화/재활성화가 fatal 없이 동작한다.
- [ ] 비활성화는 사용자 콘텐츠/설정을 삭제하지 않는다.
- [ ] uninstall 데이터 삭제 기본값은 보존이며 삭제는 명시적 opt-in이다.
- [ ] multisite 지원 범위와 option/site_option scope가 명확하다.

## Database / Import / Recovery
- [ ] 코드 버전과 DB schema version을 분리한다(해당 시).
- [ ] migration은 deterministic, forward-only, idempotent다.
- [ ] migration 실패 시 성공한 것처럼 schema version을 올리지 않는다.
- [ ] downgrade를 자동 수행하지 않는다.
- [ ] import는 schema/version/known fields를 검증하고 secret을 기본 export하지 않는다.
- [ ] destructive migration/import에는 recovery/backup plan이 있다.

## Cron / Concurrency / External HTTP
- [ ] cron 중복 예약이 없고 비활성화 시 제품 소유 hook만 해제한다.
- [ ] 중복 클릭/retry/cron overlap이 duplicate mutation을 만들지 않도록 lock/idempotency가 있다.
- [ ] lock은 expiry와 recovery가 있다.
- [ ] 외부 HTTP는 HTTPS 우선, SSL verify, timeout, response/schema validation, cache를 사용한다.
- [ ] 무제한 retry가 없다.
- [ ] 외부 서버 장애가 WordPress fatal로 이어지지 않는다.

## Feature Flags / Deprecated / Supply Chain
- [ ] experimental 기능은 기본 OFF이고 security/license gate를 우회하지 않는다.
- [ ] 제거되는 공개/내부 계약은 가능한 범위에서 deprecation path를 둔다.
- [ ] production dependencies와 버전 제한이 선언되어 있다.
- [ ] build가 lock file을 사용하면 lock file을 추적한다.
- [ ] dev dependency는 runtime 필요가 없으면 배포 ZIP에서 제외한다.
- [ ] release asset은 신뢰된 CI에서 생성한다.

## EDD License & Hybrid Updates (유료 제품)
- [ ] Store URL, Download ID, slug/folder, plugin file이 정확하다.
- [ ] Composer runtime dependency가 있으면 `vendor/` 포함 Release Asset을 사용한다.
- [ ] WordPress Plugins 화면에서 새 버전 알림/업데이트가 가능하다.
- [ ] 플러그인 내부에서도 현재/최신 버전, 라이선스, 업데이트 확인/실행 상태를 확인할 수 있다.
- [ ] 라이선스가 필요한 package download를 우회하지 않는다.
- [ ] 라이선스 서버 장애와 invalid/revoked 상태를 구분한다.

## Test / CI / Release
- [ ] PHP syntax/static sanity PASS.
- [ ] 제품에 맞는 unit/integration/admin E2E PASS.
- [ ] unauthorized capability/nonce failure tests PASS.
- [ ] migration idempotency, cron duplicate, logging redaction tests PASS(해당 시).
- [ ] 지원 WordPress/PHP matrix가 정의되고 핵심 조합 PASS.
- [ ] package root folder가 canonical slug와 일치한다.
- [ ] production dependency/vendor 포함 여부가 제품 계약과 일치한다.
- [ ] 구버전 → 최신버전 실제 upgrade regression을 최소 1회 검증했다.
- [ ] 기존 사용자 데이터가 유지된다.
- [ ] 모든 변경 완료 후 마지막에 version bump를 수행했다.

참조: `docs/MASTER-STANDARD.md`, `docs/ENGINEERING-CONTRACTS-V3.md`, `docs/PUBLIC-REPOSITORY-SAFETY.md` 및 제품별 추가 계약.
