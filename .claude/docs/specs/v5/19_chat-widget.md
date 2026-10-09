출처: v5.md "Chat Widget"

## Chat Widget

### User Story
As a visitor or logged-in user,
I want to use a chat widget to search products, place orders, go through checkout, or submit support tickets,
so that I can interact with the application without navigating away from the current page.

### Acceptance Criteria

#### AC1 – Chat toggle
Given I am on any page  
Then a chat toggle button is displayed in the bottom-right corner  
And clicking it opens the chat window with a menu: Find Product, Order Product, Checkout, Support.  

---

#### AC2 – Find Product
Given I select "Find Product"  
Then I can enter a search query and up to 5 matching products are shown as cards  
And I can click "View Product" to navigate to the detail page.  

---

#### AC3 – Order Product
Given I select "Order Product"  
Then I can search for a product, select a quantity (1, 2, 3, 5, 10, or custom 1–999), confirm the order, and the product is added to my cart.  

---

#### AC4 – Checkout
Given I select "Checkout" and my cart has items  
Then the chat walks me through the full checkout flow:  
- cart summary
- guest details (if not logged in): email, first name, last name
- address: street, city, state, country, postal code
- payment method selection and details
- order confirmation with invoice number

---

#### AC5 – Empty cart
Given I select "Checkout" and my cart is empty  
Then the message "Your cart is empty" is displayed.  

---

#### AC6 – Support
Given I select "Support"  
Then the chat prompts me for subject, message (min 50 chars), and optional file attachment (.txt)  
And if not logged in, also asks for first name, last name, and email  
And on submission, a confirmation is displayed.  
