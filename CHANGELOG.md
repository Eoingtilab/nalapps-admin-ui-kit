# Changelog

## 2.1.0
- 선택형 `EDD License & Hybrid Updates` 공통 모듈 추가
- WordPress 플러그인 페이지 기본 업데이트 알림용 updater template 추가
- 플러그인 내부 업데이트 화면/수동 확인/즉시 업데이트 template 추가
- EDD Software Licensing `get_version` API 계약 및 검증 기준 문서화
- Composer `vendor/` 포함 GitHub Release ZIP 생성 workflow template 추가
- 유료 플러그인 배포 시 Source ZIP 사용 금지 및 Update File 검증 규칙 추가
- UI 디자인 계층과 EDD 라이선스/업데이트 비즈니스 계층은 분리 유지

## 2.0.1
- Pretendard Variable을 NalApps 관리자 UI 기본 폰트로 지정
- Pretendard 공식 jsDelivr variable dynamic subset 웹폰트 사용
- 본문/폼/테이블 기본 굵기를 400으로 조정
- 버튼/내비게이션/라벨은 550~600 수준으로 완화
- 페이지 제목/KPI 핵심 수치는 700으로 제한
- 기존 800~900 중심의 과도한 굵기 사용 제거를 위한 typography override 계층 추가
- 기존 디자인/레이아웃/WordPress Adapter 계약은 유지

## 2.0.0
- Blue/Navy/Soft Blue/Neutral Gray 기반 NalApps 관리자 디자인 표준 확정
- WordPress 전용 UI Adapter 템플릿 추가
- 공통 상단 플러그인 타이틀/내부 내비게이션/페이지 헤더 계약 추가
- Dashboard/List/Add/Edit/Settings 화면 적용 규칙 추가
- WordPress button/postbox/list-table/form 충돌 대응 추가
- 외부 CSS에 의한 primary button 색상 오염 방지 규칙 추가
- 관리 홈 과도한 고정 높이/빈 공간 방지 규칙 추가
- DO-NOT 및 Acceptance Checklist 추가
