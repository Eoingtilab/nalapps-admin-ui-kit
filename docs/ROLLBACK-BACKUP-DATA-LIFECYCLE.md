# Rollback / Backup / Data Lifecycle

NalApps WordPress Plugin Standard은 모든 생성 플러그인에 공통 유지보수 계층을 제공합니다. 목표는 외부 롤백 플러그인 의존 없이 업데이트 실패에 대비하고, 플러그인 소유 데이터를 안전하게 이동·복원하며, 제거 시 데이터 보존/삭제를 사용자가 명시적으로 선택할 수 있게 하는 것입니다.

## 1. Code rollback

- 자기 플러그인의 업데이트 직전 `upgrader_pre_install`에서 현재 설치 디렉터리를 ZIP으로 백업합니다.
- 코드 백업이 실패하면 해당 업데이트를 fail-closed로 차단합니다.
- 최근 코드 백업은 최대 3개 유지합니다.
- 롤백은 `update_plugins` capability와 nonce를 요구합니다.
- 롤백 대상은 실제 백업 목록에 존재하는 파일만 허용합니다.
- WordPress core `Plugin_Upgrader`를 사용해 로컬 ZIP을 `overwrite_package=true`로 복원합니다.
- 롤백 직전 현재 코드와 데이터도 다시 snapshot하여 되돌릴 지점을 하나 더 남깁니다.

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
- post type 데이터는 가능한 경우 기존 ID를 유지하고, 충돌 시 WordPress가 새 ID를 할당할 수 있습니다.
- 제품 고유 데이터는 export/import hook을 통해 확장할 수 있습니다.

Custom table은 제품별 스키마 의미가 다르므로 generic JSON import/export를 추측하지 않습니다. 대신 `custom_tables`는 완전 삭제 범위를 선언하고, 실제 portable table 데이터가 필요하면 제품 adapter와 별도 round-trip test를 추가합니다.

## 3. Backup storage and retention

- 코드 백업: 최근 3개
- 데이터 snapshot: 최근 5개
- 저장 디렉터리는 site salt 기반 비예측 토큰을 포함합니다.
- `index.php`, Apache `.htaccess`를 작성해 직접 접근 위험을 낮춥니다.
- Nginx/프록시/오브젝트 스토리지 환경에서는 서버 정책이 파일 접근을 우선하므로 운영 환경에서 backup 경로 비공개 여부를 별도 확인합니다.
- 백업에는 고객 데이터가 포함될 수 있으므로 공개 Git 저장소나 support ticket에 첨부하면 안 됩니다.

## 4. Uninstall policy

기본값은 항상 `preserve`입니다.

- `preserve`: 플러그인 파일만 제거하고 사용자 데이터를 유지합니다.
- `delete_all`: 사용자가 Maintenance 화면에서 명시적으로 선택한 경우에만 `uninstall.php`가 선언된 options/site options/post types/custom tables 및 표준 소유 maintenance 상태를 삭제합니다.
- EDD paid 제품은 `delete_all`일 때만 해당 제품의 EDD license option도 삭제합니다.
- 삭제 후 제품별 cleanup action을 호출해 추가 소유 데이터를 정리할 수 있습니다.

삭제는 비가역 작업이므로 제품 release 전 preserve/delete-all 양쪽 경로를 테스트해야 합니다.

## 5. System Information

모든 제품은 민감정보를 제외한 진단 정보를 제공합니다.

- plugin/standard/WordPress/PHP 버전
- locale, multisite, HTTPS
- PHP memory/upload 제한
- WP_DEBUG, DISABLE_WP_CRON 상태
- active theme
- code rollback backup/data snapshot 개수
- portable option/post type 개수

동일 정보는 NalApps Maintenance 화면과 WordPress Site Health > Info의 플러그인 전용 섹션에 노출합니다. DB 비밀번호, API key, license key, token, cookie, 고객 데이터, 절대 secret 값은 노출하지 않습니다.

## 6. Release gates

모든 제품은 다음 항목을 적용 가능한 범위에서 PASS해야 합니다.

- pre-update backup 생성과 실패 시 update block
- 실제 rollback ZIP root/버전 검증
- export → import round trip
- 잘못된 JSON/다른 plugin slug/과대 파일 import 거부
- 민감 option profile 거부
- uninstall preserve/delete-all 양쪽 검증
- system info redaction
- migration이 있는 제품의 code rollback/data restore 조합 E2E
- multisite 제품의 site/network 데이터 범위 검증
