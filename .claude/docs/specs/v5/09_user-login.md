출처: v5.md "User Login"

## User Login

### User Story
As a registered user,
I want to log in with my credentials or via social login, with support for two-factor authentication,
so that I can securely access my account.

![Login](../images/login.png)

### Acceptance Criteria

#### AC1 – Login form
Given I navigate to the login page  
Then email and password fields are displayed  
And a "Sign in with Google" button is shown.  

---

#### AC2 – Successful login
Given I enter valid credentials  
When I submit the form  
Then I am redirected based on my role: `/account` for users, `/admin/dashboard` for admins.  

---

#### AC3 – Invalid credentials
Given I enter incorrect credentials  
Then the error "Invalid email or password" is displayed.  

---

#### AC4 – Account locking
Given I have entered incorrect credentials 3 times consecutively  
When I try to log in again  
Then the error "Account locked, too many failed attempts. Please contact the administrator." is displayed  
And the API returns HTTP 423.  

![State Transition Diagram – Account Locking](../images/state-transistion-diagram.png)

---

#### AC5 – Admin accounts are exempt from locking
Given I am logging in as an admin  
Then the account is never locked regardless of failed attempts.  

---

#### AC6 – Disabled account
Given my account has been disabled by an administrator  
When I try to log in with valid credentials  
Then the error "Account disabled." is displayed  
And I am not authenticated.  

---

#### AC7 – TOTP prompt
Given I have TOTP enabled on my account  
When I submit valid email and password  
Then a 6-digit TOTP input field is displayed.  

---

#### AC8 – Valid TOTP code
Given I enter a valid TOTP code  
Then I am fully authenticated and redirected.  

---

#### AC9 – Invalid TOTP code
Given I enter an incorrect TOTP code  
Then the error "Invalid TOTP" is displayed.  

---

#### AC10 – Google social login
Given I click "Sign in with Google"  
Then a popup (500x400px) opens for Google authentication  
And on success, I am logged in and redirected to my account.  
