# NalApps EDD License & Hybrid Updates v4.4

NalApps 유료 WordPress 플러그인은 `product_type=edd_paid` profile을 사용하면 **제품 자체 라이선스 UI + EDD Software Licensing SDK + WordPress 기본 updater + 플러그인 내부 updater + production dependency Release Asset + 실제 업그레이드 검증**을 하나의 상용 운영 계약으로 적용합니다.

## 절대 원칙

1. 라이선스가 업데이트 권한을 제어할 수는 있지만, 이미 설치되어 정상 사용 중인 제품의 핵심 프런트/관리 기능을 라이선스 상태만으로 갑자기 중단시키지 않습니다. 기능 제한이 필요한 제품은 profile/제품 요구사항에 명시적으로 선언해야 합니다.
2. 유료 제품에는 SDK 상태와 무관하게 접근 가능한 **제품 자체 시리얼 입력/활성화/확인/비활성화 UI**가 반드시 존재해야 합니다.
3. `new_version` 표시만으로 업데이트 PASS로 판정하지 않습니다. 실제 설치 가능한 `package` 또는 `download_link`가 존재하고 N-1 → N 업데이트가 성공해야 합니다.
4. GitHub의 자동 Source Code ZIP은 상용 Update File로 인정하지 않습니다. 신뢰된 CI가 생성한 `plugin-slug-x.y.z.zip` Release Asset을 사용합니다.
5. tag/release/asset은 immutable입니다. 기존 asset을 `--clobber`로 덮어쓰지 않습니다.
6. tag 또는 Release만 먼저 생기고 Asset이 빠진 비정상 상태는 같은 tag의 소스에서 **누락 Asset만 backfill**하여 복구할 수 있어야 합니다.

## Profile 필수값

`edd_paid` 제품은 최소 다음 값이 필요합니다.

- `product_type`: `edd_paid`
- `edd_store_url`
- `edd_download_id`
- canonical plugin `slug`

Store URL, Download ID, 제품 URL 또는 credential은 추측하지 않습니다.

## 유료 제품 필수 Runtime

Canonical scaffold는 다음을 제공해야 합니다.

- `includes/class-license.php`: 제품 자체 License UI
- 시리얼 저장/활성화/확인/비활성화
- capability + nonce
- license key secret redaction
- EDD SDK runtime dependency 및 registry/loader
- `includes/class-update-manager.php`
- WordPress `update_plugins` transient integration
- 내부 Updates 화면
- `get_version` bounded cache
- `package` 우선, `download_link` 호환 fallback
- production `vendor/` 포함 Release build

제품 자체 License UI가 없으면 유료 제품 release gate는 FAIL입니다. 이전 버전의 라이선스 입력 경로가 사라져 새 버전으로 업데이트할 수 없는 **bootstrap deadlock**을 허용하지 않습니다.

## 라이선스 상태와 제품 기능

Canonical option 예:

- key: `<plugin_slug>_license_key`
- status: `<plugin_slug>_license`
- 활성 상태: `valid` 또는 `active`

라이선스는 기본적으로 다음 권한에 사용합니다.

- 업데이트 package entitlement
- 유료 지원/서비스 entitlement
- 제품별로 명시한 추가 상용 권한

프런트 렌더링, 저장된 사용자 콘텐츠 표시, 관리자 기본 접근 등 기존 핵심 기능은 별도 요구사항 없이 라이선스에 종속시키지 않습니다.

## EDD API 계약

업데이트 확인은 Software Licensing `get_version`을 사용합니다.

- `edd_action=get_version`
- `item_id`
- `license` — 저장된 키가 있으면 포함
- `url`
- `php_version`
- `wp_version`

원격 통신은 HTTPS/SSL verification, timeout, redirect 제한, HTTP status, JSON validation, bounded cache를 적용합니다.

정상 업데이트 응답은 최소한 다음을 만족해야 합니다.

- `new_version`이 현재 버전보다 큼
- 활성 라이선스가 필요한 제품은 라이선스 상태가 유효함
- `package` 또는 `download_link`가 비어 있지 않음
- package URL을 WordPress upgrader가 실제 다운로드할 수 있음

## Release Asset 계약

정식 배포는 다음 구조를 사용합니다.

- Tag: `vX.Y.Z`
- Release title: 제품명 + 버전
- Install Asset: `<plugin-slug>-X.Y.Z.zip`
- Checksum Asset: `<plugin-slug>-X.Y.Z.zip.sha256`
- ZIP root: `<plugin-slug>/`

Release workflow는 다음 순서를 지킵니다.

1. source/version 계약 검증
2. production dependency 설치
3. distribution ZIP 생성
4. ZIP root 및 필수 runtime 파일 검증
5. SHA-256 생성
6. 새 버전이면 검증 성공 후 tag 생성
7. Release 생성
8. ZIP/SHA256 Asset 업로드
9. 업로드 후 Asset 이름 재검증

이미 tag가 존재하지만 Release/Asset이 누락된 경우에는 tag 소스로 checkout하여 동일 버전 package를 재구성하고 **없는 Asset만 추가**합니다. 기존 Asset은 덮어쓰지 않습니다.

## EDD 관리자 연결 계약

GitHub Release가 정상이어도 EDD 상품이 잘못 연결되어 있으면 업데이트는 실패할 수 있습니다. 출시 시 아래 체인을 모두 확인합니다.

1. GitHub Version Tag = `vX.Y.Z`
2. GitHub Release에 실제 install ZIP Asset 존재
3. EDD Git Download Updater가 해당 **Release Asset**을 Fetch
4. EDD Download Files에 해당 파일이 선택됨
5. Software Licensing의 Version = `X.Y.Z`
6. Software Licensing Update File = 방금 Fetch한 install ZIP
7. EDD `get_version` 응답의 package/download URL 존재
8. 라이선스가 적용된 실제 WordPress에서 다운로드 및 설치 성공

`Release Source Code`를 Update File로 사용하지 않습니다.

## 업데이트 실행 안전성

- 관리자 capability `update_plugins` 필요
- mutation은 nonce 검증
- 활성 라이선스가 필요한 package는 우회하지 않음
- 원격 오류 시 기존 코드/데이터를 임의 삭제하지 않음
- 업데이트 직전 rollback 계약이 있는 제품은 코드 백업 성공 후 진행
- 업데이트 실패 시 현재 제품을 가능한 범위에서 유지/복구
- 캐시 때문에 이전 package URL을 계속 쓰지 않도록 라이선스/수동 재확인/업데이트 후 transient를 무효화

## Version 일관성

출시 시 아래 값은 동일 버전이어야 합니다.

- Plugin Header
- runtime version constant
- `readme.txt` Stable tag
- `plugin-profile.json`
- Git tag
- GitHub Release
- Release ZIP filename
- EDD Software Licensing Version

불일치는 release gate FAIL입니다.

## 필수 실제 Upgrade Regression

판매 가능한 상태로 판정하려면 최소 한 번은 **직전 판매 버전 N-1 → 신규 버전 N** 실제 업데이트를 수행합니다.

검증 항목:

- 기존 라이선스 입력/활성화 가능
- 업데이트 알림 표시
- package URL 존재
- package 다운로드 성공
- ZIP 설치 성공
- 업데이트 후 플러그인 활성 상태 정상
- 신규 버전 확인
- 기존 설정/콘텐츠/데이터 보존
- 핵심 프런트/관리 기능 정상
- 라이선스 확인/비활성화/재활성화 정상

이 실제 E2E가 불가능한 구버전이 이미 배포된 경우에는 새 버전을 수동 덮어설치하는 migration 경로를 명시하고, 다음 버전부터 자동 업데이트 가능한 상태를 보장합니다.

## 금지

- GitHub Source Code ZIP을 정식 상용 Update File로 사용
- tag를 package build보다 먼저 생성한 뒤 실패 상태를 방치
- 기존 Release Asset overwrite/clobber
- 라이선스 UI 없이 업데이트에 라이선스를 강제하여 사용자를 deadlock 상태로 만듦
- `new_version`만 보인다는 이유로 업데이트 기능을 PASS 처리
- secret/license key를 로그, System Status, export, public repository에 노출
- 기존 데이터 삭제를 업데이트 해결책으로 사용

## PASS 기준

Automated:
- profile/schema PASS
- product-native license UI contract PASS
- updater `package` contract PASS
- frontend runtime/license separation guard PASS
- PHP/WPCS/Plugin Check/dependency/public-safety PASS
- production ZIP root/runtime dependency/checksum PASS
- Release workflow에 immutable + missing-asset backfill 계약 존재

Human E2E:
- 실제 license activate/check/deactivate PASS
- 실제 `get_version` PASS
- 실제 package URL PASS
- WordPress 기본 updater PASS
- 내부 updater PASS
- N-1 → N 실제 upgrade PASS
- 데이터/설정/핵심 기능 보존 PASS
- EDD Update File이 Release Asset ZIP과 연결됨
