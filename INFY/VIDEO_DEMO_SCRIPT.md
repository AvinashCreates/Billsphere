# BillSphere Screen Recording Demo Script

## Recording Setup

Record the browser and the terminal. Use one browser window with tabs for:

- BillSphere: `http://localhost:5173`
- PulseFlow: `http://127.0.0.1:3001`
- API docs: `http://127.0.0.1:8000/docs`

Keep the terminal visible for the opening setup only, then switch to the
browser for the product walkthrough. Pause briefly after each major result so
the viewer can read the screen.

## Scene 1 - Start The Application

**On screen:** Open three terminal panes.

**Action:**

```powershell
cd C:\Users\pc\Desktop\INfY\INFY\backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

```powershell
cd C:\Users\pc\Desktop\INfY\INFY\frontend
npm run dev -- --host localhost
```

```powershell
cd C:\Users\pc\Desktop\INfY\app
python -m http.server 3001 --bind 127.0.0.1
```

**Voiceover:** “This is BillSphere, a subscription billing platform. I’m
starting the FastAPI backend, the React frontend, and the PulseFlow external
storefront. The backend runs on port 8000, BillSphere runs on port 5173, and
the storefront runs on port 3001.”

**Action:** Open the three URLs and briefly show the landing page, storefront,
and API docs.

**Voiceover:** “The three services are available, and the API documentation is
available for inspecting the live backend contract.”

## Scene 2 - Create A Customer Account

**Action:** Open `http://localhost:5173/register`. Enter a first name, last
name, email, phone, and a password of at least eight characters. Leave the
role as Customer and submit.

**Voiceover:** “I’m registering a standard customer account. The form sends
the user profile to the backend, where the password is hashed and the account
is created with the customer role.”

**Action:** Confirm the success message, then open the login page.

## Scene 3 - Customer Login And Dynamic Profile

**Action:** Log in with the new customer account.

**Voiceover:** “After login, BillSphere receives a JWT access token and the
user role. The interface uses the authenticated user’s real name and email,
so the dashboard is not tied to hardcoded profile data.”

**Action:** Show the customer dashboard, header name, Settings, and Profile.

**Voiceover:** “The customer dashboard provides the subscription overview,
recent activity, billing, invoices, payments, notifications, and account
settings.”

## Scene 4 - Browse Real Plans

**Action:** Open Customer Plans. Search or scroll through platforms and open a
plan detail page.

**Voiceover:** “These plans are loaded from PostgreSQL. The catalog contains
53 platforms and 318 monthly and yearly plan records across three tiers.”

**Action:** Select a plan and open its confirmation page.

**Voiceover:** “The selected plan is resolved from the API response and shown
on the confirmation page. This is the path that previously displayed the
‘Confirmation unavailable’ error.”

## Scene 5 - Subscription Checkout

**Action:** Review the plan, billing cycle, tax, and total. Continue to
Payment and enter the demo payment details accepted by the application.

**Voiceover:** “The checkout flow calculates the billing amount, applies the
configured India GST tax rules, and creates the payment, invoice, and
subscription records through the billing engine.”

**Action:** Submit payment and show the success or confirmation screen.

**Voiceover:** “The successful checkout returns the payment, invoice, and
subscription status. The customer can now view the active subscription and
its next billing information.”

## Scene 6 - Billing Records And Lifecycle Actions

**Action:** Open My Plan, Billing, Payment History, and Invoices.

**Voiceover:** “The subscription appears in My Plan. Billing shows the active
cycle, Payment History shows the transaction, and Invoices shows the generated
invoice available for review or download.”

**Action:** Return to My Plan and demonstrate a permitted lifecycle action,
such as renewal or cancellation at period end. Confirm the resulting status.

**Voiceover:** “Subscription lifecycle actions are persisted and reflected in
the interface. The backend state machine supports trial, active, past-due,
and cancelled states, with audit history for important changes.”

## Scene 7 - Admin Login

**Action:** Sign out. Log in with:

```text
Email: admin@billsphere.com
Password: Admin@123456
```

**Voiceover:** “Now I’m switching to the administrator account. Role-based
access control identifies this account as an admin and exposes the admin
workspace.”

**Action:** Show the Admin Dashboard.

**Voiceover:** “The admin dashboard summarizes customers, subscriptions,
revenue, plans, payments, and operational activity.”

## Scene 8 - Admin Customer And Billing Operations

**Action:** Open Customers, Invoices, and the admin reporting or support
sections. Apply a filter and open a record.

**Voiceover:** “Administrators can inspect customer records, filter billing
activity, review invoices, and monitor the account lifecycle from the
operations workspace.”

**Action:** Open Plans and show the available catalog.

**Voiceover:** “The plan catalog is available to operations staff for reviewing
platforms, tiers, billing cycles, and pricing.”

## Scene 9 - Admin User Management

**Action:** Open `http://localhost:5173/admin/users` or select User access in
the sidebar.

**Voiceover:** “User access is a dedicated admin-only screen. It loads the
real user list from the protected `/api/v1/admin/users` endpoint.”

**Action:** Change a test user between Customer and Admin using the role
selector. Toggle the account status. Do not change the current admin to
Customer or delete the current admin.

**Voiceover:** “The administrator can change roles and activate or deactivate
accounts. The backend prevents an administrator from removing their own admin
role or deleting their own account.”

**Action:** Optionally delete a disposable test account and show the row
disappearing.

**Voiceover:** “A user can also be deleted after confirmation. The UI refreshes
immediately after the backend confirms the operation.”

## Scene 10 - PulseFlow External Integration

**Action:** Open `http://127.0.0.1:3001`. Browse the storefront and select a
featured plan.

**Voiceover:** “PulseFlow is an independent storefront integrated with
BillSphere. A customer can discover a plan outside the billing application.”

**Action:** Click the storefront plan CTA and show the browser redirect to the
BillSphere confirmation route.

**Voiceover:** “Selecting a plan redirects to BillSphere on localhost:5173,
using the plan identifier in the URL. The confirmation page then loads the
same plan data from the backend.”

## Scene 11 - Close With Verification

**Action:** Show the terminal and run the verification commands:

```powershell
cd C:\Users\pc\Desktop\INfY\INFY\backend
python -m pytest tests/ -q
cd ..\frontend
npm run lint
npm run build
```

**Voiceover:** “To close the demo, I’m showing the verification results. The
backend suite passes all 87 tests, ESLint passes, and the TypeScript and Vite
production build completes successfully.”

**Voiceover:** “This demonstrates the complete BillSphere workflow: secure
authentication, dynamic user data, real plan loading, checkout and billing,
subscription lifecycle management, admin operations, user access control, and
external storefront integration.”

## Recording Notes

- Use a disposable customer account for checkout and deletion demonstrations.
- Avoid recording passwords other than the documented demo admin credential.
- If the backend was already running before the demo, restart it after code
  changes so newly added routes are loaded.
- The unauthenticated plans endpoint may return HTTP 401; that is expected.
  Log in before demonstrating customer plan loading.