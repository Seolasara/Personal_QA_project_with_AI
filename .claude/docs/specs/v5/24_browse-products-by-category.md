출처: v5.md "Browse Products by Category"

## Browse Products by Category

### User Story
As a visitor,
I want to browse products within a specific category with filtering, sorting, pagination, and price range,
so that I can find specific products within a category.

### Acceptance Criteria

#### AC1 – Category page is displayed
Given I click on a category name  
Then a page with products belonging to that category is displayed  
And the category name is shown as the page title.  

---

#### AC2 – Filters available
Given the category page is displayed  
Then the same filters as the product overview are available:  
- category checkboxes (subcategory tree)
- brand checkboxes
- sorting dropdown
- pagination controls
- price range slider
