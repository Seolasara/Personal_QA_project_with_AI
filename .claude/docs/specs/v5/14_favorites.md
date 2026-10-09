출처: v5.md "Favorites"

## Favorites

### User Story
As an authenticated user,
I want to view and manage my list of favorite products,
so that I can quickly access products I'm interested in.

### Acceptance Criteria

#### AC1 – Favorites page
Given I am logged in  
When I navigate to my favorites page  
Then a list of my favorite products is displayed showing image, name, and description (truncated to 250 characters).  

---

#### AC2 – Empty favorites
Given I have no favorites  
Then a message indicating no favorites is displayed.  

---

#### AC3 – Remove a favorite
Given the favorites list is displayed  
When I click the delete button on a favorite  
Then the product is removed and the list refreshes.  
