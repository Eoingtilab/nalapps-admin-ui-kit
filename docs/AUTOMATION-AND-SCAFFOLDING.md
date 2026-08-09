# NalApps Automation & Scaffolding

NalApps WordPress Plugin Standard v4의 목적은 표준을 사람이 매번 해석해서 적용하는 것이 아니라 **제품 profile을 입력하면 프로젝트 골격과 품질게이트를 자동 생성하고 CI가 표준 위반을 차단**하는 것이다.

## Canonical entrypoint

```bash
python tools/scaffold_complete.py --profile path/to/plugin-profile.json --output build/scaffold --clean
```

생성기는 `profiles/company-profile.json`, `profiles/plugin-profile.schema.json`, `VERSION`을 canonical source로 사용한다.

## 자동 생성 범위

기본 생성:
- main plugin bootstrap
- unique namespace/prefix 기반 core class
- plugin-profile.json
- nalapps-standard-manifest.json
- README.md / readme.txt / CHANGELOG.md
- SECURITY.md / CONTRIBUTING.md
- .gitignore
- composer.json
- phpcs.xml.dist
- GitHub quality workflow
- immutable release workflow
- release acceptance checklist

Profile별 조건부 생성:
- `external_api=true`: bounded HTTPS HTTP client skeleton
- `database=true`: schema-version migration skeleton
- `cron=true`: duplicate-safe Cron manager skeleton
- `rest_api=true`: permission_callback이 있는 read-only REST skeleton
- `file_upload=true`: capability + MIME/extension validation skeleton
- `product_type=edd_paid`: EDD store/download configuration skeleton 및 EDD release gate 선택

## 자동 검증

`tools/self_test.py`는 최소 3개의 synthetic product profile을 매번 생성한다.

1. free/basic
2. EDD paid + external API
3. full-capability private plugin

각 fixture에서 필수 파일, 조건부 모듈, manifest module selection, standard version, unresolved placeholder 여부를 검증한다.

## CI enforcement

`.github/workflows/quality-gate.yml`은 다음을 자동 실행한다.

- canonical standard audit
- JSON Schema profile validation
- scaffold self-test matrix
- public repository safety gate
- Composer dependency audit
- PHP syntax
- WordPress Coding Standards / PHPCS
- PHP 7.4 / 8.1 / 8.3 / 8.4 / 8.5 syntax matrix
- release provenance generator smoke test

기계적으로 검증 가능한 항목은 사람이 체크박스를 눌렀다는 이유만으로 PASS 처리하지 않는다.

## Release tagging

`VERSION`은 **모든 기능/문서/테스트 변경이 끝난 마지막 커밋에서만** 변경한다.

표준 저장소의 `tag-version.yml`은 새 VERSION을 발견해도 즉시 태그하지 않는다. profile/self-test/security/WPCS/dependency gate를 먼저 통과한 뒤에만 immutable `v{VERSION}` 태그를 생성한다.

이미 존재하는 버전 태그는 재생성하거나 다른 commit으로 이동시키지 않는다.

## Product release contract

완성형 scaffold가 생성하는 release workflow는 다음 원칙을 사용한다.

- 기존 tag가 있으면 release rebuild/overwrite 금지
- PHP syntax와 WPCS 통과 후 build
- canonical slug를 ZIP root folder로 사용
- SHA-256 checksum 생성
- validation 이후에만 tag 생성
- tag 생성 이후 GitHub Release 생성

제품이 Composer production dependency를 사용하는 경우 제품 release workflow는 반드시 production dependency를 distribution ZIP에 포함하도록 제품별 build step을 확장해야 한다. EDD SDK처럼 runtime dependency가 필요한 제품은 Source ZIP을 배포 파일로 사용하지 않는다.

## Human-only gates

다음은 자동화만으로 완전 판정하지 않는다.

- 실제 WordPress 관리자 UX/E2E
- 기능의 사업 요구사항 적합성
- 실제 EDD 라이선스 activation/deactivation
- 구버전에서 최신버전으로의 실제 upgrade regression
- 외부 서비스 약관/개인정보 고지 적합성
- 접근성의 최종 사용자 경험 검수

이 항목은 `docs/ACCEPTANCE-CHECKLIST.md`에서 사람이 최종 승인한다.
