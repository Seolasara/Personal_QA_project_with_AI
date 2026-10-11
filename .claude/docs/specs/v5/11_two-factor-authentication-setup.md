출처: v5.md "Two-Factor Authentication Setup"

## Two-Factor Authentication Setup

### User Story
As an authenticated user,
I want to set up TOTP two-factor authentication,
so that my account is protected with an additional security layer.

### Acceptance Criteria

#### AC1 – TOTP setup section
Given I am on my profile page  
Then a "Setup two factor authentication" section is displayed.  

---

#### AC2 – QR code displayed
Given the TOTP setup section is shown  
Then a QR code is displayed that I can scan with my authenticator app.  

---

#### AC3 – Manual secret entry
Given the TOTP setup section is shown  
Then the secret key is also displayed as text for manual entry.  

---

#### AC4 – Verification
Given I enter a valid 6-digit code from my authenticator app  
When I click "Verify TOTP"  
Then the message "TOTP verified and enabled successfully." is displayed.  

---

#### AC5 – Invalid code
Given I enter an incorrect code  
Then an error message is displayed.  

---

#### AC6 – Restricted for test accounts
Given I am logged in as customer@practicesoftwaretesting.com or admin@practicesoftwaretesting.com  
Then TOTP setup is denied with "Access denied: If you want to configure TOTP, please create your own account."  
