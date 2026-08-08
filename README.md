# NalApps Admin UI Kit v2.0

어잉티연구소/NalApps WordPress 플러그인용 관리자 UI 표준입니다.

## 왜 v2.0인가
기존 Kit는 CSS 샘플 중심이라 실제 플러그인에 적용할 때 화면 판별, body class, 상단 플러그인 헤더, WordPress 기본 컴포넌트 충돌, 외부 CSS 우선순위를 매번 다시 판단해야 했습니다. v2.0은 **디자인 + WordPress 연결 계약 + Adapter + 화면 템플릿 + 금지사항 + 검수 체크리스트**를 하나의 표준으로 묶었습니다.

## 기본 적용 순서
1. `assets/css/nalapps-admin-ui.css`와 `assets/js/nalapps-admin-ui.js`를 대상 플러그인에 복사합니다.
2. `wordpress/class-nalapps-admin-ui-adapter.php`를 복사하고 namespace, plugin file/version 상수, page prefix, post type, 메뉴 URL을 실제 플러그인 값으로 바꿉니다.
3. Adapter를 플러그인 bootstrap에서 1회 생성합니다.
4. 관리 홈은 `wordpress/dashboard-template.php` 구조를 기준으로 만듭니다.
5. 설정 화면은 `wordpress/settings-template.php`를 기준으로 만듭니다.
6. `docs/ACCEPTANCE-CHECKLIST.md`를 모두 통과한 뒤 완료 처리합니다.

## 다른 플러그인 개발 시 지시 방법
개발자/AI에게 아래처럼 지시하면 됩니다.

> NalApps Admin UI는 `Eoingtilab/nalapps-admin-ui-kit`의 최신 안정 버전을 기준으로 적용한다. 디자인을 임의로 재해석하지 말고 제공 Adapter, CSS 클래스, WordPress Integration Contract, DO-NOT, Acceptance Checklist를 따른다. 제품 기능/저장/API/프런트 로직은 UI 적용 때문에 변경하지 않는다.

## 버전 정책
- `2.x`: 현재 Blue 기반 WordPress Admin 디자인 시스템
- 파괴적 클래스/Adapter 계약 변경: major 증가
- 새 컴포넌트: minor 증가
- CSS/문서 오류 수정: patch 증가
