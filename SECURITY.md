# Security Policy

NalApps WordPress Plugin Standard와 이를 적용한 플러그인은 보안 이슈를 공개 issue에 secret/credential과 함께 게시하지 않습니다.

## Reporting

보안 취약점 제보에는 재현 절차, 영향 범위, 관련 버전만 포함하고 실제 사용자 데이터·API key·license key·password·token은 제거합니다. 공개 지원 URL이 제품별로 존재하지 않으면 임의 URL을 만들지 말고 EOINGTI Lab 공식 사이트 `https://eoingti.com/`의 현재 안내를 확인합니다.

## Minimum Security Contract

- capability + nonce for mutations
- validation before sanitization where type/range matters
- context-aware escaping on output
- prepared SQL or safe WordPress APIs
- REST permission callbacks
- file upload validation
- no secret logging
- bounded retries and graceful remote failure
- dependency/release package review

Public repositories must also pass `docs/PUBLIC-REPOSITORY-SAFETY.md`.
