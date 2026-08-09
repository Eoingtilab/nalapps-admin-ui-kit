# NalApps Plugin Metadata & Documentation Standard

모든 NalApps WordPress 플러그인의 헤더, README, 저장소, 개발사 표기를 통일하기 위한 계약입니다.

## 1. 회사 기본값

`docs/COMPANY-PROFILE.md`를 canonical source로 사용합니다.

- Author: `EOINGTI Lab`
- Author URI: `https://eoingti.com/`
- GitHub owner: `Eoingtilab`
- Repository: `https://github.com/Eoingtilab/<plugin-slug>`

## 2. WordPress Plugin Header

최소 권장 필드:

- Plugin Name
- Plugin URI
- Description
- Version
- Author
- Author URI
- Text Domain
- Requires at least
- Requires PHP
- Update URI (자체 업데이트 제품에서 필요한 경우)
- License
- License URI

템플릿: `wordpress/standard/plugin-header.template.php`

## 3. Plugin URI 정책

1. 실제 제품 소개/문서 페이지가 존재하면 그 URL을 사용한다.
2. 제품 페이지가 아직 없으면 `https://eoingti.com/`를 사용한다.
3. 존재하지 않는 제품 경로나 URL을 추정해서 만들지 않는다.
4. GitHub 저장소는 Plugin URI가 아니라 README의 Source/Repository 항목으로 별도 표기한다.

## 4. GitHub Repository 정책

- 기본 owner는 `Eoingtilab`이다.
- 저장소명은 canonical plugin slug와 동일하게 하는 것을 우선한다.
- README에 source repository URL을 명확히 표기한다.
- GitHub Release를 사용하는 제품은 CHANGELOG와 tag/version을 일치시킨다.
- Composer dependency가 있으면 Source ZIP 대신 production dependency가 포함된 Release Asset을 사용한다.

## 5. README 필수 항목

공개/배포 플러그인의 README에는 가능한 범위에서 다음을 포함한다.

- 제품명과 설명
- 개발사 및 홈페이지
- GitHub 소스 저장소
- 요구 WordPress/PHP 버전
- 주요 기능
- 설치 방법
- 업데이트 정책
- 라이선스 정책
- 데이터 보존/삭제 정책
- 개인정보/외부 통신 여부
- 지원/문제 해결 방법
- 변경 이력 위치
- 라이선스/저작권

템플릿: `wordpress/standard/README.template.md`

## 6. readme.txt 정책

WordPress 형식의 `readme.txt`를 사용하는 경우 최소한 다음을 버전과 동기화한다.

- Requires at least
- Tested up to
- Requires PHP
- Stable tag
- License
- Description
- Installation
- Changelog

`Stable tag`, 메인 플러그인 header `Version`, EDD 배포 버전, GitHub release/tag는 출시 시 서로 일치해야 한다.

## 7. Support / Privacy

- 실제 지원 URL이 없으면 존재하지 않는 support URL을 만들지 않는다.
- 비밀키/라이선스키/비밀번호를 GitHub Issue에 올리지 않도록 README에 안내한다.
- 외부 API/원격 서비스가 있으면 무엇을 왜 전송하는지 제품 문서에 설명한다.

## 8. Branding

- 사용자 노출 개발사명은 `EOINGTI Lab`을 기본으로 한다.
- 문서에서는 필요 시 `EOINGTI Lab / 어잉티연구소`를 병기할 수 있다.
- NalApps는 제품군/디자인 시스템 브랜드로 사용한다.
- 플러그인별로 회사명/Author URI/GitHub owner를 임의 변경하지 않는다.

## 9. Acceptance

출시 PASS 전에 다음을 확인한다.

- Header Author/Author URI가 회사 프로필과 일치
- Repository owner가 `Eoingtilab`
- README에 개발사/홈페이지/GitHub 정보 존재
- Plugin URI가 실제 존재하는 URL 또는 eoingti.com 루트
- 존재하지 않는 support/product URL 없음
- Version/Stable tag/release/tag/EDD version 일치
- secret 또는 개인 인증정보가 README/소스/릴리스에 없음
