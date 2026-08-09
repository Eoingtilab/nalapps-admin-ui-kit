# NalApps Admin UI Kit v2.1

어잉티연구소/NalApps WordPress 플러그인용 관리자 UI 및 유료 플러그인 배포 표준입니다.

## 포함 범위

v2.1부터는 두 계층을 분리해 제공합니다.

### 1. Admin UI
- Pretendard Variable 기반 타이포그래피
- Blue / Navy / Soft Blue / Neutral Gray 디자인 토큰
- WordPress 전용 UI Adapter
- 관리 홈 / 목록 / 추가 / 수정 / 설정 화면 규칙
- WordPress 기본 컴포넌트 충돌 대응

### 2. 선택형 EDD License & Update Module
유료 플러그인에서 필요할 때만 적용합니다.

- EDD Software Licensing SDK 연동
- WordPress `플러그인` 화면 기본 업데이트 알림
- 플러그인 내부 `업데이트` 화면
- 현재 버전 / 최신 버전 표시
- 수동 `업데이트 확인`
- 유효 라이선스에서 내부 `지금 업데이트`
- Composer `vendor/` 포함 GitHub Release ZIP 빌드 템플릿

자세한 내용은 `docs/EDD-LICENSE-AND-UPDATES.md`를 따릅니다.

## 기본 적용 순서

1. `assets/css/nalapps-admin-ui.css`와 Typography 계층을 대상 플러그인에 적용합니다.
2. `wordpress/class-nalapps-admin-ui-adapter.php`를 복사하고 실제 plugin 값으로 치환합니다.
3. Dashboard/Settings 템플릿을 기준으로 관리자 화면을 만듭니다.
4. 유료 EDD 제품이면 `wordpress/edd/` 모듈을 추가 적용합니다.
5. Store URL, EDD Download ID, slug, plugin file, version constant, license option prefix를 실제 값으로 지정합니다.
6. `docs/ACCEPTANCE-CHECKLIST.md`와 `docs/EDD-LICENSE-AND-UPDATES.md`의 PASS 조건을 검증합니다.

## 다른 플러그인 개발 시 지시 방법

> `Eoingtilab/nalapps-admin-ui-kit`의 최신 안정 태그를 기준으로 NalApps Admin UI를 적용한다. 디자인을 임의로 재해석하지 말고 Adapter, 디자인 토큰, WordPress Integration Contract, DO-NOT, Acceptance Checklist를 따른다. 유료 EDD 플러그인이면 `wordpress/edd/`의 하이브리드 업데이트 모듈도 적용해 WordPress 플러그인 페이지와 플러그인 내부 업데이트 화면을 모두 지원한다. 제품 기능/저장/API/프런트 로직은 UI 적용 때문에 변경하지 않는다.

## 버전 정책

- 파괴적 클래스/Adapter 계약 변경: major 증가
- 새 컴포넌트/공통 모듈: minor 증가
- CSS/문서 오류 수정: patch 증가
