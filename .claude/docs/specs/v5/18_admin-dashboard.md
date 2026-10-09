출처: v5.md "Admin Dashboard"

## Admin Dashboard

### User Story
As an administrator,
I want to access a dashboard and manage all entities,
so that I can oversee and administer the application.

### Acceptance Criteria

#### AC1 – Dashboard
Given I am logged in as an admin  
When I navigate to `/admin/dashboard`  
Then a bar chart of total sales by year and a paginated list of recent invoices are displayed.  

---

#### AC2 – Product management
Given I navigate to the products management page  
Then I can list, create, edit, and delete products.  

---

#### AC3 – Category management
Given I navigate to the categories management page  
Then I can list, create, edit, and delete categories (with optional parent category).  

---

#### AC4 – Brand management
Given I navigate to the brands management page  
Then I can list, create, edit, and delete brands.  

---

#### AC5 – Order management
Given I navigate to the orders management page
Then I can list all orders, view details, and update order status  
And the available status values are: AWAITING_FULFILLMENT, ON_HOLD, AWAITING_SHIPMENT, SHIPPED, COMPLETED.  

---

#### AC6 – User management
Given I navigate to the users management page  
Then I can list, view, edit, and delete user accounts.  

---

#### AC7 – Disable and enable user accounts
Given I am editing a user account in the admin panel  
Then an "Enabled" toggle is available  
And disabling the account immediately prevents the user from logging in  
And re-enabling the account restores the user's access.  

---

#### AC8 – Message management
Given I navigate to the messages management page  
Then I can view all contact messages, view details, and reply.  

---

#### AC9 – Reports
Given I navigate to the reports section  
Then I can view monthly sales, weekly sales, and general statistics.  
