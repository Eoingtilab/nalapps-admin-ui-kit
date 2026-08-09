# Changelog

## 2.3.0
- EOINGTI Lab/어잉티연구소 canonical company profile 추가
- 개발사 홈페이지 기본값을 `https://eoingti.com/`로 고정
- GitHub 조직/owner 기본값을 `Eoingtilab`로 고정
- 플러그인 저장소 기본 규칙 `Eoingtilab/<plugin-slug>` 추가
- WordPress plugin header 공통 template 추가
- README 공통 template 추가
- Plugin URI / Author URI / GitHub source / readme.txt / 지원·개인정보 표기 계약 추가
- 존재하지 않는 제품/지원 URL을 추측해 생성하지 않는 fail-safe 규칙 추가
- Acceptance Checklist에 회사 메타데이터/README/release version consistency 검증 추가

## 2.2.0
- NalApps Admin UI Kit을 `NalApps WordPress Plugin Standard Kit`으로 확장
- 모든 플러그인 공통 운영 표준 문서 `docs/WORDPRESS-PLUGIN-STANDARD.md` 추가
- capability + nonce 중심 보안 helper와 호환성/runtime status core template 추가
- 코드 버전과 DB schema version을 분리하는 forward-only deterministic migration template 추가
- 중복 예약 방지 및 비활성화 정리용 Cron manager template 추가
- secret redaction 및 bounded retention을 적용한 opt-in logger template 추가
- secret을 노출하지 않는 읽기 전용 System Status page template 추가
- activation/deactivation/uninstall 데이터 보존 정책과 `uninstall.php.template` 추가
- 표준 모듈 적용 예제 `wordpress/standard/bootstrap-example.php` 추가
- Acceptance Checklist를 security/database/cron/logging/status/lifecycle/release까지 확장
- 기존 Admin UI 및 EDD License & Hybrid Updates 모듈은 독립 계층으로 그대로 유지

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
