출처: v5.md "Checkout – Payment (Advanced)"

## Checkout – Payment (Advanced)

### User Story
As a customer,
I want to provide payment details specific to my chosen payment method,
so that my payment is processed correctly.

### Acceptance Criteria

#### AC1 – Payment method selection
Given I am on the payment step  
Then a dropdown is displayed with options:  
- Bank Transfer
- Cash on Delivery
- Credit Card
- Buy Now Pay Later
- Gift Card

---

#### AC2 – Bank Transfer fields
Given I select "Bank Transfer"  
Then these fields are displayed:  
- Bank name (required, letters and spaces only)
- Account name (required, alphanumeric with spaces, periods, apostrophes, hyphens)
- Account number (required, digits only)

---

#### AC3 – Credit Card fields
Given I select "Credit Card"  
Then these fields are displayed:  
- Card number (format: XXXX-XXXX-XXXX-XXXX)
- Expiration date (format: MM/YYYY, must be a future date)
- CVV (3 or 4 digits)
- Card holder name (letters and spaces only)

---

#### AC4 – Credit Card expiration validation
Given I enter an expiration date in the past  
Then the error "Expiration date must be in the future." is displayed.  

---

#### AC5 – Buy Now Pay Later
Given I select "Buy Now Pay Later"  
Then a "Monthly installments" dropdown is displayed with options: 3, 6, 9, 12.  

---

#### AC6 – Gift Card fields
Given I select "Gift Card"  
Then these fields are displayed:  
- Gift card number (required, alphanumeric)
- Validation code (required, alphanumeric)

---

#### AC7 – Cash on Delivery
Given I select "Cash on Delivery"  
Then no additional fields are required.  

---

#### AC8 – Payment method change resets form
Given I switch to a different payment method  
Then the form resets and shows the new method's fields.  

---

#### AC9 – Successful order
Given valid payment details are provided  
When I click confirm  
Then the payment is validated, the order is placed, a confirmation with the invoice number is shown, and the cart is cleared  
And a checkout confirmation email is sent to the customer.  
