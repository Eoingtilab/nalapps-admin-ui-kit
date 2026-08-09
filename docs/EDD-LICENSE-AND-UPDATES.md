# NalApps EDD License & Hybrid Updates v4

NalApps 유료 WordPress 플러그인은 `product_type=edd_paid` profile을 사용하면 **EDD Software Licensing SDK + 라이선스 상태 adapter + WordPress 기본 updater + 플러그인 내부 updater + production dependency release build**를 자동 선택합니다.

## 목표

하나의 EDD Software Licensing 제품을 기준으로 다음 두 업데이트 UX를 동시에 제공합니다.

1. WordPress `플러그인` 화면의 기본 업데이트 알림/업데이트
2. 플러그인 내부 `설정 → <제품명> Updates` 화면의 현재 버전·최신 버전·라이선스 상태·수동 확인·즉시 업데이트

## Profile 필수값

`edd_paid` 제품은 최소 다음 값이 필요합니다.

- `product_type`: `edd_paid`
- `edd_store_url`
- `edd_download_id`
- canonical plugin `slug`

`profiles/plugin-profile.schema.json`은 위 값을 fail-closed로 검증합니다. Store URL이나 Download ID를 추측해서 생성하지 않습니다.

## v4 자동 생성

Canonical entrypoint `tools/scaffold_product.py`는 EDD 유료형에서 다음을 추가합니다.

- `composer.json` runtime dependency: EDD Software Licensing SDK
- SDK registry bootstrap
- SDK runtime loader under `vendor/easy-digital-downloads/edd-sl-sdk/`
- `includes/class-edd-config.php`
- `includes/class-license.php`
- `includes/class-update-manager.php`
- WordPress `update_plugins` transient integration
- 내부 Updates 관리자 화면
- capability + nonce가 적용된 manual check / install action
- `get_version` request cache
- runtime Composer dependency가 있으면 `vendor/`를 포함하는 release build

## 라이선스 상태

Generated `License` adapter는 SDK가 저장한 canonical option을 읽습니다.

- key option: `<plugin_slug_with_underscores>_license_key`
- status option: `<plugin_slug_with_underscores>_license`
- 활성 상태: `valid` 또는 `active`

제품 기능 자체를 라이선스 상태로 잠글지는 제품 요구사항에 따라 명시적으로 결정합니다. 표준은 updater/download authorization을 제공하지만, 알 수 없는 제품 기능을 임의로 비활성화하지 않습니다.

## EDD API 계약

업데이트 확인은 Software Licensing `get_version` 요청을 사용합니다.

- `edd_action=get_version`
- `item_id`
- `license` — 저장된 라이선스가 있으면 포함
- `url`
- `php_version`
- `wp_version`

원격 통신은 timeout, SSL verification, HTTP status, JSON validation을 적용하고 응답은 bounded transient cache를 사용합니다.

## 업데이트 실행 안전성

- 관리자 capability `update_plugins` 필요
- check/install mutation은 각각 nonce 검증
- 실제 설치는 활성 라이선스와 다운로드 URL이 있을 때만 허용
- 원격 오류는 기존 플러그인 데이터나 설정을 삭제하지 않음
- update response는 WordPress 기본 Plugins 화면과 내부 Updates 화면에서 동일한 최신 버전 정보를 사용

## 배포 규칙

1. 코드/CSS/문서/테스트 변경을 먼저 완료합니다.
2. 버전 변경은 마지막 release commit에서만 합니다.
3. 이미 존재하는 tag/release는 immutable이며 덮어쓰거나 이동하지 않습니다.
4. production Composer dependency가 있으면 release build에서 `composer install --no-dev`를 수행합니다.
5. EDD SDK가 runtime dependency인 제품은 배포 ZIP에 `vendor/easy-digital-downloads/edd-sl-sdk/`가 포함되어야 합니다.
6. ZIP 최상위 폴더명은 canonical plugin slug와 정확히 일치해야 합니다.
7. release ZIP SHA-256 checksum을 남깁니다.
8. EDD 상품의 Version/Update File은 검증된 새 release에 맞춥니다.

## PASS 기준

Automated:
- profile validation PASS
- EDD runtime files generated
- composer runtime dependency present
- main bootstrap에 SDK registry/loader와 updater 연결 존재
- PHP syntax/WPCS/dependency/public-safety gate PASS
- ZIP root/runtime dependency contract PASS

Human E2E:
- 실제 라이선스 activate/deactivate PASS
- `get_version` 최신 버전 확인 PASS
- WordPress Plugins 화면에서 업데이트 알림 PASS
- 내부 Updates 화면에서도 같은 최신 버전 표시 PASS
- 내부 `Check for updates` 재조회 PASS
- 실제 `Update now` 설치 PASS
- 업데이트 후 기존 데이터/설정 보존 PASS

## 금지

- GitHub Source ZIP을 runtime Composer dependency가 있는 EDD 제품의 Update File로 사용하지 않음
- EDD Store URL/Download ID/license key를 추측하거나 public repo에 저장하지 않음
- 라이선스 키/API key/token/password를 로그/System Status에 원문 노출하지 않음
- 이미 출시한 tag/release asset을 같은 버전으로 교체하지 않음
