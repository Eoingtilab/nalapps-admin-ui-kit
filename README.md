# NalApps WordPress Plugin Standard Kit v2.3

어잉티연구소/NalApps WordPress 플러그인용 **관리자 UI + 유료 플러그인 배포 + 운영 품질 + 개발사 메타데이터 표준**입니다.

## Canonical Company Profile

모든 NalApps 플러그인은 별도 지시가 없으면 다음 기본값을 사용합니다.

- 개발사: `EOINGTI Lab / 어잉티연구소`
- Author: `EOINGTI Lab`
- Author URI / 개발사 홈페이지: `https://eoingti.com/`
- GitHub 조직: `https://github.com/Eoingtilab`
- GitHub owner: `Eoingtilab`
- 기본 저장소: `https://github.com/Eoingtilab/<plugin-slug>`
- Plugin URI: 실제 제품 페이지가 있으면 해당 URL, 없으면 `https://eoingti.com/`

Canonical source: `docs/COMPANY-PROFILE.md`

## 포함 범위

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

### 4. Metadata & Documentation Standard
플러그인마다 반복 입력하던 개발사/저장소/README 정보를 표준화합니다.

- `docs/COMPANY-PROFILE.md`: 회사/브랜드/홈페이지/GitHub canonical defaults
- `docs/PLUGIN-METADATA-STANDARD.md`: Header/Plugin URI/GitHub/README/readme.txt 계약
- `wordpress/standard/plugin-header.template.php`: WordPress 플러그인 헤더 템플릿
- `wordpress/standard/README.template.md`: 공개 저장소 README 템플릿

## 기본 적용 순서

1. 회사/브랜드 기본값은 `docs/COMPANY-PROFILE.md`를 자동 적용합니다.
2. 플러그인 헤더는 `wordpress/standard/plugin-header.template.php`를 기준으로 생성합니다.
3. GitHub 저장소는 기본적으로 `Eoingtilab/<plugin-slug>`를 사용합니다.
4. README는 `wordpress/standard/README.template.md`를 기준으로 작성합니다.
5. `assets/css/nalapps-admin-ui.css`와 Typography 계층을 적용합니다.
6. `wordpress/class-nalapps-admin-ui-adapter.php`를 실제 plugin 값으로 치환합니다.
7. `wordpress/standard/`에서 필요한 운영 표준 모듈을 적용합니다.
8. 유료 EDD 제품이면 `wordpress/edd/` 하이브리드 업데이트 모듈을 추가 적용합니다.
9. `docs/ACCEPTANCE-CHECKLIST.md`와 제품별 계약을 모두 검증합니다.

## 다른 플러그인 개발 시 지시 방법

가급적 긴 지시문 대신 아래 한 문장만 사용합니다.

> `Eoingtilab/nalapps-admin-ui-kit`의 최신 안정 태그 기준 **NalApps WordPress Plugin Standard 전체를 적용한다.** 회사/개발사 메타데이터, eoingti.com 개발사 사이트, Eoingtilab GitHub 조직, Plugin Header, README, Admin UI, 보안, 호환성, lifecycle, migration, cron, logging, system status, release/acceptance 기준을 자동 적용하고, 유료 EDD 제품이면 라이선스와 하이브리드 업데이트 모듈까지 적용한다. 실제 존재하지 않는 제품/지원 URL은 만들지 않는다.

제품별로 정말 필요한 값만 추가로 지정하면 됩니다: 제품명, slug, 핵심 기능, 무료/유료 여부, 외부 API/DB/Cron 사용 여부, EDD Download ID 등.

## 버전 정책

- 파괴적 클래스/Adapter 계약 변경: major 증가
- 새 컴포넌트/공통 모듈/표준 계층: minor 증가
- CSS/문서 오류 수정: patch 증가
