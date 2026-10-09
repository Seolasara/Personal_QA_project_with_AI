# Sprint 5 User Stories 인덱스

- 기능 요구사항(User Story, AC)이 필요하면 이 목록에서 해당 기능 파일만 골라 읽는다. 여러 파일을 한꺼번에 읽지 않는다.
- 원본: testsmith-io/practice-software-testing 저장소 `docs/user-stories/v5.md`를 `## ` 기능 단위로 나눈 것이다(내용 수정 없음).
- Sprint 5 개요: 서버 저장 장바구니, 고급 결제, 비밀번호 강도, 계정 잠금, 2단계 인증, 소셜 로그인, PDF 인보이스, 관리자, 채팅, 할인, 다국어, 가격 슬라이더, 개인정보 페이지.
- 형식: 파일 (줄 수, AC 수) — AC 제목. `spec analysis` 칸은 같은 기능을 이미 분석한 `spec analysis/ui/` 파일.

## 1. 상품과 탐색
- [Product Overview](01_product-overview.md) (90줄, AC 13) — Product grid is displayed, Navigating to product detail, Pagination, Search, Category filter, Hierarchical category selection, Brand filter, Combining filters, Sorting, Price range slider, Adjusting the price range, Discount price display, Out of stock indicator / spec analysis: `ui/ui-product-browse.md`
- [Product Detail](02_product-detail.md) (104줄, AC 14) — Product information shown, Discount price display, Quantity selector, Increase quantity, Decrease quantity, Minimum quantity, Manual quantity entry, Add to cart, Out of stock, Rental duration slider, Add to Favorites, Duplicate favorite, Not logged in, Related products / spec analysis: `ui/ui-product-detail.md`
- [Rental Products](03_rental-products.md) (38줄, AC 5) — Rentals page is accessible, Rental product display, Rental detail page, Rental label in checkout, Location-based discount on rentals
- [Browse Products by Category](24_browse-products-by-category.md) (24줄, AC 2) — Category page is displayed, Filters available / spec analysis: `ui/ui-product-browse.md`

## 2. 체크아웃
- [Checkout – Cart Review](04_checkout-cart-review.md) (61줄, AC 8) — Cart contents displayed, Update quantity, Delete item, Empty cart, Proceed, Discount badge on items, Combined product discount, Combined discount removed / spec analysis: `ui/ui-cart.md`
- [Checkout – Sign In](05_checkout-sign-in.md) (45줄, AC 5) — Login step displayed for guests, Login form fields, TOTP support during checkout login, Successful login during checkout, Already logged in
- [Checkout – Billing Address](06_checkout-billing-address.md) (37줄, AC 4) — Address form fields, Validation, Proceed to payment, Pre-fill for logged-in users
- [Checkout – Payment (Advanced)](07_checkout-payment-advanced.md) (76줄, AC 9) — Payment method selection, Bank Transfer fields, Credit Card fields, Credit Card expiration validation, Buy Now Pay Later, Gift Card fields, Cash on Delivery, Payment method change resets form, Successful order / spec analysis: `ui/ui-payment.md`

## 3. 계정과 인증
- [User Registration](08_user-registration.md) (65줄, AC 6) — Registration form fields, Password requirements displayed, Real-time password validation, Password strength indicator, Duplicate email, Successful registration
- [User Login](09_user-login.md) (78줄, AC 10) — Login form, Successful login, Invalid credentials, Account locking, Admin accounts are exempt from locking, Disabled account, TOTP prompt, Valid TOTP code, Invalid TOTP code, Google social login / spec analysis: `ui/ui-login-logout.md`
- [Forgot Password](10_forgot-password.md) (35줄, AC 4) — Forgot password form, Email validation, Successful reset, Non-existent email
- [Two-Factor Authentication Setup](11_two-factor-authentication-setup.md) (43줄, AC 6) — TOTP setup section, QR code displayed, Manual secret entry, Verification, Invalid code, Restricted for test accounts
- [Customer Profile](12_customer-profile.md) (40줄, AC 4) — Profile page is accessible, Editable fields, Read-only email, Successful update
- [Change Password](13_change-password.md) (50줄, AC 6) — Change password form, Password strength indicator, Passwords must match, Current password verification, New password must differ, Successful change

## 4. 마이페이지
- [Favorites](14_favorites.md) (26줄, AC 3) — Favorites page, Empty favorites, Remove a favorite
- [Invoices](15_invoices.md) (61줄, AC 8) — Invoice list, Invoice detail, Non-existent invoice, Discount on invoice, Discounted line items, PDF download button, PDF generation status, Successful PDF download
- [Messages](16_messages.md) (27줄, AC 3) — Messages list, Message detail, Reply to message
- [Contact Form (Advanced)](17_contact-form-advanced.md) (61줄, AC 7) — Auto-fill for logged-in users, Guest user fields, Subject and message, File attachment, Invalid file type, Invalid file size, Successful submission

## 5. 관리자와 부가 기능
- [Admin Dashboard](18_admin-dashboard.md) (64줄, AC 9) — Dashboard, Product management, Category management, Brand management, Order management, User management, Disable and enable user accounts, Message management, Reports
- [Chat Widget](19_chat-widget.md) (51줄, AC 6) — Chat toggle, Find Product, Order Product, Checkout, Empty cart, Support

## 6. 할인과 기타
- [Geo-Location Discount](20_geo-location-discount.md) (37줄, AC 4) — Discount applied based on location, Discount display, No match, Discount in cart
- [Combination Discount](21_combination-discount.md) (31줄, AC 4) — Combination discount applied, Discount display in cart, Discount removed when condition no longer met, Discount on invoice
- [Multi-Language Support](22_multi-language-support.md) (39줄, AC 5) — Automatic browser language detection, Unsupported browser language fallback, Language selector, Language switch, Persistence across sessions
- [Privacy Policy](23_privacy-policy.md) (12줄, AC 1) — Privacy page accessible
