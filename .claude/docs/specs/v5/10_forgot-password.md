출처: v5.md "Forgot Password"

## Forgot Password

### User Story
As a registered user who has forgotten their password,
I want to request a password reset by providing my email,
so that I can regain access to my account.

![Forgot Password](../images/forgot-password.png)

### Acceptance Criteria

#### AC1 – Forgot password form
Given I click "Forgot password" on the login page  
Then a form with an email input is displayed.  

---

#### AC2 – Email validation
Given I enter an email address  
Then it must match a valid RFC-compliant format.  

---

#### AC3 – Successful reset
Given I enter a registered email  
When I submit the form  
Then a new password is generated and sent to my email address  
And a confirmation message is displayed and fades out after 3 seconds.  

---

#### AC4 – Non-existent email
Given I enter an unregistered email  
When I submit the form  
Then an error message is displayed.  
