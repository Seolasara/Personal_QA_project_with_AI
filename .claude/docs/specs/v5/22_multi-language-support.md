출처: v5.md "Multi-Language Support"

## Multi-Language Support

### User Story
As a visitor,
I want to switch the application language,
so that I can use it in my preferred language.

### Acceptance Criteria

#### AC1 – Automatic browser language detection
Given I visit the application for the first time  
And my browser language is set to a supported language (English, German, Spanish, French, Dutch, or Turkish)  
Then the application automatically displays in my browser's language.  

---

#### AC2 – Unsupported browser language fallback
Given I visit the application for the first time  
And my browser language is not one of the supported languages  
Then the application defaults to English.  

---

#### AC3 – Language selector
Given I am on any page  
Then a language selector is available in the navigation bar with: DE, EN, ES, FR, NL, TR.  

---

#### AC4 – Language switch
Given I select a language from the selector  
Then all labels, messages, and UI elements update to the selected language.  

---

#### AC5 – Persistence across sessions
Given I have selected a language  
Then my preference is stored in the browser (localStorage)  
And on subsequent visits my stored preference takes priority over browser language detection.  
