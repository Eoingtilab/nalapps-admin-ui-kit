# Changelog

## 4.2.0
- 슬라이드팝업 UI 파일럿에서 검증한 상용형 관리자 디자인을 공통 NalApps Admin UI로 승격
- 과도한 카드/그라데이션 대신 화이트 작업면, 얇은 경계, 절제된 그림자, 블루 포인트, active underline navigation 적용
- 공통 page header에 contextual action 영역 추가
- 공통 관리자 내비게이션 계약에 업데이트, 백업/복구, 시스템 정보 영역 추가
- maintenance UI에 데이터 내보내기/가져오기, 롤백, 시스템 정보, 제거 시 전체 데이터 삭제 toggle을 동일 디자인으로 통합
- 생성형 maintenance runtime에 refined admin UI CSS/typography 자산을 자동 포함
- EDD 유료형 내부 업데이트 화면은 단순 버전 확인이 아니라 capability+nonce+valid license+package 검증 후 `Plugin_Upgrader`를 통한 실제 `Update now` 실행을 필수 계약으로 명문화
- standard audit에 실행형 internal updater, package URL, Plugin_Upgrader, refined UI, delete-all toggle 회귀 게이트 추가
- 기존 WordPress Plugins 화면 업데이트와 내부 업데이트 실행을 모두 유지

## 4.1.0
- 모든 생성 플러그인에 pre-update 코드 백업과 데이터 스냅샷 기반 롤백 runtime 추가
- 선언형 `data_contract` 기반 데이터 JSON 내보내기/가져오기 및 import 전 자동 snapshot 추가
- 플러그인 제거 시 기본 데이터 보존, 명시적 `delete_all` 선택 시에만 선언된 플러그인 데이터 삭제 계약 추가
- 비밀정보를 제외한 System Information 및 WordPress Site Health 진단 정보 추가
- EDD Software Licensing 응답의 canonical `package` 필드를 실제 업데이트 설치 URL로 사용하고 `download_link`는 호환 fallback으로 제한
- rollback/data portability/safe uninstall/system info를 canonical CLI 생성 결과와 CI release gate에 포함

## 4.0.0
- 문서형 표준을 `Plugin Profile → Product Scaffold → CI Enforcement → Immutable Release Gate` 자동화 체계로 승격
- canonical `tools/scaffold_product.py` 완성형 플러그인 generator 추가
- 내부 scaffold 계층을 `scaffold_plugin.py` → `scaffold_complete.py` → `scaffold_product.py`로 분리
- `profiles/plugin-profile.schema.json`을 plugin/release/EDD metadata까지 확장하고 unknown field fail-closed 적용
- `edd_paid` profile에서 `edd_download_id`와 `edd_store_url`을 필수화
- 안전한 `release_mode=manual|auto_on_version_bump` 계약 추가, 신규 scaffold 기본은 manual release
- free / EDD paid + API / full-capability synthetic plugin 3종 self-test matrix 추가
- 모든 생성형에 activation/deactivation lifecycle 및 secret-free System Status 연결
- profile별 external HTTP, DB migration, Cron, REST, file upload 모듈 조건부 생성 및 bootstrap 연결
- EDD paid profile에서 Software Licensing SDK runtime dependency, SDK registry/loader, license state adapter, WordPress 기본 updater, 내부 Updates 화면 자동 생성
- EDD paid generated updater에 capability + nonce, bounded cache, HTTP/JSON validation, 활성 라이선스 기반 update install 적용
- generated plugin에 Composer/WPCS 설정, GitHub quality workflow, immutable release workflow, release acceptance checklist 자동 생성
- 표준 저장소에 실제 WordPress Coding Standards / PHPCS CI enforcement 추가
- PHP 7.4 / 8.1 / 8.3 / 8.4 / 8.5 syntax matrix 추가
- Composer dependency audit 자동화 추가
- public repository secret/credential/backup/customer-data guard script 추가
- release package file SHA-256 provenance manifest generator 추가
- standard canonical file/cross-reference drift를 차단하는 `tools/standard_audit.py` 추가
- 표준 VERSION 태그도 self-test/security/dependency/PHP/WPCS 검증 이후에만 생성하도록 강화
- 기존 VERSION/tag는 immutable 처리하고 tag 이동/재생성 금지
- generated product release 기본값을 manual로 설정해 신규 scaffold의 우발적 자동 배포 방지
- generated product release도 기존 tag/release overwrite 금지, ZIP root 및 SHA-256 checksum 검증 후 신규 release 생성
- production Composer dependency가 있으면 release 전 `composer install --no-dev` 후 `vendor/` 포함하도록 build 계약 강화
- 자동 검증과 Human Final Gate를 분리한 v4 Acceptance Gate 확정
- `docs/AUTOMATION-AND-SCAFFOLDING.md` 추가
- free/EDD paid canonical example profile 추가

## 3.0.0
- 저장소 정식 명칭을 `Eoingtilab/nalapps-wordpress-plugin-standard` 기준으로 통일
- `profiles/company-profile.json` canonical EOINGTI Lab 회사 프로필 추가
- `profiles/plugin-profile.schema.json` 및 example profile 추가
- 제품별 profile만 입력하고 나머지 공통 표준을 자동 상속하는 개발 방식 확정
- 최상위 `docs/MASTER-STANDARD.md` 추가
- 성능 budget, conditional asset loading, 접근성, 관리자 UX 계약 추가
- Privacy/Telemetry opt-in, 최소수집, diagnostics redaction 계약 추가
- REST/AJAX permission/schema 및 file upload validation 계약 추가
- concurrency lock, idempotency, retry/overlap 방지 계약 추가
- Feature Flag, backup/recovery, import/export, capability matrix 계약 추가
- namespace/prefix/conflict isolation 및 deprecated API 정책 추가
- dependency/lock file/supply-chain/release asset 정책 추가
- public repository safety gate와 secret/customer-data 금지 규칙 추가
- `SECURITY.md`, `CONTRIBUTING.md` 추가
- Plugin Header에 Domain Path, Requires Plugins, Network, GPL metadata 표준 확장
- GitHub README 및 WordPress readme.txt 공통 템플릿 강화
- reusable `templates/github/workflows/plugin-ci.yml` CI template 추가
- `docs/TESTING-CI-RELEASE.md` 추가 및 version bump-last release protocol 확정
- Acceptance Gate를 metadata/public safety/UI/accessibility/security/performance/privacy/lifecycle/DB/concurrency/supply-chain/EDD/CI 전체로 확대

## 2.3.0
- EOINGTI Lab/어잉티연구소 canonical company profile 추가
- 개발사 홈페이지 기본값을 `https://eoingti.com/`로 고정
- GitHub 조직/owner 기본 규칙 `Eoingtilab/<plugin-slug>` 추가
- WordPress plugin header/README 공통 template 및 release metadata consistency 검증 추가

## 2.2.0
- NalApps Admin UI Kit을 `NalApps WordPress Plugin Standard Kit`으로 확장
- capability + nonce, DB migration, Cron, logger, System Status, lifecycle/uninstall 공통 template 추가

## 2.1.0
- 선택형 `EDD License & Hybrid Updates` 공통 모듈 추가
- WordPress 플러그인 페이지 기본 업데이트 알림 및 내부 업데이트 확인/설치 template 추가
- Composer `vendor/` 포함 GitHub Release ZIP 계약 추가

## 2.0.1
- Pretendard Variable typography 표준 적용

## 2.0.0
- Blue/Navy/Soft Blue/Neutral Gray 기반 NalApps 관리자 디자인 표준 확정
