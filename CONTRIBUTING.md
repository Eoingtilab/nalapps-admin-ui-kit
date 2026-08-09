# Contributing

이 저장소의 변경은 NalApps WordPress Plugin Standard의 재사용성을 높이되 기존 제품 계약을 불필요하게 깨뜨리지 않아야 합니다.

## 변경 원칙

1. 실제 제품 기능이나 URL을 추측하지 않습니다.
2. secret/customer data를 commit하지 않습니다.
3. 공통화 가능한 변경과 제품 전용 변경을 분리합니다.
4. 파괴적 변경은 migration/deprecation 계획을 함께 제시합니다.
5. 코드/문서/테스트를 먼저 완료하고 VERSION bump는 release의 마지막 변경으로 수행합니다.
6. Acceptance Gate의 관련 항목을 모두 검증합니다.

## Pull Request 최소 정보

- 변경 목적
- 영향 모듈
- backward compatibility
- security/privacy 영향
- 테스트 결과
- release/migration 필요 여부

기여물은 저장소의 공개 배포 정책과 라이선스 정책을 따라야 합니다.
