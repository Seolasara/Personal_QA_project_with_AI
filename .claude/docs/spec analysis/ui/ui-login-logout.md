# UI 분석: 로그인/로그아웃

> 개요, 판단 기준, 우선순위별 리스크 목록: [00_ui-overview.md](00_ui-overview.md)

## 1. 기능 목적
| 기능 | 목적 |
|---|---|
| 로그인/로그아웃 | 이메일과 비밀번호로 인증한 뒤 역할별로 이동(`/account`)하고, 로그아웃하면 세션을 종료합니다. |

## 2. 핵심 흐름
1. 로그인: Sign In 링크 → 이메일/비밀번호 입력 → Login → `/account`("My account", 헤더에 사용자 이름 버튼)
   - 실패 케이스
     - 이메일 형식 오류: `email-error`
     - 자격 불일치: `login-error` ("Invalid email or password")
     - 3회 연속 실패: 계정 잠김 (HTTP 423)
2. 로그아웃: 헤더 사용자 메뉴(`nav-menu`) → Sign out(`nav-sign-out`) → 홈 이동, 사용자 메뉴 사라짐

## 3. 리스크
- **R2** 공유 데모 계정과 데이터
  - 공개 공용 계정이라 3회 연속 실패 시 잠김(423)이 다른 테스트에 영향을 줍니다.
  - 계정 잠김 검증은 전용 계정이 필요합니다.
  - 상세는 [00_ui-overview.md](00_ui-overview.md)에 있습니다.

## 4. 테스트 범위 (포함)
- 로그인: 정상, 이메일 형식 오류, 없는 계정, 비밀번호 오류, 빈 입력(required 메시지)
- 로그아웃: 사용자 메뉴, Sign out, 홈 이동, 메뉴 소멸

## 5. TC 작성 입력값 (후보)
**A. 로그인**
- 후보 A-1: 빈 이메일과 빈 비밀번호 제출
  - 화면: `/auth/login`
  - 입력: 이메일 공란, 비밀번호 공란 (각각, 동시)
  - 기대: `email-error`, `password-error` 노출 (required 메시지), 요청 미전송
- 후보 A-2: 비밀번호 길이 경계 (minlength/maxlength 에러)
  - 기대: `password-error` 길이 메시지
- 후보 A-3: 계정 잠김 (3회 연속 실패 → 423)
  - 기대: "Account locked, too many failed attempts. Please contact the administrator."
  - 주의: 공용 계정은 쓰지 않습니다. 전용 신규 계정이 필요하며, 회원가입은 범위 밖이라 사용자 판단이 필요합니다.
- 후보 A-4: 로그인 상태에서 Sign In 링크 비노출 확인

**B. 로그아웃**
- 후보 B-1: 로그아웃 후 `/account` 직접 접근 시 로그인 페이지로 리다이렉트
- 후보 B-2: 로그아웃 후 장바구니와 세션 상태 확인
