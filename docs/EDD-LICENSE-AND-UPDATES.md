# NalApps EDD License & Hybrid Updates

NalApps 유료 WordPress 플러그인은 UI Kit의 디자인 계층과 별도로 **선택형 EDD 배포 모듈**을 사용할 수 있습니다.

## 목표

하나의 EDD Software Licensing 제품을 기준으로 다음 두 업데이트 UX를 동시에 제공합니다.

1. WordPress `플러그인` 화면의 기본 업데이트 알림/업데이트
2. 플러그인 내부 `업데이트` 화면의 현재 버전·최신 버전·수동 확인·즉시 업데이트

## 필수 설정값

대상 플러그인마다 아래 값만 바꿉니다.

- Store URL: 예) `https://app.nal.la`
- EDD Download ID
- Plugin slug
- Main plugin file
- Plugin version constant
- SDK license option prefix

## 권장 구조

- EDD 공식 Software Licensing SDK: 라이선스 입력/활성화/검증 및 기본 업데이트 통합
- `wordpress/edd/class-nalapps-edd-update-manager.php`: 동일한 `get_version` API를 사용해 플러그인 내부 업데이트 화면과 WordPress 업데이트 transient를 보강
- GitHub Release workflow: Composer `vendor/`가 포함된 배포 ZIP 생성

## EDD API 계약

업데이트 확인은 Software Licensing API의 `get_version` 요청을 사용합니다.

필수/권장 파라미터:

- `edd_action=get_version`
- `item_id`
- `license` — 라이선스가 있으면 포함
- `url`
- `php_version`
- `wp_version`

라이선스를 생략해도 최신 버전 정보는 조회할 수 있지만 다운로드 URL은 제공되지 않을 수 있습니다. 실제 자동 업데이트에는 활성 라이선스와 올바른 Update File이 필요합니다.

## 배포 규칙

1. 코드/CSS/문서/Composer 변경을 먼저 완료합니다.
2. 배포 ZIP에는 `vendor/easy-digital-downloads/edd-sl-sdk/`가 반드시 포함되어야 합니다.
3. ZIP 최상위 폴더명은 실제 WordPress plugin directory와 동일해야 합니다.
4. EDD Download의 Version Number와 Update File을 새 릴리스에 맞춥니다.
5. **버전 번호는 마지막에 올립니다.** 버전 변경으로 Git 태그가 자동 생성되는 저장소에서는 특히 중요합니다.
6. 새 버전이 실제 설치본보다 높은 상태에서 WordPress `플러그인` 화면과 플러그인 내부 `업데이트` 화면을 모두 검증합니다.

## PASS 기준

- 유효 라이선스에서 EDD `get_version` 응답의 최신 버전을 읽을 수 있음
- 현재 버전보다 최신이면 WordPress 플러그인 목록에 업데이트가 표시됨
- 동일한 최신 버전이 플러그인 내부 업데이트 화면에도 표시됨
- 내부 `업데이트 확인` 버튼이 캐시를 비우고 재조회함
- 활성 라이선스와 다운로드 URL이 있으면 내부에서 업데이트 실행 가능
- 최신 버전과 현재 버전이 같으면 업데이트 버튼이 나타나지 않음
- 서버 오류가 플러그인의 기존 데이터나 설정을 삭제하지 않음

## 금지

- GitHub Source ZIP을 Composer 기반 유료 플러그인의 EDD Update File로 사용하지 않음
- UI Kit의 CSS와 EDD 제품 비즈니스 로직을 한 클래스에 섞지 않음
- EDD Download ID 또는 Store URL을 추측하지 않음
- 라이선스 키를 Git에 저장하지 않음
