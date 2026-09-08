# Traceability Matrix

> `scripts/gen_traceability.py` 로 자동 생성. 직접 편집하지 말 것.

| TC | 제목 | 우선순위 | 컴포넌트 | 연결 테스트 | 마커 | 비고 |
|---|---|---|---|---|---|---|
| QA-01 | 메인 페이지 정상 접속 확인 | P1 | main | `playwright-demo/tests/login_test.py::test_landing_page` | playwright-demo/tests/login_test.py::test_landing_page |  |
| QA-02 | 도메인 없는 비정상 이메일 입력 시 로그인 실패 확인 | P1 | login | `playwright-demo/tests/login_test.py::test_invalid_email_format` | playwright-demo/tests/login_test.py::test_invalid_email_format |  |
| QA-03 | 도메인 포함 비정상 이메일 입력 시 로그인 실패 확인 | P1 | login | `playwright-demo/tests/login_test.py::test_invalid_email` | playwright-demo/tests/login_test.py::test_invalid_email |  |
| QA-04 | 비정상 비밀번호 입력 시 로그인 실패 확인 | P1 | login | `playwright-demo/tests/login_test.py::test_invalid_password` | playwright-demo/tests/login_test.py::test_invalid_password |  |
| QA-05 | 정상 계정 입력 시 로그인 동작 확인 | P1 | login | `playwright-demo/tests/login_test.py::test_login` | playwright-demo/tests/login_test.py::test_login |  |
| QA-06 | 메인 페이지 이동 시 로그인 상태 유지 확인 | P1 | main | `playwright-demo/tests/login_test.py::test_loggedin_home` | playwright-demo/tests/login_test.py::test_loggedin_home |  |
| QA-07 | 필터 영역 체크박스 정상 동작 확인 | P2 | product | `playwright-demo/tests/product_search_test.py::test_product_checkbox` | playwright-demo/tests/product_search_test.py::test_product_checkbox |  |
| QA-08 | 상품 클릭 시 상품 상세 페이지 정상 이동 확인 | P1 | product | `playwright-demo/tests/product_search_test.py::test_product_get` | playwright-demo/tests/product_search_test.py::test_product_get |  |
| QA-09 | 상품 상세 페이지 내 장바구니 버튼 정상 동작 확인 | P1 | cart | `playwright-demo/tests/add_to_cart_test.py::test_cart_button` | playwright-demo/tests/add_to_cart_test.py::test_cart_button |  |
| QA-10 | 장바구니 추가 상품 리스트 정상 노출 확인 | P1 | cart | `playwright-demo/tests/add_to_cart_test.py::test_cart_check` | playwright-demo/tests/add_to_cart_test.py::test_cart_check |  |
| QA-11 | 결제 방법 드롭다운 Cash on Delivery 정상 적용 확인 | P1 | payment | `playwright-demo/tests/payment_test.py::test_checkout_button` | playwright-demo/tests/payment_test.py::test_checkout_button |  |
| QA-12 | Confirm 버튼 클릭 시 결제 완료 확인 | P2 | payment | `playwright-demo/tests/payment_test.py::test_payment_checkout` | playwright-demo/tests/payment_test.py::test_payment_checkout |  |
| QA-13 | Sign out 버튼 클릭 시 정상 로그아웃 확인 | P2 | logout | `playwright-demo/tests/logout_test.py::test_logout` | playwright-demo/tests/logout_test.py::test_logout |  |

## 고아 마커 (TC 파일 없음)

없음

## 커버리지 요약

- 전체 TC: 13
- automated: 13
- 마커 연결됨: 13
