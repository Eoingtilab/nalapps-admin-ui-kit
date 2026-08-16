# NalApps License Modes Contract

NalApps 제품 라이선스는 다음 세 가지 모드로 구분합니다.

1. `paid` — 유료 라이선스
2. `free_registered` — 무료이지만 라이선스 키 등록/활성화가 필요한 제품
3. `free_download` — 라이선스 등록 없이 자유 다운로드하여 사용하는 무료 제품

`product_type`은 제품/배포 유형을 나타내고, 실제 라이선스 동작은 `license_mode`와 `license_required`가 결정합니다.

## 1. paid

- 대표 profile: `product_type: edd_paid`
- `license_mode: paid`
- `license_required: true`
- 현재 공통 표준의 등록/활성화 backend는 EDD Software Licensing입니다.
- `edd_download_id`, `edd_store_url`이 필요합니다.
- 라이선스 화면에는 `유료 (Paid)`가 표시됩니다.
- 시리얼 키 입력, 활성화, 상태 확인, 비활성화가 제공됩니다.
- 유효한 라이선스 여부에 따라 라이선스가 필요한 업데이트/권한을 판단할 수 있습니다.

## 2. free_registered

- 대표 profile: `product_type: free`
- `license_mode: free_registered`
- `license_required: true`
- 제품 가격은 무료지만 라이선스 키 등록은 필요합니다.
- 현재 공통 표준의 등록/활성화 backend는 EDD Software Licensing입니다.
- `edd_download_id`, `edd_store_url`이 필요합니다.
- 라이선스 화면에는 `무료 (라이선스 등록)`이 표시됩니다.
- 시리얼 키 입력, 활성화, 상태 확인, 비활성화가 제공됩니다.
- 무료라는 이유만으로 자동 활성 상태가 되지 않습니다. 실제 등록 결과가 `valid` 또는 `active`여야 활성 상태입니다.

## 3. free_download

- 대표 profile: `product_type: free`
- `license_mode: free_download`
- `license_required: false`
- 시리얼 키, 원격 활성화 서버, 활성화/비활성화 절차가 없습니다.
- 라이선스 화면에는 `무료 (Free)`가 표시됩니다.
- 현재 상태는 항상 `활성화 (Active)`로 표시됩니다.
- 내부 상태는 `free`, `is_valid()`는 항상 `true`, `key()`는 빈 문자열입니다.
- 핵심 기능이나 업데이트 가능 여부를 라이선스 키 존재 여부에 종속시키면 안 됩니다.

NalApps Easy SMTP처럼 그냥 내려받아 설치하는 무료 플러그인/유틸은 이 `free_download` 모드를 사용합니다.

## Backward compatibility

기존 profile에 `license_mode`가 없는 경우 validator가 다음과 같이 정규화합니다.

- `product_type: edd_paid` → `paid`
- `license_required: true` → `free_registered`
- 그 외 기존 무료/비공개 profile → `free_download`

`license_required`가 없는 기존 profile도 선택된 모드에 따라 자동 정규화합니다. 따라서 기존 4.6 계열 profile을 즉시 파괴하지 않으면서, 새로 생성되는 profile에는 명시적인 세 가지 라이선스 모드를 기록할 수 있습니다.

## Update source

라이선스와 업데이트 배포 채널은 별개 계약입니다.

- `update_source: edd` — EDD 라이선스/버전 endpoint 기반
- `update_source: github_releases` — GitHub Releases 기반

GitHub Releases를 사용하는 경우 `update_repository`를 명시합니다. 설치/업데이트용 패키지는 GitHub 자동 생성 Source Code ZIP이 아니라 검증된 제품용 Release Asset ZIP을 사용해야 하며, checksum 검증이 가능한 구조를 권장합니다. Release Asset이 누락되면 설치 가능한 업데이트로 취급하면 안 됩니다.

## Release gate

Canonical scaffold와 CI는 최소한 다음을 검증합니다.

- 세 가지 `license_mode` 값만 허용
- `paid`, `free_registered`는 `license_required=true`
- `free_download`는 `license_required=false`
- `paid`, `free_registered`는 등록형 라이선스 metadata와 활성화 UI를 가짐
- `free_registered` 라이선스 화면은 무료 등록형임을 명확히 표시
- `free_download`는 키 입력/활성화 API가 없고 항상 활성 상태
- 생성된 main plugin이 각 모드에 필요한 runtime을 실제 로드함
- manifest에 모드별 required module/release gate가 기록됨
- legacy profile 정규화 회귀 테스트 통과
