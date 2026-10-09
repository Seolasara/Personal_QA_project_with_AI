출처: v5.md "Combination Discount"

## Combination Discount

### User Story
As a customer with both rental and non-rental items in my cart,
I want to receive an additional discount on my order,
so that I am rewarded for combining product types.

### Acceptance Criteria

#### AC1 – Combination discount applied
Given my cart contains at least one rental item and at least one non-rental item  
Then an additional 15% discount is applied to the cart subtotal.  

---

#### AC2 – Discount display in cart
Given the combination discount is applied  
Then the cart shows the subtotal, discount percentage (15%), discount amount, and final total.  

---

#### AC3 – Discount removed when condition no longer met
Given I remove all rental items or all non-rental items from my cart  
Then the 15% combination discount is removed  
And the total reverts to the regular subtotal.  

---

#### AC4 – Discount on invoice
Given I complete checkout with the combination discount applied  
Then the invoice shows the subtotal, the 15% discount amount, and the final total.  
