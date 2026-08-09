# Rollback / Backup / Data Lifecycle

NalApps WordPress Plugin Standard은 모든 생성 플러그인에 공통 유지보수 계층을 제공합니다. 목표는 외부 롤백 플러그인 의존 없이 업데이트 실패에 대비하고, 플러그인 소유 데이터를 안전하게 이동·복원하며, 제거 시 데이터 보존/삭제를 사용자가 명시적으로 선택할 수 있게 하는 것입니다.

## 1. Code rollback

- 자기 플러그인의 업데이트 직전 `upgrader_pre_install`에서 현재 설치 디렉터리를 ZIP으로 백업합니다.
- 코드 백업이 실패하면 해당 업데이트를 fail-closed로 차단합니다.
- 최근 코드 백업은 최대 3개 유지합니다.
- 롤백은 `update_plugins` capability와 nonce를 요구합니다.
- 로컬 비상 롤백 대상은 실제 백업 목록에 존재하는 파일만 허용합니다.
- WordPress core `Plugin_Upgrader`를 사용해 선택한 패키지를 `overwrite_package=true`로 복원합니다.
- 롤백 직전 현재 코드와 데이터도 다시 snapshot하여 되돌릴 지점을 하나 더 남깁니다.

### Verified Release Version Rollback

NalApps Standard v4.5부터 Maintenance Center는 Elementor 계열 UX와 유사하게 **검증된 이전 배포 버전을 선택하여 롤백**할 수 있어야 합니다.

- GitHub Releases API에서 draft/prerelease를 제외한 정식 Release만 조회합니다.
- 현재 설치 버전보다 낮은 semantic version만 후보로 노출합니다.
- 각 버전은 정확히 `<plugin-slug>-<version>.zip` 이름의 **Release Asset**이 실제 존재할 때만 후보가 됩니다.
- GitHub 자동 생성 `Source code (zip/tar.gz)`는 롤백 패키지로 절대 사용하지 않습니다.
- 선택한 버전 문자열과 서버에서 다시 조회한 허용 목록을 대조하여 임의 URL/임의 버전 입력을 차단합니다.
- 롤백 직전 현재 코드 ZIP과 데이터 snapshot을 자동 생성합니다.
- 롤백 후 WordPress update transient와 Release rollback cache를 초기화합니다.
- Release API가 실패하거나 검증된 Asset이 없으면 fail-closed로 버전 롤백 UI를 비활성화합니다.

**중요:** 코드 롤백은 데이터베이스 migration을 역방향으로 실행하지 않습니다. 스키마/데이터를 이전 상태로 되돌려야 하면 별도 데이터 snapshot/import를 사용하고 제품별 migration 호환성을 검증해야 합니다.

## 2. Data backup / Export / Import

제품은 `plugin-profile.json`의 `data_contract`에 자신이 소유한 데이터만 선언합니다.

```json
{
  "data_contract": {
    "options": ["my_plugin_settings"],
    "site_options": [],
    "post_types": ["my_plugin_item"],
    "custom_tables": ["my_plugin_records"]
  }
}
```

- export 형식: `nalapps-data-backup-v1`
- plugin slug/version/standard version/UTC 생성시각을 기록합니다.
- 선언된 option/site option/post type만 자동 export 대상입니다.
- password, secret, token, API key, license key 등 민감 option 이름은 profile validation에서 차단합니다.
- import는 `manage_options` capability + nonce + JSON 확장자 + 최대 파일 크기 + plugin slug/format 검증을 통과해야 합니다.
- import 직전 로컬 snapshot을 자동 생성합니다.
- 사용자 UI에서는 `Export/Import`보다 의미가 분명한 `백업 파일 다운로드 / 백업 파일 복원` 표현을 우선합니다.
- 데이터 백업/복원, 버전 롤백, 로컬 비상백업, 제거 정책은 서로 다른 위험도이므로 Maintenance Center에서 별도 섹션으로 분리합니다.

Custom table은 제품별 스키마 의미가 다르므로 generic JSON import/export를 추측하지 않습니다. 대신 `custom_tables`는 완전 삭제 범위를 선언하고, 실제 portable table 데이터가 필요하면 제품 adapter와 별도 round-trip test를 추가합니다.

## 3. Backup storage and retention

- 코드 백업: 최근 3개
- 데이터 snapshot: 최근 5개
- 저장 디렉터리는 site salt 기반 비예측 토큰을 포함합니다.
- `index.php`, Apache `.htaccess`를 작성해 직접 접근 위험을 낮춥니다.
- Nginx/프록시/오브젝트 스토리지 환경에서는 서버 정책이 파일 접근을 우선하므로 운영 환경에서 backup 경로 비공개 여부를 별도 확인합니다.
- 백업에는 고객 데이터가 포함될 수 있으므로 공개 Git 저장소나 support ticket에 첨부하면 안 됩니다.

## 4. Update Center contract

상용 플러그인의 내부 Update Center는 WordPress 플러그인 목록으로 사용자를 다시 보내는 단순 링크가 아니라 실제 관리 화면이어야 합니다.

- 현재 버전과 최신 버전을 명확히 표시합니다.
- `업데이트 확인`을 제공합니다.
- 새 버전 + 유효 라이선스 + 실제 `package/download_link`가 모두 충족되면 내부 화면에서 `지금 업데이트`를 즉시 실행할 수 있어야 합니다.
- 업데이트 전 코드 backup + data snapshot 계약을 그대로 통과해야 합니다.
- 최신 버전일 때는 최신 상태를 명확히 표시합니다.
- 라이선스/패키지/서버 오류는 서로 구분된 운영 메시지로 표시합니다.
- 업데이트 실패 시 기존 자동 backup이 존재해야 하며 Maintenance Center에서 로컬 복구 또는 검증된 이전 Release 롤백을 수행할 수 있어야 합니다.

## 5. Uninstall policy

기본값은 항상 `preserve`입니다.

- `preserve`: 플러그인 파일만 제거하고 사용자 데이터를 유지합니다.
- `delete_all`: 사용자가 Maintenance 화면에서 명시적으로 선택한 경우에만 `uninstall.php`가 선언된 options/site options/post types/custom tables 및 표준 소유 maintenance 상태를 삭제합니다.
- EDD paid 제품은 `delete_all`일 때만 해당 제품의 EDD license option도 삭제합니다.
- 삭제 후 제품별 cleanup action을 호출해 추가 소유 데이터를 정리할 수 있습니다.

삭제는 비가역 작업이므로 제품 release 전 preserve/delete-all 양쪽 경로를 테스트해야 합니다.

## 6. System Information

모든 제품은 민감정보를 제외한 진단 정보를 제공합니다.

- plugin/standard/WordPress/PHP 버전
- locale, multisite, HTTPS
- PHP memory/upload 제한
- WP_DEBUG 상태
- active theme
- local code rollback backup 개수
- verified rollback Release 개수
- data snapshot 개수

동일 정보는 NalApps Maintenance 화면과 WordPress Site Health > Info의 플러그인 전용 섹션에 노출합니다. DB 비밀번호, API key, license key, token, cookie, 고객 데이터, 절대 secret 값은 노출하지 않습니다.

## 7. Release gates

모든 제품은 다음 항목을 적용 가능한 범위에서 PASS해야 합니다.

- pre-update backup 생성과 실패 시 update block
- 실제 local rollback ZIP root/버전 검증
- 검증된 Release Asset 버전 목록 생성
- Source Code archive가 버전 롤백 후보에서 제외됨을 검증
- 현재 버전보다 높은/같은 버전 rollback 거부
- N → N-1 실제 버전 롤백 E2E
- 롤백 직전 코드/data 재백업
- export → import round trip
- 잘못된 JSON/다른 plugin slug/과대 파일 import 거부
- 민감 option profile 거부
- uninstall preserve/delete-all 양쪽 검증
- system info redaction
- migration이 있는 제품의 code rollback/data restore 조합 E2E
- multisite 제품의 site/network 데이터 범위 검증
