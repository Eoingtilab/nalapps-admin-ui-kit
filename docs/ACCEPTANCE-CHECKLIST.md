# 적용 완료 체크리스트

## Company / Metadata
- [ ] Author가 `EOINGTI Lab`로 통일되어 있다.
- [ ] Author URI가 `https://eoingti.com/`이다.
- [ ] GitHub 저장소 owner가 `Eoingtilab`이다.
- [ ] README에 EOINGTI Lab/어잉티연구소, eoingti.com, GitHub 저장소가 표시된다.
- [ ] Plugin URI는 실제 제품 페이지 또는 `https://eoingti.com/`이며 존재하지 않는 URL을 추측해 넣지 않았다.
- [ ] Version / Stable tag / GitHub tag·release / EDD version이 출시 시 서로 일치한다.

## Admin UI
- [ ] 상단에 플러그인명과 NalApps 브랜드 영역이 보인다.
- [ ] 관리 홈/목록/새로 추가/수정/설정 화면에서 같은 내부 메뉴가 유지된다.
- [ ] 기본 palette가 Blue/Navy/Soft Blue/Neutral Gray로 통일되어 있다.
- [ ] 일반 버튼이 초록/주황/보라로 오염되지 않는다.
- [ ] 안내 박스는 기본 Soft Blue이며 경고/오류일 때만 상태색을 사용한다.
- [ ] 관리 홈 카드 높이가 콘텐츠에 맞고 큰 빈 공간이 없다.
- [ ] WordPress postbox/list-table/form이 NalApps 화면에서만 정규화된다.
- [ ] 1440px/1024px/모바일 폭에서 레이아웃이 무너지지 않는다.

## Security
- [ ] 모든 mutation이 capability + nonce를 함께 검사한다.
- [ ] 입력은 타입/범위를 validate한 뒤 sanitize한다.
- [ ] 사용자/원격 데이터 출력은 context별 escape한다.
- [ ] 직접 SQL은 `$wpdb->prepare()` 또는 안전한 WP API를 사용한다.
- [ ] license/API key/token/password가 HTML, 로그, 예외 메시지에 원문 노출되지 않는다.

## Compatibility & Lifecycle
- [ ] 플러그인 헤더와 runtime의 최소 WordPress/PHP 버전이 일치한다.
- [ ] 활성화/비활성화/재활성화가 fatal 없이 동작한다.
- [ ] 비활성화만으로 사용자 콘텐츠/설정이 삭제되지 않는다.
- [ ] uninstall 데이터 삭제는 명시적 opt-in이며 기본값은 보존이다.
- [ ] multisite 지원 여부와 option/site_option 범위가 명확하다.

## Database
- [ ] 코드 버전과 DB schema version이 분리되어 있다(해당 시).
- [ ] migration은 순서가 결정적이고 forward-only이다.
- [ ] migration을 두 번 실행해도 데이터가 중복/손상되지 않는다.
- [ ] migration 실패 후 schema version을 성공한 것처럼 올리지 않는다.
- [ ] 오래된 코드로 DB schema를 자동 downgrade하지 않는다.

## Cron / External HTTP / Logging
- [ ] cron 중복 예약이 없다.
- [ ] 비활성화 시 제품 소유 cron만 해제한다.
- [ ] 외부 HTTP는 timeout, SSL verify, 응답 검증, cache 정책이 있다.
- [ ] 무제한 retry가 없다.
- [ ] debug log는 bounded retention을 사용하고 secret을 마스킹한다.

## System Status
- [ ] 운영형 플러그인은 필요한 경우 읽기 전용 System Status를 제공한다.
- [ ] 버전/DB/Cron/라이선스 상태/마지막 원격 확인 정보를 진단할 수 있다.
- [ ] System Status에 license key/API key/token/password가 표시되지 않는다.

## EDD License & Updates (유료 플러그인)
- [ ] EDD Store URL, Download ID, canonical plugin slug/folder가 정확하다.
- [ ] 배포 ZIP 최상위 폴더명이 canonical plugin slug와 정확히 일치한다.
- [ ] Composer dependency가 있으면 `vendor/` 포함 Release Asset을 사용한다.
- [ ] WordPress 플러그인 페이지에서 새 버전 업데이트 알림을 받을 수 있다.
- [ ] 플러그인 내부 업데이트 화면에서도 현재/최신 버전과 업데이트 상태를 확인할 수 있다.
- [ ] 유효 라이선스가 필요한 다운로드는 라이선스 상태를 우회하지 않는다.

## Regression & Release
- [ ] 저장/CRUD/API/프런트 기능 회귀가 없다.
- [ ] PHP syntax/static sanity 검사를 통과한다.
- [ ] 구버전 → 최신버전 실제 업데이트 경로를 최소 1회 검증했다.
- [ ] 기존 데이터가 업데이트 후 유지된다.
- [ ] Plugin Standard 버전을 플러그인 문서나 소스 주석에 기록했다.
- [ ] README/소스/릴리스 자산에 secret 또는 개인 인증정보가 없다.

모든 적용 제품은 `docs/COMPANY-PROFILE.md`, `docs/PLUGIN-METADATA-STANDARD.md`, `docs/WORDPRESS-PLUGIN-STANDARD.md`와 제품별 추가 계약을 함께 따른다.
