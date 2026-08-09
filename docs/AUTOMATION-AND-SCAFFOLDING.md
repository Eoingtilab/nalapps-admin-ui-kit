# NalApps Automation & Scaffolding v4

NalApps WordPress Plugin Standard v4의 목적은 표준을 사람이 매번 해석해서 적용하는 것이 아니라 **제품 profile을 입력하면 프로젝트 골격과 품질게이트를 자동 생성하고 CI가 표준 위반을 차단**하는 것이다.

## Canonical entrypoint

```bash
python tools/scaffold_product.py --profile path/to/plugin-profile.json --output build/scaffold --clean
```

생성기는 `profiles/company-profile.json`, `profiles/plugin-profile.schema.json`, `VERSION`을 canonical source로 사용한다.

내부 계층은 `scaffold_plugin.py` → `scaffold_complete.py` → `scaffold_product.py` 순서이며, 외부 사용자는 최상위 `scaffold_product.py`만 사용한다.

## 자동 생성 범위

기본 생성:
- main plugin bootstrap
- unique namespace/prefix 기반 core class
- activation/deactivation lifecycle hook
- read-only System Status
- plugin-profile.json
- nalapps-standard-manifest.json
- README.md / readme.txt / CHANGELOG.md
- SECURITY.md / CONTRIBUTING.md
- .gitignore
- composer.json
- phpcs.xml.dist
- GitHub quality workflow
- immutable release workflow
- release acceptance checklist

Profile별 조건부 생성:
- `external_api=true`: bounded HTTPS HTTP client skeleton
- `database=true`: schema-version migration skeleton + lifecycle 연결
- `cron=true`: duplicate-safe Cron manager + activation/deactivation 연결
- `rest_api=true`: permission_callback이 있는 read-only REST skeleton + REST bootstrap 연결
- `file_upload=true`: capability + MIME/extension validation skeleton
- `product_type=edd_paid`: EDD SDK runtime dependency, SDK registry/loader, EDD config, license state adapter, WordPress 기본 updater, 내부 Updates 화면, EDD release gate

## EDD paid 자동화

`edd_paid` profile은 `edd_download_id`와 `edd_store_url`이 없으면 validation 실패한다.

생성되는 유료형 runtime:
- Composer production dependency로 EDD Software Licensing SDK 선언
- main plugin에서 `edd_sl_sdk_registry` 등록
- production `vendor/easy-digital-downloads/edd-sl-sdk/edd-sl-sdk.php` 로드
- SDK canonical license option을 읽는 `License` adapter
- EDD `get_version`을 사용하는 `Update_Manager`
- WordPress `update_plugins` transient 보강
- Settings 아래 내부 Updates 화면
- capability + nonce manual check/install
- 활성 라이선스 + download URL 조건의 내부 update install

표준은 제품의 고유 기능을 알 수 없으므로 라이선스 invalid 시 제품 전체 기능을 임의로 차단하지 않는다. 제품 기능 gating은 제품 요구사항에서 별도로 명시한다.

## Release mode

Profile의 `release_mode`:
- `manual`: 기본값. `workflow_dispatch`로 명시적으로 release 실행
- `auto_on_version_bump`: 운영 release 절차가 검증된 제품에서만 사용. main plugin/readme version 변경 push를 release 후보로 처리

기존 tag/release는 두 모드 모두 immutable이다.

## 자동 검증

`tools/self_test.py`는 최소 3개의 synthetic product profile을 매번 생성한다.

1. free/basic
2. EDD paid + external API
3. full-capability private plugin

각 fixture에서 다음을 검증한다.
- 필수 파일
- System Status
- 조건부 모듈
- manifest module selection
- standard version
- generated Composer/WPCS/workflow
- EDD paid SDK dependency + license/updater wiring
- unresolved secret placeholder 없음

## CI enforcement

`.github/workflows/quality-gate.yml`은 다음을 자동 실행한다.

- canonical standard audit
- JSON Schema profile validation
- product scaffold self-test matrix
- public repository safety gate
- Composer dependency audit
- PHP syntax
- WordPress Coding Standards / PHPCS
- PHP 7.4 / 8.1 / 8.3 / 8.4 / 8.5 syntax matrix
- release provenance generator smoke test

기계적으로 검증 가능한 항목은 사람이 체크박스를 눌렀다는 이유만으로 PASS 처리하지 않는다.

## Release tagging

`VERSION`은 **모든 기능/문서/테스트 변경이 끝난 마지막 커밋에서만** 변경한다.

표준 저장소의 `tag-version.yml`은 새 VERSION을 발견해도 즉시 태그하지 않는다. profile/self-test/security/WPCS/dependency gate를 먼저 통과한 뒤에만 immutable `v{VERSION}` 태그를 생성한다.

이미 존재하는 버전 태그는 재생성하거나 다른 commit으로 이동시키지 않는다.

## Product release contract

Product scaffold가 생성하는 release workflow는 다음 원칙을 사용한다.

- 기본 release mode는 manual
- 기존 tag가 있으면 release rebuild/overwrite 금지
- PHP syntax와 WPCS 통과 후 build
- Composer dependency audit
- production Composer dependency가 있으면 `composer install --no-dev`
- canonical slug를 ZIP root folder로 사용
- runtime `vendor/`가 필요하면 distribution에 포함
- SHA-256 checksum 생성
- validation 이후에만 tag 생성
- tag 생성 이후 GitHub Release 생성

EDD SDK처럼 runtime dependency가 필요한 제품은 GitHub Source ZIP을 배포 파일로 사용하지 않는다.

## Human-only gates

다음은 자동화만으로 완전 판정하지 않는다.

- 실제 WordPress 관리자/프런트 UX E2E
- 기능의 사업 요구사항 적합성
- 실제 접근성 흐름
- 실제 EDD 라이선스 activation/deactivation/update
- 구버전에서 최신버전으로의 실제 upgrade regression
- 외부 서비스 약관/개인정보 고지 적합성

이 항목은 `docs/ACCEPTANCE-CHECKLIST.md`에서 사람이 최종 승인한다.
