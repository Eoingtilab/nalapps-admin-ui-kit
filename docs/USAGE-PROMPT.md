# 다른 플러그인에 적용할 때 사용하는 표준 지시문

NalApps Admin UI는 GitHub 저장소 `Eoingtilab/nalapps-admin-ui-kit`의 최신 안정 버전을 기준으로 적용한다.

필수 규칙:
1. UI를 임의로 재해석하거나 비슷하게 새로 디자인하지 않는다.
2. 저장소의 `assets/css/nalapps-admin-ui.css`, WordPress Adapter, DESIGN-TOKENS, WORDPRESS-INTEGRATION, DO-NOT, ACCEPTANCE-CHECKLIST를 먼저 읽고 그대로 따른다.
3. 상단 플러그인 타이틀/브랜드, 내부 내비게이션, 페이지 헤더를 모든 대상 관리자 화면에서 일관되게 적용한다.
4. 관리 홈/목록/새로 추가/수정/설정 화면의 UI를 같은 디자인 시스템으로 통일한다.
5. 기본 색상은 Blue/Navy/Soft Blue/Neutral Gray만 사용하며 Success/Warning/Danger는 실제 상태 표현에만 사용한다.
6. UI 적용 때문에 제품의 저장, CRUD, API, 라이선스, 업데이트, 프런트 출력 로직을 변경하지 않는다.
7. 다른 플러그인 또는 WordPress 코어 CSS와 충돌하지 않도록 대상 관리자 화면에만 Kit assets를 enqueue 한다.
8. 완료 전 ACCEPTANCE-CHECKLIST 전체를 검증하고 결과를 보고한다.
9. 적용한 NalApps Admin UI Kit 버전을 플러그인 소스 또는 문서에 기록한다.
