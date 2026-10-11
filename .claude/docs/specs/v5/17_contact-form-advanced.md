출처: v5.md "Contact Form (Advanced)"

## Contact Form (Advanced)

### User Story
As a visitor or logged-in user,
I want to send a message through a contact form with optional file attachment,
so that I can provide additional context with my inquiry.

### Acceptance Criteria

#### AC1 – Auto-fill for logged-in users
Given I am logged in  
Then my first name, last name, and email are auto-filled  
And the message "Known user, [Full Name]" is displayed  
And the name and email fields are hidden.  

---

#### AC2 – Guest user fields
Given I am not logged in  
Then first name, last name, and email fields are displayed and required.  

---

#### AC3 – Subject and message
Given the form is displayed  
Then a subject dropdown is shown with options:  
- Customer service
- Webmaster
- Return
- Payments
- Warranty
- Status of order
And a message field is shown (required, minimum 50 characters).  

---

#### AC4 – File attachment
Given the form is displayed  
Then an optional file attachment field is available  
And only `.txt` files are accepted  
And the file must be exactly 0 KB in size.  

---

#### AC5 – Invalid file type
Given I select a non-`.txt` file  
Then the error "File should have a txt extension." is displayed.  

---

#### AC6 – Invalid file size
Given I select a file that is not 0 KB  
Then the error "File should be empty." is displayed.  

---

#### AC7 – Successful submission
Given all fields are valid  
When I submit the form  
Then a confirmation email is sent to the provided email address  
And a confirmation message is displayed.  
