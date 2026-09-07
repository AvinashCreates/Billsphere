# DEMO

# BillSphere 15-Minute Live Demonstration Script

## 1. Presentation Brief

**Project:** BillSphere

**Presentation length:** 15 minutes

**Presenters:** Exactly eight team members, Person 1 through Person 8

**Audience outcome:** Demonstrate one complete billing journey from customer registration through plan selection, checkout, confirmation, invoices, payment records, notifications, and administrator operations.

**Core message:** BillSphere connects customer self-service, recurring subscriptions, payment confirmation, invoicing, administrative visibility, analytics, and auditability in one workflow.

### Master admin credentials

```text
Username: admin@billsphere.com
Password: Admin@123456
```

Only one master administrator account is used for the demonstration. Do not change its role, deactivate it, or delete it during the presentation.

### Customer demo account

Person 1 creates this account live during the presentation. Use a unique address so the demo does not collide with an existing account:

```text
First name: Demo
Last name: Customer
Email: demo.customer+YYYYMMDDHHMM@example.com
Phone: +91 98765 43210
Password: DemoUser@123
Role: Customer
```

Replace `YYYYMMDDHHMM` with the current date and time. Record the exact email and password in a private presenter note, not on the public recording.

### Local services

Open three terminal windows before the presentation. Keep the terminal visible only during setup.

**BillSphere backend:**

```powershell
cd "C:\Users\pc\Desktop\INfY\INFY\backend"
$env:PYTHONPATH = (Get-Location).Path
& ".\.venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**BillSphere frontend:**

```powershell
cd "C:\Users\pc\Desktop\INfY\INFY\frontend"
npm run dev -- --host localhost --port 5173
```

**PulseFlow external storefront:**

```powershell
cd "C:\Users\pc\Desktop\INfY\app"
python -m http.server 3001 --bind 127.0.0.1
```

Open these URLs in one browser window:

```text
BillSphere: http://localhost:5173
PulseFlow: http://127.0.0.1:3001
API documentation: http://127.0.0.1:8000/docs
```

### Presentation rules

- Use a disposable customer account.
- Never expose the customer password or admin password on a recording longer than necessary.
- Do not refresh during a payment confirmation transition unless the presenter is explicitly showing persistence.
- Pause for two seconds after every successful state change.
- If an email is delayed, use the confirmation link displayed by the checkout screen or the configured demo mailbox.
- If a live dependency is unavailable, use the prepared screenshots or the backup account and state the reason briefly.
- Do not claim that a feature is live if the screen is showing a fallback or mock value.

---

## 2. Minute-by-Minute Allocation

| Time | Presenter | Segment | Handoff result |
|---|---|---|---|
| 00:00–02:00 | Person 1 | Introduction, landing page, signup, login | A newly created customer is authenticated |
| 02:00–03:30 | Person 2 | Customer onboarding and profile | Customer identity and profile are visible |
| 03:30–05:30 | Person 3 | Customer dashboard, plans, and checkout setup | A plan checkout is submitted |
| 05:30–07:15 | Person 4 | Confirmation, payment, invoice, and history | Payment is confirmed and billing records are visible |
| 07:15–09:00 | Person 5 | Admin transition and overview | Master admin dashboard is loaded |
| 09:00–11:00 | Person 6 | Customer and user management | The demo customer is found and reviewed |
| 11:00–13:30 | Person 7 | Analytics, logs, configuration, and external storefront | Operational evidence and integration are shown |
| 13:30–15:00 | Person 8 | Summary, technology, verification, and Q&A | The presentation closes and questions open |

---

# 3. Live Script

## Person 1 — Introduction, Landing Page, and Authentication

**Time:** 00:00–02:00

### 00:00–00:20 — Opening

**[Action: Shares screen. Shows the BillSphere landing page at `http://localhost:5173`.]

**Person 1 says:**

> “Good morning. We are presenting BillSphere, a subscription billing and payment-operations platform. BillSphere connects customers, plans, subscriptions, payment confirmation, invoices, notifications, and administrator oversight in one system. We will follow one customer from account creation to billing, and then show how the master administrator sees the same activity from the operations side.”

**[Visual: Landing page hero, navigation, primary call-to-action, and product sections are visible.]

**Person 1 says:**

> “The landing page introduces the platform as a working billing product rather than a static marketing page. The important entry points are registration, login, customer plans, and the authenticated workspace.”

### 00:20–00:40 — Service and security context

**[Action: Briefly switches to the browser tab at `http://127.0.0.1:8000/docs`.]

**Person 1 says:**

> “Behind the interface is a FastAPI service with PostgreSQL-backed models, JWT authentication, subscription lifecycle logic, payment and invoice services, tax calculation, notifications, audit logs, and background scheduling. The API documentation is available for inspecting the live contract.”

**[Action: Returns to the BillSphere landing page.]

### 00:40–01:25 — Dynamic customer signup

**[Action: Clicks `Register` or opens `http://localhost:5173/register`.]

**Person 1 says:**

> “I will now create a customer account dynamically. This is not a pre-filled customer profile. The form sends a first name, last name, email, phone number, password, and the customer role to the backend.”

**[Action: Enters the following values.]

```text
First name: Demo
Last name: Customer
Email: demo.customer+YYYYMMDDHHMM@example.com
Phone: +91 98765 43210
Password: DemoUser@123
Role: Customer
```

**Person 1 says:**

> “The role remains Customer. The backend validates the request, hashes the password, stores the account, and returns a registration result. The password is never displayed as plain text in the application data model.”

**[Action: Clicks the registration button.]

**[Visual: Success message appears.]

**Person 1 says:**

> “The account has been created. I will now move to login and use the same account so the rest of the demonstration is based on real authenticated state.”

### 01:25–02:00 — Customer login and handoff

**[Action: Opens `/login`. Enters the demo customer email and `DemoUser@123`.]

**Person 1 says:**

> “On login, BillSphere sends the credentials to the authentication endpoint. A successful response provides an access token. The frontend then loads the current user profile and uses the returned role to choose the customer dashboard.”

**[Action: Clicks `Login`. Waits for the customer dashboard.]

**[Visual: Customer dashboard loads with the authenticated customer name.]

**Person 1 says:**

> “The customer is authenticated and the real customer identity is visible. Person 2 will now complete the onboarding and profile portion of the journey.”

**[Handoff: Person 1 gives control of the screen to Person 2.]

---

## Person 2 — Customer Onboarding and Profile Setup

**Time:** 02:00–03:30

### 02:00–02:20 — Confirm the customer workspace

**[Action: Shows `http://localhost:5173/customer/dashboard`.]

**Person 2 says:**

> “I am continuing as the customer created by Person 1. The customer workspace is protected by authentication, and its billing requests are made only after the authenticated session has been loaded. This prevents the dashboard from showing misleading zero values while a token is still being checked.”

**[Action: Points to the customer navigation.]

**Person 2 says:**

> “The customer navigation provides access to My Plan, Plans, Invoices, Payments, Payment History, Billing, Notifications, Settings, Help, and Profile.”

### 02:20–03:00 — Profile and photo

**[Action: Opens `/profile`.]

**Person 2 says:**

> “I will open Profile to complete the identity setup. The name, email, phone, and account information are taken from the authenticated customer session where available.”

**[Action: Enters or confirms the phone number and writes a short About value such as `Demo account for BillSphere walkthrough`.]

**[Action: Clicks `Upload photo`, chooses a prepared square JPG or PNG, and waits for the preview.]

**Person 2 says:**

> “The customer can keep a profile photo. The selected image is previewed immediately and stored for this account, so the avatar remains available when the user returns to the profile page.”

**[Visual: Circular profile image appears.]

**[Action: Clicks `Save Profile`.]

**Person 2 says:**

> “The profile update is now visible in the customer experience. This is a customer-owned identity setting; it does not change billing authorization or administrator permissions.”

### 03:00–03:30 — Preferences and handoff

**[Action: Opens `/settings`. Shows Appearance, Notifications, Billing and Payments, Subscription, Invoice Preferences, Security, Privacy, and Regional sections.]

**Person 2 says:**

> “Settings groups the customer’s preferences into understandable sections. For the demo, I will leave email confirmations, invoice notifications, billing reminders, and renewal reminders enabled. Those settings match the workflow we are about to demonstrate.”

**[Action: Returns to `/customer/dashboard`.]

**Person 2 says:**

> “The account is ready. Person 3 will now select a real plan and begin the billing action.”

**[Handoff: Person 2 gives control to Person 3.]

---

## Person 3 — Customer Main Dashboard and Core Action

**Time:** 03:30–05:30

### 03:30–04:00 — Customer dashboard

**[Action: Shows `/customer/dashboard`.]

**Person 3 says:**

> “The main customer dashboard is the operational home for the account. It summarizes the current subscription, upcoming billing information, recent invoices, payment activity, and account actions.”

**[Action: Opens `/customer/plans`.]

### 04:00–04:35 — Browse the catalog

**Person 3 says:**

> “Plans are loaded from the backend catalog. Each plan has a platform, tier, billing cycle, price, trial information, and feature entitlements. I will select a plan that is easy to read on screen, preferably a monthly or yearly Basic, Standard, or Premium plan.”

**[Action: Search or scroll. Selects one plan.]

**[Visual: Plan card or plan detail page opens at `/customer/plans/:planId`.]

**Person 3 says:**

> “The selected plan is resolved by its plan ID. The application carries that identifier into the confirmation route, which prevents the confirmation page from becoming disconnected from the plan the customer selected.”

### 04:35–05:05 — Review subscription details

**[Action: Opens the plan detail and clicks `Continue`, `Choose Plan`, or the equivalent primary action.]

**[Visual: Confirmation page opens at `/customer/plans/:planId/confirm`.]

**Person 3 says:**

> “The confirmation screen summarizes the platform, tier, billing cycle, price, trial period, included features, customer limits, invoice limits, tax explanation, and the next step. The customer can review the commitment before entering payment.”

**[Action: Reviews the displayed plan name, billing cycle, price, trial, and features.]

### 05:05–05:30 — Enter checkout

**[Action: Clicks `Continue to Payment`.]

**[Visual: Payment screen opens at `/customer/plans/:planId/payment`.]

**Person 3 says:**

> “The payment route is plan-specific. It receives the plan ID from the URL and loads the matching plan from the API. This is important because the general Payments navigation is payment history, while this route is the active checkout for one selected plan.”

**[Action: Hands the screen to Person 4 while the payment page is loaded.]

**Person 3 says:**

> “The checkout is ready. Person 4 will complete the customer-side billing interaction and verify the generated records.”

**[Handoff: Person 3 gives control to Person 4.]

---

## Person 4 — Customer Advanced Interactions and Billing Evidence

**Time:** 05:30–07:15

### 05:30–05:55 — Complete payment form

**[Action: On `/customer/plans/:planId/payment`, selects the available demo payment method.]

**Person 4 says:**

> “This is the secure checkout surface. I will provide the required customer information, phone number, billing address, payment method details accepted by the demo flow, and confirm the terms.”

**[Action: Completes full name, registered email, phone, address, city, state, and postal code. Selects UPI, card, net banking, or wallet as appropriate for the visible form.]

**Person 4 says:**

> “The form validates required information before submission. The backend then creates the payment, invoice, and subscription records through the billing engine. In this demonstration the gateway is a controlled mock payment flow, so the audience can observe the complete lifecycle without using a real card.”

### 05:55–06:20 — Submit checkout

**[Action: Checks the confirmation checkbox and clicks `Pay`.]

**[Visual: Processing state appears. Then the payment-pending screen or confirmation-link state appears.]

**Person 4 says:**

> “The payment request has been accepted. The initial state may be pending confirmation because BillSphere deliberately separates submitting a payment from confirming it. This protects the subscription from becoming active before the confirmation step is completed.”

**[Action: Clicks the displayed confirmation link if email delivery is unavailable, or opens the confirmation email in the prepared mailbox.]

### 06:20–06:45 — Confirm payment

**[Action: Opens `/payment-confirmation?token=...`.]

**Person 4 says:**

> “The confirmation link contains a single-use payment token. The confirmation page loads the plan, amount, invoice status, payment status, and subscription status before presenting the decision.”

**[Action: Clicks `YES - CONFIRM PAYMENT`.]

**[Visual: Enlarged receipt-print animation plays. The payment card appears first, then the receipt prints down with a serrated edge, total paid, status, and barcode.]

**Person 4 says:**

> “This is the successful payment state. The receipt animation makes the transition visible: the payment is no longer just a form submission; it has become a completed billing event with a receipt and an active subscription.”

**[Action: Waits until the animation settles.]

### 06:45–07:15 — Verify customer records

**[Action: Opens `/customer/subscriptions` or My Plan.]

**Person 4 says:**

> “The subscription now appears in My Plan with its lifecycle status and next billing information.”

**[Action: Opens `/customer/invoices`.]

**Person 4 says:**

> “The invoice is available for review and download. It contains the billing record associated with the checkout.”

**[Action: Opens `/customer/payment-history`.]

**Person 4 says:**

> “Payment History now reads real payment records from the authenticated API rather than placeholder sample data. I can open a payment detail view and download its receipt.”

**[Action: Opens `/customer/notifications`, opens the payment or invoice notification, and clicks its action.]

**Person 4 says:**

> “Notification actions are connected to the customer screens. A payment notification opens payment history, an invoice notification opens invoices, and a subscription notification opens My Plan.”

**[Handoff: Person 4 gives control to Person 5.]

**Person 4 says:**

> “The customer-side billing journey is complete. Person 5 will now switch from customer self-service to the master administrator workspace.”

---

## Person 5 — Transition to Admin and Overview

**Time:** 07:15–09:00

### 07:15–07:35 — Sign out

**[Action: Opens the customer menu or sidebar and clicks `Logout`.]

**Person 5 says:**

> “I will sign out before switching roles. Logout removes the customer access token and ends the customer session. The next login will be evaluated independently by the backend.”

**[Visual: Login page appears.]

### 07:35–08:00 — Master administrator login

**[Action: Enters the single master administrator account.]

```text
Username: admin@billsphere.com
Password: Admin@123456
```

**Person 5 says:**

> “There is one master administrator account for this demonstration. BillSphere does not infer administrator access from the browser interface. The backend validates the token subject, loads the user from the database, confirms the account is active, and then checks the stored administrator role.”

**[Action: Clicks `Login`.]

**[Visual: `/admin/dashboard` loads.]

### 08:00–08:35 — Admin dashboard overview

**Person 5 says:**

> “The administrator dashboard is a separate operational workspace. It loads plans, registered customer accounts, subscriptions, invoices, payments, refunds, and audit logs through protected APIs.”

**[Action: Points to the Overview section.]

**Person 5 says:**

> “The primary metrics are Monthly Recurring Revenue, Active Subscriptions, Customers, Failed Payments, Total Revenue, Trial Customers, Invoices, and Payments. These values are calculated from the backend records loaded for the complete customer population, not only records owned by the admin account.”

### 08:35–09:00 — Explain zero-safe loading

**[Action: Clicks Refresh and waits for the dashboard response.]

**Person 5 says:**

> “The dashboard waits for authentication before requesting protected data and normalizes paginated response wrappers such as plans, customers, and items. If an endpoint fails, the interface reports the problem instead of silently presenting every metric as zero.”

**[Action: Shows the customer count and revenue-related cards.]

**Person 5 says:**

> “The customer and payment event created by the earlier presenters are now available to administration. Person 6 will drill into the customer and user management screens.”

**[Handoff: Person 5 gives control to Person 6.]

---

## Person 6 — Admin Customer Management and User Access

**Time:** 09:00–11:00

### 09:00–09:35 — Customer directory

**[Action: Clicks `Customers` in the admin navigation or opens `/customers`.]

**Person 6 says:**

> “The Customer Directory is restricted to administrators. It uses the admin customer endpoint, which returns registered customer accounts and enriches them with billing country, platform, billing cycle, payment status, renewal date, and trial date when available.”

**[Action: Searches for `Demo Customer` or the unique demo email.]

**[Visual: The customer created by Person 1 appears.]

**Person 6 says:**

> “This is the same customer created at the beginning of the presentation. The account is represented by the authenticated user record, while the billing information is linked through the customer record used by subscriptions and invoices.”

**[Action: Applies the payment status, platform, or billing-cycle filter.]

**Person 6 says:**

> “The filters operate on real billing attributes. A customer without a subscription is still visible with a no-subscription status; a customer with the completed demo checkout shows the current payment and plan state.”

### 09:35–10:05 — Admin customer operations

**[Action: Shows the export button without deleting the demo customer. Optionally exports the current list to XLSX.]

**Person 6 says:**

> “Operations can export the visible customer roster for reconciliation. The export includes the customer identity, country, platform, plan type, payment status, billing dates, and registration date.”

**[Action: Do not delete the demonstration account. If deletion must be shown, use a separate disposable account and confirm the dialog.]

**Person 6 says:**

> “For safety, I will not delete the customer that is supporting this presentation. The UI does require confirmation, and the protected admin operation prevents the master administrator from deleting itself.”

### 10:05–10:45 — Admin user management

**[Action: Opens `/admin/users` or selects `User access`.]

**Person 6 says:**

> “User Access is the dedicated administrator-only screen. It loads users from the protected admin users endpoint and shows name, email, role, account status, verification status, and creation date.”

**[Action: Searches for the demo customer.]

**Person 6 says:**

> “The customer account created earlier is visible here as a Customer. An administrator can activate or deactivate a disposable test account and can change a disposable test user’s role.”

**[Action: Do not change the master admin. If demonstrating a role/status change, use an additional disposable user.]

**Person 6 says:**

> “The current master administrator remains protected. The backend rejects attempts to remove the current admin’s administrator role or delete the current admin account.”

### 10:45–11:00 — Handoff

**[Action: Returns to `/admin/dashboard`.]

**Person 6 says:**

> “The customer identity, billing records, and access controls are connected. Person 7 will now show the operational analytics, audit evidence, configuration areas, and external storefront integration.”

**[Handoff: Person 6 gives control to Person 7.]

---

## Person 7 — Analytics, Logs, Configuration, and Integration

**Time:** 11:00–13:30

### 11:00–11:35 — Subscriptions and invoices

**[Action: In `/admin/dashboard`, opens the `Subscriptions` section.]

**Person 7 says:**

> “Subscriptions are displayed with their customer, plan, status, start date, and period end. The lifecycle supports trial, active, past-due, paused, and cancelled states, depending on the records created by the billing engine.”

**[Action: Opens `Invoices`.]

**Person 7 says:**

> “Invoices show invoice number, customer, plan, amount, tax, status, due date, and available detail actions. The invoice is generated as part of the subscription billing flow rather than being a disconnected static document.”

**[Action: Opens an invoice detail modal and, if available, clicks the PDF action.]

### 11:35–12:05 — Payments and refunds

**[Action: Opens `Payments`.]

**Person 7 says:**

> “Payment Operations shows payment IDs, customer, invoice, amount, method, transaction reference, status, and date. Successful, pending, failed, and refunded states are normalized for operational review.”

**[Action: Opens `Refunds`.]

**Person 7 says:**

> “Refund records are tied back to payments and invoices. This is the point where finance and support teams can inspect the downstream effect of a refund without searching across unrelated screens.”

### 12:05–12:35 — Analytics

**[Action: Opens `Analytics`.]

**Person 7 says:**

> “Analytics calculates recurring revenue, active subscriptions, trials, failed invoices, successful payments, total payments, and total invoices from the current dataset. Revenue distribution is grouped by active plan.”

**[Action: Points to MRR and successful payment totals.]

**Person 7 says:**

> “Monthly recurring revenue is based on active subscriptions and plan prices, adjusted for the billing cycle. Revenue totals are based on completed payment records, so pending checkout requests do not inflate recognized revenue.”

### 12:35–13:00 — Audit and settings

**[Action: Opens `Audit Logs`.]

**Person 7 says:**

> “Audit Logs provide a chronological trail of authentication, billing, subscription, and administrative events. Each entry can include the actor, action, module, entity, description, and timestamp.”

**[Action: Opens `Settings`.]

**Person 7 says:**

> “Settings exposes the active backend API, authentication status, plan count, and customer count. These indicators are useful during operations because they distinguish a connected data source from a visually populated but disconnected screen.”

### 13:00–13:20 — External storefront

**[Action: Opens `http://127.0.0.1:3001` in the PulseFlow tab.]

**Person 7 says:**

> “PulseFlow is an external storefront. It demonstrates that plan discovery can happen outside the billing workspace while BillSphere remains the system that resolves the plan, authenticates the customer, and processes the billing workflow.”

**[Action: Selects a featured plan and clicks its call-to-action.]

**[Visual: Browser redirects to a BillSphere plan or confirmation route with a plan identifier.]

**Person 7 says:**

> “The storefront passes the selected plan identifier into BillSphere. The receiving page loads the same backend plan data instead of relying on hardcoded storefront values.”

### 13:20–13:30 — Handoff

**[Action: Returns to the admin dashboard or a prepared verification terminal.]

**Person 7 says:**

> “We have now demonstrated the operational, analytical, audit, and integration sides. Person 8 will summarize the complete journey, technology, and verification results.”

**[Handoff: Person 7 gives control to Person 8.]

---

## Person 8 — Conclusion, Verification, and Q&A

**Time:** 13:30–15:00

### 13:30–14:05 — End-to-end summary

**[Action: Shares the admin dashboard overview or a prepared architecture slide.]

**Person 8 says:**

> “BillSphere has taken one account through the complete lifecycle: dynamic customer registration, JWT login, profile setup, plan discovery, plan confirmation, checkout, payment confirmation, subscription activation, invoice creation, payment history, notifications, and administrator review.”

**Person 8 says:**

> “The customer and admin views are connected through shared backend records. The customer sees only the customer workspace and its own billing data. The administrator sees the operational population, with protected access checks based on the database user role.”

### 14:05–14:35 — Technology summary

**[Visual: Shows the architecture or API documentation tab briefly.]

**Person 8 says:**

> “The backend uses Python, FastAPI, SQLAlchemy, PostgreSQL, Alembic, Pydantic, JWT authentication, Celery, Redis, and ReportLab. The frontend uses React, TypeScript, Vite, React Router, Lucide icons, responsive CSS, and real API service modules. The system also includes tax handling, invoice line items, payment retries, refunds, notifications, audit logs, and an external storefront integration.”

### 14:35–14:50 — Verification

**[Action: Shows the terminal and runs the verification commands.]

```powershell
cd "C:\Users\pc\Desktop\INfY\INFY\backend"
python -m pytest tests/ -q

cd ..\frontend
npm run lint
npm run build
```

**Person 8 says:**

> “The final verification checks the backend test suite, frontend linting, and the production build. These checks confirm that the tested API behavior, TypeScript compilation, bundling, and frontend code quality are all passing before release.”

**[Visual: Keep the successful command output visible for two seconds.]

### 14:50–15:00 — Close and Q&A

**Person 8 says:**

> “The value of BillSphere is the connection between customer experience and operational control. A customer can discover a plan, complete a secure confirmation flow, and retrieve billing records. An administrator can then monitor customers, payments, invoices, subscriptions, analytics, and audit history from one protected workspace.”

**Person 8 says:**

> “Thank you for your time. This concludes the BillSphere demonstration, and we officially open the floor for questions.”

**[Action: Stops screen sharing only after the audience begins questions.]

---

# 4. Presenter Runbook

## Before the room opens

1. Start PostgreSQL and Redis, or confirm the Docker services are healthy.
2. Start the backend from the Python 3.12 virtual environment.
3. Start the frontend from `INFY/frontend`.
4. Start the PulseFlow static server from `app`.
5. Open `/`, `/register`, `/login`, `/customer/dashboard`, `/admin/dashboard`, `/admin/users`, `/customers`, `/customer/payment-history`, `/customer/invoices`, `/customer/notifications`, and `/profile` in browser tabs if rapid navigation is needed.
6. Confirm the master admin login works.
7. Confirm a disposable customer account can be created.
8. Confirm at least one active plan exists.
9. Confirm the API docs page loads.
10. Prepare one square profile image and one disposable test user if role/status management will be shown.

## During signup

- Use a unique email address.
- Never use a presenter’s personal password.
- Keep the customer credentials available privately for Person 2.
- Wait for the registration response before opening login.

## During checkout

- Select a plan with a visible price and clear feature list.
- Use the demo payment method accepted by the running application.
- Complete every required field before pressing `Pay`.
- If the payment is pending, open the generated confirmation link.
- Click confirmation once and wait for the receipt animation to finish.
- Do not click the confirmation action repeatedly.

## During admin operations

- Use only `admin@billsphere.com` for the master admin.
- Never change the master admin to Customer.
- Never deactivate or delete the master admin.
- Use a second disposable account for destructive user-management examples.
- Keep the demo customer account because later presenters rely on its records.

## If a live step fails

**Customer signup fails:** Use a prepared disposable customer account and state that the live database path was already verified.

**Email is delayed:** Use the confirmation URL displayed by the payment-pending page.

**A dashboard metric is zero:** Click Refresh, confirm the admin token is valid, and show the relevant data screen. Do not describe zero as a meaningful business result until the endpoint response has been checked.

**The admin page redirects to login:** Sign in again with the master admin and return to the original route.

**The external storefront is unavailable:** Continue with the BillSphere plan detail route and describe the storefront as an optional integration demonstration.

**The API is unavailable:** Stop the presentation briefly, show the API docs or prepared screenshots, and do not invent live data.

---

# 5. Audience Q&A Preparation

## How is customer data protected?

“Protected API routes require a valid JWT access token. Customer queries are scoped to the authenticated customer, while administrator queries validate the user record and administrator role from the database.”

## Is the payment gateway real?

“The demonstration uses a controlled mock payment flow so we can show the full payment, invoice, subscription, confirmation, retry, and refund lifecycle safely. The service boundary is designed for a real gateway integration.”

## What happens after a failed payment?

“The subscription can enter a past-due state, payment retry records can be scheduled, and the retry workflow can eventually cancel the subscription after configured attempts.”

## Where does recurring revenue come from?

“MRR is calculated from active subscriptions and their plan prices, with annual and quarterly billing normalized into a monthly value.”

## Why is email confirmation separate from checkout?

“It prevents a subscription from becoming active until the payment decision is explicitly confirmed. This makes the state transition visible and auditable.”

## Can administrators edit every customer record?

“Administrators can review customer accounts and billing activity through protected operational screens. Destructive actions should be performed only on disposable accounts during a demonstration.”

## How are invoices generated?

“The billing engine creates invoice records and line items associated with subscription charges, usage, proration, and applicable tax lines. The customer and administrator interfaces expose those records for review and PDF download.”

---

# 6. Final Presenter Checklist

- [ ] Exactly eight presenters are assigned.
- [ ] Each presenter knows the first sentence and final handoff sentence.
- [ ] The customer demo email is unique.
- [ ] The master admin account has not been modified.
- [ ] Backend, frontend, database, Redis, and external storefront are running.
- [ ] The browser is using `localhost:5173` consistently for BillSphere.
- [ ] The API is available at `127.0.0.1:8000/docs`.
- [ ] The customer profile photo is prepared.
- [ ] The selected plan is available and has a visible price.
- [ ] The confirmation link or demo mailbox is ready.
- [ ] The audience can see the enlarged receipt-print success animation.
- [ ] Payment history shows real records, not placeholder data.
- [ ] Invoice and notification actions are ready to demonstrate.
- [ ] Admin dashboard refresh has completed before Person 5 begins.
- [ ] No presenter will delete the master admin or the demo customer.
- [ ] Backend tests, frontend lint, and frontend build commands are ready for the closing verification.
