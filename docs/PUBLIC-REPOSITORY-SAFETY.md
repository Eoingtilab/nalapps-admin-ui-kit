# Public Repository Safety Gate

이 저장소와 이를 따르는 공개 플러그인 저장소는 공개 가능한 코드/문서/템플릿만 포함한다.

## 절대 커밋 금지

- EDD license key, API key/secret, OAuth token, GitHub PAT, webhook secret
- WordPress application password, 관리자/SSH/DB 자격증명
- `.env` 실제 값, production config dump, 인증 cookie/session
- 고객 DB/백업/주문/이메일/전화번호 등 개인정보
- 고객 전용 비공개 계약자료나 소스
- secret이 포함된 로그/스크린샷/fixture

## 허용 예제

실제 값 대신 `YOUR_API_KEY_HERE`, `example.com`, `123` 같은 명시적 placeholder만 사용한다.

## CI Gate

공개 release 전에 다음을 검사한다.

1. secret pattern scan
2. `.env`, key/certificate, backup/database dump 금지 파일 검사
3. 개인/고객 도메인·메일·전화번호 fixture 검토
4. release ZIP 재검사
5. 실패 시 tag/release 금지

Telemetry는 기본 OFF이고 필요할 경우 명시적 opt-in만 허용한다. 진단정보는 secret과 개인정보를 마스킹한 뒤에만 복사/전송할 수 있다.
