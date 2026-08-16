# NalApps Free License Contract

NalApps `product_type: free` 제품은 유료 EDD 라이선스 제품과 완전히 분리된 계약을 사용합니다.

## 필수 Profile 계약

- `product_type`은 `free`여야 합니다.
- `license_required`는 반드시 `false`여야 합니다.
- 시리얼 키, 라이선스 키, 원격 활성화 서버, 활성화/비활성화 API를 요구하지 않습니다.

## Runtime 계약

무료 제품의 라이선스 런타임은 설치되어 활성화된 플러그인 안에서 다음 상태를 항상 반환해야 합니다.

- 표시 라이선스: `무료 (Free)`
- 표시 상태: `활성 (Active)`
- 내부 상태: `free`
- `is_valid()`: 항상 `true`
- `key()`: 빈 문자열

무료 제품의 핵심 기능이나 업데이트 가능 여부를 라이선스 키 입력 또는 외부 라이선스 서버 응답에 종속시키지 않습니다.

## UI 계약

라이선스 화면이 존재하는 경우 다음을 명확히 보여야 합니다.

- 라이선스: 무료
- 현재 상태: 활성
- 시리얼 키 입력란 없음
- 활성화 버튼 없음
- 비활성화 버튼 없음

## Release Gate

Canonical scaffold와 CI는 최소한 다음을 검증합니다.

- `license_required=false`
- `includes/class-license.php` 생성
- `status()`가 `free` 반환
- `is_valid()`가 항상 `true` 반환
- 무료/활성 UI 문구 존재
- `activate_license`, `deactivate_license`, `license_key`, `Serial key` 같은 유료 활성화 흐름이 무료 런타임에 없음
- 생성된 main plugin이 free-license runtime을 실제 로드함
- manifest에 `free_license_display`, `free_license_always_active` 모듈과 `free_license_ui`, `free_license_always_active` release gate가 기록됨

## 업데이트 계약

무료 라이선스와 업데이트 배포는 별개의 문제입니다. 무료 제품도 업데이트 ZIP은 검증된 배포 채널에서 제공해야 하며, GitHub Releases를 사용하는 경우 Source Code ZIP이 아니라 제품용 Release Asset ZIP과 checksum을 사용합니다. Release Asset이 없으면 업데이트가 가능한 것으로 표시하거나 설치를 시도해서는 안 됩니다.
