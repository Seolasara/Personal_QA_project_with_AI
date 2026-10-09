출처: v5.md "Geo-Location Discount"

## Geo-Location Discount

### User Story
As a visitor browsing from a supported city,
I want to automatically receive a location-based discount on eligible products,
so that I benefit from regional promotions.

![Decision Table – Discount Rules](../images/decision-table.png)

### Acceptance Criteria

#### AC1 – Discount applied based on location
Given my browser geo-location matches a supported city and a product is a location offer  
Then the following discount is applied:  
- New York: 5%
- Mumbai: 10%
- Tokyo: 15%
- Amsterdam: 20%
- London: 25%

---

#### AC2 – Discount display
Given a location discount is applied  
Then the original price is shown with a strikethrough and the discounted price is shown below.  

---

#### AC3 – No match
Given my location does not match any supported city  
Then no location discount is applied.  

---

#### AC4 – Discount in cart
Given I add a location-discounted product to the cart  
Then the discounted price is used for the cart line item.  
