# NalApps WordPress Plugin Standard v4.4 Acceptance Gate

모든 해당 항목이 PASS여야 release 완료로 판단합니다. 제품 profile에서 사용하지 않는 기능만 N/A 처리할 수 있습니다.

## Automated Gate — CI가 직접 판정
- [ ] `plugin-profile.json`이 canonical JSON Schema를 통과한다.
- [ ] 표준 저장소 self-test가 free / EDD paid / full-capability synthetic profile을 모두 생성한다.
- [ ] scaffold 필수 파일과 profile별 조건부 모듈 선택이 일치한다.
- [ ] PHP syntax가 지원 PHP matrix에서 통과한다.
- [ ] WordPress Coding Standards / PHPCS gate가 통과한다.
- [ ] Composer dependency audit가 통과한다.
- [ ] public repository secret/credential/backup/customer-data safety gate가 통과한다.
- [ ] package root와 canonical slug가 일치한다.
- [ ] Version / Stable tag / profile metadata의 기계 검증 가능한 값이 일치한다.
- [ ] release provenance/hash 생성기가 정상 동작한다.
- [ ] 이미 존재하는 tag/release/asset을 덮어쓰거나 이동하지 않는다.
- [ ] 상용 Release template에 `--clobber`가 존재하지 않는다.
- [ ] Release template은 ZIP root 검사와 SHA-256 생성을 수행한다.
- [ ] tag/Release는 있으나 ZIP/SHA256이 빠진 상태에서 누락 Asset만 backfill할 수 있다.
- [ ] existing tag recovery build는 반드시 해당 tag source로 pin한다.
- [ ] 새 tag는 package build/validation 성공 이후에만 생성한다.
- [ ] 표준 VERSION tag는 모든 automated gate 통과 후에만 생성된다.

## Company / Metadata
- [ ] Author=`EOINGTI Lab`, Author URI=`https://eoingti.com/` 기본값이 유지된다.
- [ ] GitHub owner=`Eoingtilab`, repository=`Eoingtilab/<plugin-slug>` 규칙을 따른다.
- [ ] Plugin URI는 실제 제품 페이지 또는 `https://eoingti.com/`이며 가짜 URL이 없다.
- [ ] README/readme.txt에 개발사, 홈페이지, source, 요구환경, 설치, 사용, 지원, privacy, license, changelog가 필요한 범위에서 포함된다.
- [ ] Plugin Header / runtime constant / Stable tag / profile / Git tag / Release / ZIP filename / EDD Version이 출시 시 일치한다.

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
- [ ] 긴 작업은 진행 상태와 중복 제출 방지가 있다.
- [ ] 1440/1024/mobile 관리자 레이아웃 회귀가 없다.

## Security
- [ ] 모든 mutation은 최소 capability + nonce를 함께 검사한다.
- [ ] 입력은 타입/범위 validate 후 sanitize한다.
- [ ] 출력은 context별 escape한다.
- [ ] SQL은 안전한 WP API 또는 `$wpdb->prepare()`를 사용한다.
- [ ] REST/AJAX/file upload는 해당 permission/nonce/schema/MIME/size 검증을 수행한다.

## Performance / Privacy / Diagnostics
- [ ] 필요한 화면/페이지에서만 assets와 remote calls를 실행한다.
- [ ] 반복 원격/고비용 조회는 TTL과 invalidation이 정의된 cache를 사용한다.
- [ ] telemetry 기본값은 OFF다.
- [ ] System Status/로그/지원 진단에 credential/license key 원문이 없다.

## Compatibility / Naming / Lifecycle
- [ ] canonical slug/folder/namespace/function/option/transient/cron/REST prefix가 일관된다.
- [ ] Plugin Header와 runtime 최소 WordPress/PHP 버전이 일치한다.
- [ ] 활성화/비활성화/재활성화가 fatal 없이 동작한다.
- [ ] 비활성화는 사용자 콘텐츠/설정을 삭제하지 않는다.
- [ ] uninstall 기본값은 `preserve`이며 삭제는 명시적 opt-in이다.

## Database / Import / Recovery
- [ ] code version과 DB schema version을 분리한다(해당 시).
- [ ] migration은 deterministic, forward-only, idempotent다.
- [ ] migration/import 전 recovery/backup plan이 있다.
- [ ] secret은 기본 export하지 않는다.

## Cron / Concurrency / External HTTP
- [ ] cron 중복 예약이 없고 비활성화 시 제품 소유 hook만 해제한다.
- [ ] 중복 mutation 방지 lock/idempotency가 있다.
- [ ] 외부 HTTP는 SSL verify, timeout, response/schema validation, bounded retry/cache를 사용한다.
- [ ] 외부 서버 장애가 WordPress fatal로 이어지지 않는다.

## EDD License & Hybrid Updates (유료 제품)
- [ ] Store URL, Download ID, slug/folder, plugin file이 정확하다.
- [ ] SDK UI가 없어도 접근 가능한 **제품 자체 라이선스 입력 UI**가 있다.
- [ ] 시리얼 저장/활성화/확인/비활성화가 실제 동작한다.
- [ ] 라이선스 입력 UI가 없는 상태에서 업데이트에 라이선스를 요구하는 bootstrap deadlock이 없다.
- [ ] 별도 요구사항이 없으면 기존 핵심 프런트/관리 기능을 라이선스 상태로 잠그지 않는다.
- [ ] Composer runtime dependency가 있으면 `vendor/` 포함 Release Asset을 사용한다.
- [ ] GitHub 자동 `Release Source Code` ZIP을 EDD Update File로 사용하지 않는다.
- [ ] 정식 `<plugin-slug>-X.Y.Z.zip` Release Asset과 `.sha256`이 존재한다.
- [ ] EDD Git Download Updater가 해당 Release Asset을 Fetch했다.
- [ ] Software Licensing Version이 출시 버전과 일치한다.
- [ ] Software Licensing Update File이 실제 Release Asset ZIP으로 지정되어 있다.
- [ ] `get_version` 응답에서 `new_version`뿐 아니라 실제 설치 가능한 `package` 또는 `download_link`가 존재한다.
- [ ] 라이선스가 필요한 package download를 우회하지 않는다.
- [ ] 라이선스 서버 장애와 invalid/revoked 상태를 구분한다.
- [ ] WordPress Plugins 화면에서 새 버전 알림과 실제 업데이트가 가능하다.
- [ ] 플러그인 내부에서도 같은 최신 버전/라이선스/업데이트 상태를 확인하고 실행할 수 있다.

## Human Final Gate — 자동화로 대체하지 않음
- [ ] 제품 요구사항과 실제 기능이 일치한다.
- [ ] 실제 WordPress 관리자/프런트 E2E가 통과한다.
- [ ] 실제 지원 브라우저/반응형 화면에서 UI가 정상이다.
- [ ] 직전 판매 버전 N-1 → 신규 N **실제 업데이트 설치**를 최소 1회 검증했다.
- [ ] package URL 다운로드 → ZIP 설치 → 활성 상태 → 신규 버전 확인까지 전부 성공했다.
- [ ] 업데이트 후 기존 사용자 데이터/설정/콘텐츠가 유지된다.
- [ ] 업데이트 후 핵심 프런트/관리 기능이 정상이다.
- [ ] EDD 유료 제품은 실제 라이선스 activate/check/deactivate/re-activate를 검증했다.
- [ ] 기존 구버전 구조적 결함으로 자동 업데이트가 불가능하면 안전한 1회 수동 덮어설치 migration 경로를 문서화하고, 그 다음 버전부터 자동 업데이트 가능함을 검증했다.
- [ ] 외부 서비스 약관/개인정보 고지/수집 필드가 실제 구현과 일치한다.
- [ ] 모든 변경 완료 후 마지막에 version bump를 수행했다.

참조: `docs/MASTER-STANDARD.md`, `docs/ENGINEERING-CONTRACTS-V3.md`, `docs/AUTOMATION-AND-SCAFFOLDING.md`, `docs/PUBLIC-REPOSITORY-SAFETY.md`, `docs/EDD-LICENSE-AND-UPDATES.md`.
