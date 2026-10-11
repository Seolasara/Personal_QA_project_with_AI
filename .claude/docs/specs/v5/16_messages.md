출처: v5.md "Messages"

## Messages

### User Story
As an authenticated user,
I want to view my contact messages and reply to them,
so that I can follow up on my inquiries.

### Acceptance Criteria

#### AC1 – Messages list
Given I am logged in  
When I navigate to my messages page  
Then a paginated table is displayed with columns: subject, message (truncated to 50 chars), status badge (NEW / IN_PROGRESS / RESOLVED), date, and a details link.  

---

#### AC2 – Message detail
Given I click on a message  
Then the original message is displayed (sender, subject, status, full text, timestamp)  
And any replies are listed chronologically below.  

---

#### AC3 – Reply to message
Given I am on the message detail page  
When I enter a reply and submit  
Then the reply is added and the replies list is updated.  
