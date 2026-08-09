# NalApps / EOINGTI Lab Company Profile

NalApps WordPress 플러그인의 공통 개발사 메타데이터 기본값입니다.

## Canonical Defaults

- 회사/개발사 한글명: `어잉티연구소`
- 개발사 영문명: `EOINGTI Lab`
- 브랜드: `NalApps`
- 개발사 홈페이지: `https://eoingti.com/`
- GitHub 조직: `https://github.com/Eoingtilab`
- 기본 GitHub owner: `Eoingtilab`

## 적용 원칙

1. WordPress 플러그인 헤더의 `Author` 기본값은 `EOINGTI Lab`로 사용한다.
2. `Author URI` 기본값은 `https://eoingti.com/`로 사용한다.
3. GitHub 저장소는 기본적으로 `https://github.com/Eoingtilab/<plugin-slug>` 구조를 사용한다.
4. `Plugin URI`는 제품별 공식 소개/문서 페이지가 있으면 해당 URL을 사용한다.
5. 제품별 공식 페이지가 아직 없으면 `Plugin URI`는 `https://eoingti.com/`를 사용한다.
6. README/CHANGELOG/지원 문서에는 개발사 홈페이지와 GitHub 저장소를 명확히 기록한다.
7. 실제 제품별 Store URL, EDD Download ID, 지원 URL이 별도로 존재하면 회사 기본값보다 제품별 값을 우선한다.
8. 존재하지 않는 제품 페이지나 지원 URL을 임의로 만들어 넣지 않는다.

## 금지

- 개인 GitHub 계정을 기본 소스 저장소로 사용하지 않는다.
- `Author URI`를 GitHub 저장소 URL로 대체하지 않는다.
- 제품 페이지가 없는 상태에서 존재하지 않는 `eoingti.com/products/...` URL을 추측해 생성하지 않는다.
- 플러그인마다 Author 표기를 제각각 바꾸지 않는다.
