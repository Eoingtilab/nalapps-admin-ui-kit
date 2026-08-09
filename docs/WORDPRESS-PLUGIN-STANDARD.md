# NalApps WordPress Plugin Standard v1

NalApps WordPress 플러그인이 공통으로 따라야 하는 운영·보안·유지보수 표준입니다. UI와 제품 기능을 분리하고, 유료 플러그인은 EDD 모듈을 선택적으로 추가합니다.

## 1. 기본 헤더와 식별자

- 플러그인 폴더명/slug는 출시 후 변경하지 않는다.
- 메인 파일의 `Version`, `Requires at least`, `Requires PHP`, `Text Domain`을 유지한다.
- 자체 업데이트 제품은 WordPress.org 동명 플러그인과의 충돌 방지 정책을 문서화하고 필요 시 `Update URI`를 사용한다.
- 코드 버전과 DB schema version을 분리한다.

## 2. Security Contract

모든 상태 변경 요청은 다음을 모두 통과해야 한다.

1. 적절한 `current_user_can()` capability 검사
2. nonce 검증
3. 입력 타입/범위 validation
4. 입력 sanitize
5. 출력 context별 escape
6. SQL이 필요하면 `$wpdb->prepare()` 사용

금지:

- `$_GET`, `$_POST`, `$_REQUEST` 값을 검증 없이 저장/출력
- capability 없이 nonce만으로 권한을 판단
- 시리얼키/API 키/토큰/비밀번호를 로그나 화면에 원문 노출
- 임의의 원격 URL을 검증 없이 다운로드/실행

## 3. Compatibility Contract

- 최소 WordPress/PHP 버전을 플러그인 헤더와 runtime check에서 동일하게 유지한다.
- 필수 확장/의존성이 있으면 활성화 전에 명확히 실패시킨다.
- 다른 플러그인이 필수인 경우 가능한 환경에서는 `Requires Plugins`를 사용하고, 구형 WordPress 대응이 필요하면 별도 runtime guard를 둔다.
- 호환성 실패는 fatal error보다 관리자 안내와 기능 비활성화를 우선한다.

## 4. Database Migration Contract

- `plugin_version`과 `db_schema_version`을 분리한다.
- migration은 명시적인 버전 순서로 forward-only 실행한다.
- 각 migration은 재실행 가능한 idempotent 구조여야 한다.
- 성공한 migration 뒤에만 schema version을 갱신한다.
- 코드가 DB schema보다 오래된 downgrade 상황에서는 자동 downgrade하지 않고 차단/경고한다.
- migration 실패 시 다음 migration을 실행하지 않는다.

샘플: `wordpress/standard/class-nalapps-db-migrator.php`

## 5. Activation / Deactivation / Uninstall

활성화:
- 기본 옵션과 필요한 schema만 생성
- 중복 cron을 만들지 않음

비활성화:
- 예약 cron, transient, 임시 lock만 정리
- 사용자가 만든 콘텐츠/설정/라이선스 데이터는 삭제하지 않음

삭제(uninstall):
- 영구 데이터 삭제는 사용자가 명시적으로 선택한 경우에만 허용
- 기본 정책은 데이터 보존
- 공유 테이블/다른 플러그인 데이터는 절대 삭제 금지

샘플: `wordpress/standard/uninstall.php.template`

## 6. Cron Contract

- `wp_next_scheduled()`로 중복 예약 방지
- 비활성화 시 제품이 소유한 hook만 정확히 해제
- 관리/상태 화면에서 next run을 확인할 수 있게 함
- 외부 API 호출 cron은 timeout/cache/rate limit 정책을 별도로 둠

샘플: `wordpress/standard/class-nalapps-cron-manager.php`

## 7. Logging Contract

- 기본값 OFF 또는 최소 로그
- 디버그/지원 목적일 때만 명시적으로 활성화
- secret-looking key는 재귀적으로 마스킹
- 로그 개수/크기에 상한을 둠
- 고객지원 화면에서 로그 전체를 무제한 노출하지 않음
- 로그 삭제 기능을 제공할 수 있음

샘플: `wordpress/standard/class-nalapps-safe-logger.php`

## 8. External HTTP Contract

모든 외부 요청은 다음을 지킨다.

- HTTPS 우선
- `sslverify => true`
- 명시적인 timeout
- 무제한 retry 금지
- transient/object cache 활용
- 응답 HTTP status와 JSON/schema validation
- 장애 시 graceful degradation
- secret query/body 값 로그 금지

EDD 업데이트는 `docs/EDD-LICENSE-AND-UPDATES.md`를 추가로 따른다.

## 9. System Status Contract

운영 플러그인은 고객지원이 필요한 수준이라면 읽기 전용 상태 화면을 제공한다.

권장 표시:
- 플러그인 버전
- WordPress/PHP 버전
- DB schema/target version
- HTTPS 여부
- cron next run
- 라이선스 상태(키 원문 금지)
- 업데이트 최신/현재 버전
- 마지막 원격 확인 시각
- 필수 dependency 상태

금지 표시:
- license key 원문
- API key/token/password
- 인증 cookie/session
- 불필요한 개인정보

샘플: `wordpress/standard/class-nalapps-system-status.php`

## 10. Multisite

- 사이트별 설정인지 네트워크 설정인지 사전에 결정한다.
- `get_option()`과 `get_site_option()`을 혼용하지 않는다.
- network activation을 지원하지 않는다면 명시적으로 문서화한다.
- 라이선스 activation limit과 multisite 정책을 제품별로 문서화한다.

## 11. Internationalization

- 사용자 노출 문자열은 text domain 기반으로 작성한다.
- 날짜/시간/숫자는 WordPress locale 함수를 우선한다.
- 한국어 전용 제품이어도 데이터 구조에 언어 의존 문자열을 하드코딩하지 않는다.

## 12. Release & Update

- 배포용 ZIP의 최상위 폴더명은 canonical plugin slug와 정확히 일치한다.
- Composer dependency가 있으면 Source ZIP을 배포 파일로 사용하지 않는다.
- production dependency 포함 Release Asset을 만든다.
- 유료 EDD 제품은 WordPress 기본 업데이트 알림 + 제품 내부 업데이트 확인을 함께 지원하는 것을 NalApps 기본 정책으로 한다.
- 배포 전 PHP syntax, 핵심 기능, migration, uninstall preservation, update package를 검증한다.

## 13. Required Verification

출시 전 최소 검증:

- PHP syntax / static sanity
- 활성화/비활성화/재활성화
- 권한 없는 사용자의 mutation 차단
- nonce 실패 차단
- 기존 데이터 보존
- migration idempotency
- cron 중복 없음
- 로그 secret redaction
- system status에 secret 없음
- 최신/구버전 업데이트 경로
- 모바일/태블릿/데스크톱 관리자 UI
- 기능 회귀 없음

최종 판정은 `docs/ACCEPTANCE-CHECKLIST.md`를 모두 충족해야 PASS로 한다.
