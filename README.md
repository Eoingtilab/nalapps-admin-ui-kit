# NalApps WordPress Plugin Standard Kit v2.2

어잉티연구소/NalApps WordPress 플러그인용 **관리자 UI + 유료 플러그인 배포 + 운영 품질 표준**입니다.

## 포함 범위

v2.2부터는 세 계층을 분리해 제공합니다.

### 1. Admin UI
- Pretendard Variable 기반 타이포그래피
- Blue / Navy / Soft Blue / Neutral Gray 디자인 토큰
- WordPress 전용 UI Adapter
- 관리 홈 / 목록 / 추가 / 수정 / 설정 화면 규칙
- WordPress 기본 컴포넌트 충돌 대응

### 2. 선택형 EDD License & Hybrid Update Module
유료 플러그인에서 필요할 때만 적용합니다.

- EDD Software Licensing SDK 연동
- WordPress `플러그인` 화면 기본 업데이트 알림
- 플러그인 내부 `업데이트` 화면
- 현재 버전 / 최신 버전 표시
- 수동 `업데이트 확인`
- 유효 라이선스에서 내부 `지금 업데이트`
- Composer `vendor/` 포함 GitHub Release ZIP 빌드 템플릿

자세한 내용은 `docs/EDD-LICENSE-AND-UPDATES.md`를 따릅니다.

### 3. WordPress Plugin Standard
모든 NalApps 플러그인에 공통 적용할 운영 품질 계층입니다.

- capability + nonce 기반 mutation 보안 계약
- 입력 validation/sanitize, 출력 escape 규칙
- 최소 WordPress/PHP 호환성 체크
- 코드 버전과 DB schema version 분리
- forward-only/idempotent DB migration template
- 중복 방지 Cron manager
- secret redaction + bounded retention logger
- 읽기 전용 System Status page
- activation/deactivation/uninstall 데이터 보존 정책
- multisite / i18n / 외부 HTTP / release 검증 규칙

핵심 문서: `docs/WORDPRESS-PLUGIN-STANDARD.md`

재사용 코드: `wordpress/standard/`

## 기본 적용 순서

1. `assets/css/nalapps-admin-ui.css`와 Typography 계층을 대상 플러그인에 적용합니다.
2. `wordpress/class-nalapps-admin-ui-adapter.php`를 복사하고 실제 plugin 값으로 치환합니다.
3. Dashboard/Settings 템플릿을 기준으로 관리자 화면을 만듭니다.
4. `wordpress/standard/`에서 필요한 운영 표준 모듈을 적용합니다.
5. `bootstrap-example.php`의 placeholder를 실제 plugin constants/options/menu slug로 치환합니다.
6. 유료 EDD 제품이면 `wordpress/edd/` 하이브리드 업데이트 모듈을 추가 적용합니다.
7. Store URL, EDD Download ID, canonical slug/folder, plugin file, version constant를 실제 값으로 지정합니다.
8. `docs/ACCEPTANCE-CHECKLIST.md`, `docs/WORDPRESS-PLUGIN-STANDARD.md`, 해당 제품별 추가 계약을 모두 검증합니다.

## 다른 플러그인 개발 시 지시 방법

> `Eoingtilab/nalapps-admin-ui-kit`의 최신 안정 태그를 기준으로 NalApps WordPress Plugin Standard를 적용한다. 디자인을 임의로 재해석하지 말고 Admin UI Adapter/디자인 토큰/WordPress Integration Contract/DO-NOT/Acceptance Checklist를 따른다. `wordpress/standard/`의 보안·호환성·DB migration·Cron·logging·System Status·uninstall 정책을 제품 특성에 맞게 적용한다. 유료 EDD 플러그인이면 `wordpress/edd/`의 하이브리드 업데이트 모듈도 적용해 WordPress 플러그인 페이지와 플러그인 내부 업데이트 화면을 모두 지원한다. 제품 기능/저장/API/프런트 로직은 공통 표준 적용 때문에 임의 변경하지 않는다.

## 버전 정책

- 파괴적 클래스/Adapter 계약 변경: major 증가
- 새 컴포넌트/공통 모듈: minor 증가
- CSS/문서 오류 수정: patch 증가
