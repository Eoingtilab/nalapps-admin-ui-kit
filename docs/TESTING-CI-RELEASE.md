# Testing, CI & Release Standard

## Test Layers

제품 특성에 따라 다음 계층을 적용합니다.

- Unit: pure logic, validators, formatters, state transitions
- Integration: WordPress options, DB migration, hooks, REST/AJAX, cron
- Admin E2E: 주요 관리자 흐름, 권한, nonce, 저장/삭제, update UI
- Front regression: 실제 기능 출력과 theme/plugin 충돌
- Upgrade regression: 최소 1개 이전 안정 버전에서 최신 버전으로 실제 업데이트

## Mandatory Security Tests

- unauthorized capability rejected
- invalid/missing nonce rejected
- malformed REST/AJAX input rejected
- upload validation rejected for forbidden type/size
- secrets are redacted in logger/System Status/support bundles
- duplicate submission/cron overlap is idempotent when applicable

## Matrix

제품에서 지원한다고 선언한 최소/대표/최신 WordPress 및 PHP 조합을 정의합니다. 지원하지 않는 조합은 명시적으로 fail-fast 또는 관리자 안내를 제공합니다.

## CI Minimum

- PHP syntax
- Composer validation/install when applicable
- PHPUnit when configured
- PHPCS/WPCS when configured
- public repository safety scan
- forbidden artifact scan (`.env`, private keys, DB dumps)
- package root and required runtime dependencies
- version metadata consistency

참고 template: `templates/github/workflows/plugin-ci.yml`

## Release Order

1. 기능/문서/테스트 완료
2. full acceptance gate
3. changelog/readme/update notice 확정
4. package build dry-run 및 secret scan
5. **버전 bump 마지막 커밋**
6. immutable tag 생성
7. CI-built Release Asset 생성
8. EDD/배포 채널 metadata 반영
9. clean install + upgrade smoke test

중간 작업 중 version을 먼저 올려 자동 tag가 불완전한 release를 가리키게 하지 않습니다.

## Package Gate

- ZIP root folder = canonical plugin slug
- runtime dependencies included
- dev/test/build-only files excluded where appropriate
- no `.git`, local `.env`, caches, logs, dumps or credentials
- main plugin header/readme stable tag/release version match

## Release Verdict

`docs/ACCEPTANCE-CHECKLIST.md`의 해당 항목이 전부 PASS일 때만 release-ready로 보고합니다. 테스트를 실제 실행하지 않았다면 PASS라고 단정하지 않습니다.
