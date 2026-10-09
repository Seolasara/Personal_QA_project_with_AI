출처: v5.md "Invoices"

## Invoices

### User Story
As an authenticated user,
I want to view my invoices with discount details and download them as PDF,
so that I can keep records of my purchases.

### Acceptance Criteria

#### AC1 – Invoice list
Given I am logged in  
When I navigate to my invoices page  
Then a paginated table is displayed with columns: invoice number, billing street, invoice date, total, and a details link.  

---

#### AC2 – Invoice detail
Given I click on an invoice  
Then the detail page shows:  
- invoice number, date, and total
- billing address (street, postal code, city, state, country)
- payment method and details
- product line items (quantity, name, price, line total)

---

#### AC3 – Non-existent invoice
Given the invoice does not exist or does not belong to me  
Then a "not found" message is displayed.  

---

#### AC4 – Discount on invoice
Given the invoice has a discount  
Then the detail page shows the subtotal, discount percentage and amount, and final total.  

---

#### AC5 – Discounted line items
Given a line item has a discount  
Then the original price is shown with a strikethrough and the discounted price below.  

---

#### AC6 – PDF download button
Given I am on the invoice detail page  
Then a "Download PDF" button is displayed.  

---

#### AC7 – PDF generation status
Given the PDF is still being generated  
Then the download button is disabled  
And the system checks the status every 20 seconds.  

---

#### AC8 – Successful PDF download
Given the PDF generation is complete  
When I click "Download PDF"  
Then the PDF file is downloaded.  
