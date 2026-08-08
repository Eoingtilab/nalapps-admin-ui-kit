# WordPress Integration Contract

## 필수 연결
1. `admin_enqueue_scripts`에서 대상 플러그인 화면에만 CSS/JS를 로드합니다.
2. `admin_body_class`에 `nalapps-admin-screen`을 추가합니다.
3. 상단 플러그인 타이틀/내부 내비게이션/페이지 헤더를 공통 Adapter에서 출력합니다.
4. Dashboard/List/Add/Edit/Settings 모든 화면이 같은 Adapter를 사용해야 합니다.
5. UI Adapter는 비즈니스 로직, 저장 로직, API 호출 로직을 소유하지 않습니다.

## WordPress 기본 UI 대응
Kit은 `.button`, `.button-primary`, `.postbox`, `.wp-list-table`, 입력 폼을 대상 화면 안에서만 정규화합니다.

## CSS 충돌 방지
- 전역 admin enqueue 금지
- `body.nalapps-admin-screen` 범위 밖의 WordPress 관리자 UI를 변경하지 않음
- 다른 플러그인이 강한 버튼 스타일을 주입해도 primary button이 파랑으로 유지되도록 대상 범위 selector를 사용
