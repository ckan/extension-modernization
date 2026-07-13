---
icon: lucide/terminal-square
---

# E2E with Cypress

Cypress is a popular frontend-centric E2E testing framework. It runs directly inside browser engines, offering real-time debugging tools, automatic waiting, and UI action recording.

---

## Directory Layout

Create a Cypress folder structure at the root of your extension:

```
ckanext-myextension/
├── cypress.config.js        # Cypress configuration
├── package.json
└── cypress/
    ├── fixtures/
    │   └── example.json
    ├── support/
    │   ├── commands.js      # Custom Cypress commands
    │   └── e2e.js
    └── e2e/
        └── test_spec.cy.js  # Spec test files
```

---

## Configuration (`cypress.config.js`)

Configure Cypress to point to your local CKAN development instance:

```javascript title="cypress.config.js"
const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    baseUrl: "http://localhost:5000", # URL of the running CKAN server
    supportFile: "cypress/support/e2e.js",
    specPattern: "cypress/e2e/**/*.cy.{js,jsx,ts,tsx}",
    viewportWidth: 1280,
    viewportHeight: 720,
  },
});
```

---

## Writing Cypress Specs

Write tests under `cypress/e2e/` using Cypress's assertion chains:

```javascript title="cypress/e2e/test_spec.cy.js"
describe("CKAN Extension Views", () => {
  
  // Clean or seed database before running specs
  beforeEach(() => {
    // Run custom shell command to reset database state
    cy.exec("ckan -c test.ini db clean --yes && ckan -c test.ini db init");
  });

  it("should display public items index page", () => {
    // Navigate to page
    cy.visit("/my-extension/items");

    // Assert page header and title
    cy.title().should("include", "Public Items");
    cy.get("h1").should("contain", "Items List");
  });

  it("should restrict creating items to logged in users", () => {
    cy.visit("/my-extension/items/new");

    // Expect redirecting to CKAN login page
    cy.url().should("include", "/user/login");
    cy.get(".flash-banner").should("contain", "Unauthorized");
  });
});
```

---

## Custom Command for Login

Define custom helpers inside `cypress/support/commands.js` to reuse login sequences:

```javascript title="cypress/support/commands.js"
Cypress.Commands.add("login", (username, password) => {
  cy.visit("/user/login");
  cy.get("input[name=login]").type(username);
  cy.get("input[name=password]").type(password);
  cy.get("form").submit();
});
```

Use it in your specs:

```javascript
it("should allow creating items when logged in", () => {
  cy.login("admin_user", "password123");
  cy.visit("/my-extension/items/new");
  // Fill and submit item form
});
```
