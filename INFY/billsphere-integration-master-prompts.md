# BillSphere Integration — Master Prompts for GitHub Copilot

Two ready-to-paste prompts for connecting client apps to **BillSphere** (your FastAPI + PostgreSQL billing platform) for plan purchasing. BillSphere stays the single source of truth for plans, subscriptions, invoices, and payments. Each client app (Spotify-style, E-learning) becomes a **consumer** of BillSphere's API — it never runs its own billing logic.

Fill in the `<<...>>` placeholders before pasting into Copilot Chat/Agent mode in each app's repo.

---

## 0. Shared Architecture Context (paste this first in BOTH repos)

```
CONTEXT: I'm integrating this application with an external billing platform called
BillSphere. BillSphere is a separate FastAPI + PostgreSQL service that owns all
subscription plans, subscriptions, invoices, and payments. This app should NOT
implement its own billing/plan/payment logic — it should call BillSphere's REST API.

BillSphere API base URL: <<BILLSPHERE_API_BASE_URL>>  (e.g. http://127.0.0.1:8000/api/v1)

Key BillSphere endpoints available to integrate against:
- POST /auth/register            → create a BillSphere customer account
- POST /auth/login               → returns JWT access token
- GET  /auth/me                  → current authenticated customer
- POST /auth/refresh             → refresh JWT token
- GET  /customers/customers      → customer records
- GET  /plans/plans              → list available plans (filterable by platform)
- POST /subscriptions/subscriptions        → create a subscription for a plan
- GET  /subscriptions/subscriptions        → view/list subscriptions
- PATCH/PUT on subscription id   → update/cancel subscription
- GET  /invoices/invoices        → invoice history
- GET  /payments/payments/       → payment history/status

Auth model: JWT Bearer tokens. Every authenticated call needs
`Authorization: Bearer <token>` header. Token is obtained via BillSphere login,
not this app's own auth system (or, if this app already has its own auth, we will
map/sync the two — see step 1 below).

Plans in BillSphere are tagged by a `platform` field. This app's plans should be
filtered using platform = "<<PLATFORM_NAME>>".

Do not hardcode plan prices/names in this app — always fetch them live from
BillSphere's /plans/plans endpoint so BillSphere remains the single source of truth.
```

---

## 1. Master Prompt — Spotify-style Music App

```
ROLE: You are integrating this music-streaming web app with BillSphere, an
external billing/subscription platform (FastAPI backend, REST API, JWT auth).
BillSphere already exists and is running — you are only building the CLIENT-SIDE
integration in THIS repo, plus any small backend proxy endpoints this app needs.

GOAL
Let a logged-in user of this music app browse subscription tiers (e.g. Free,
Premium Individual, Premium Family), purchase/upgrade a plan, and have the app's
own feature-gating (ad-free playback, offline downloads, high-bitrate audio,
number of family accounts, skip limits) driven by the subscription status
returned by BillSphere — not by local state.

BILLSPHERE CONNECTION DETAILS
- Base URL: <<BILLSPHERE_API_BASE_URL>>
- Platform tag to filter plans by: "spotify" (or <<YOUR_PLATFORM_TAG>>)
- Auth: JWT bearer tokens from BillSphere's /auth endpoints

WHAT TO BUILD

1. Account linking / auth bridge
   - If this app has its own user accounts, add a step during signup/first
     upgrade attempt that creates a matching BillSphere customer via
     POST /auth/register (or logs in an existing one via POST /auth/login),
     and securely stores the returned JWT (httpOnly cookie or secure storage —
     never localStorage for the token).
   - Add a token refresh flow using POST /auth/refresh so sessions don't expire
     mid-playback.
   - If this app does NOT have its own auth yet, use BillSphere as the auth
     provider directly.

2. Plans / Pricing page
   - Fetch live plans from GET /plans/plans?platform=spotify (or equivalent
     query param BillSphere exposes) on page load.
   - Render tiers dynamically from the API response (name, price, currency,
     billing cycle, trial period, feature list) — do not hardcode plan copy.
   - Highlight the user's current plan if GET /subscriptions/subscriptions
     shows an active subscription.

3. Purchase / upgrade flow
   - "Subscribe" or "Upgrade" button → POST /subscriptions/subscriptions with
     the selected plan_id and authenticated customer id.
   - Handle BillSphere's payment confirmation step: after subscription creation,
     poll or listen for payment status (GET /payments/payments/) until it moves
     from pending → successful, and only then mark the plan as active client-side.
   - On success: show a confirmation screen, refresh the user's session/plan
     entitlements, and unlock premium UI (ad-free player, download button,
     high-bitrate toggle, family member invites — scale unlocked features to
     the tier purchased).
   - On failure/decline: show a clear retry path and surface BillSphere's
     failure reason if provided.
   - Handle mid-cycle upgrades/downgrades (e.g. Individual → Family) by calling
     the subscription update endpoint and reflecting BillSphere's proration
     result, not a locally computed price.

4. Feature gating
   - Centralize entitlement checks in a single hook/service (e.g.
     `useSubscriptionStatus()` or `SubscriptionGate` component) that reads the
     current subscription state from BillSphere (cache it, refresh on app
     load and after purchase) and exposes booleans like `isPremium`,
     `isFamilyPlan`, `hasAdFreePlayback`, `canDownloadOffline`.
   - Gate playback features, download buttons, and family-member management
     screens behind this single source of truth. Do not duplicate plan logic
     in multiple components.

5. Billing/account pages
   - "Manage Subscription" page pulls from GET /subscriptions/subscriptions
     (current plan, renewal date, status) and GET /invoices/invoices +
     GET /payments/payments/ for billing history.
   - Cancel flow calls the subscription cancel endpoint and updates UI state
     to reflect `cancelled` / graceful downgrade-at-period-end behavior if
     BillSphere supports it.

6. Error handling & edge cases
   - Handle BillSphere being unreachable (show a retryable error, don't crash
     playback for existing entitled users — cache last-known entitlement
     state for a grace period).
   - Handle `past_due` subscription status by showing a payment-update prompt
     without immediately revoking access (respect BillSphere's dunning/retry
     schedule).
   - Handle 401s by attempting token refresh once, then redirecting to login.

CONSTRAINTS
- No plan pricing, feature limits, or billing math hardcoded in this repo —
  always source from BillSphere.
- No payment card data handled/stored in this app.
- All BillSphere calls go through a single API client module
  (e.g. `src/services/billsphere.ts`) — no scattered fetch calls.
- Add TypeScript types for BillSphere's Plan, Subscription, Invoice, and
  Payment response shapes based on the schemas BillSphere returns.

DELIVERABLES
- `src/services/billsphere.ts` (or equivalent) — typed API client with
  auth, plans, subscriptions, invoices, payments methods + token refresh.
- Pricing/Plans page wired to live data.
- Purchase/upgrade flow with payment-confirmation polling.
- `useSubscriptionStatus` hook (or app-appropriate equivalent) for gating.
- Manage Subscription / Billing History page.
- Basic tests for the API client and the gating logic.

Ask me for the exact BillSphere response schemas (from /docs Swagger) if you
need field-level detail before implementing the TypeScript types.
```

---

## 2. Master Prompt — E-learning Platform

```
ROLE: You are integrating this e-learning web app with BillSphere, an external
billing/subscription platform (FastAPI backend, REST API, JWT auth). BillSphere
already exists and is running — you are only building the CLIENT-SIDE
integration in THIS repo, plus any small backend proxy endpoints this app needs.

GOAL
Let a logged-in learner browse course-access tiers (e.g. Basic, Standard,
Premium — mapping to limited/full course catalog access, certificates,
mentor sessions, download limits) via BillSphere, purchase/upgrade a plan,
and have this app's own access control (which courses/certificates/features
a learner can use) driven by the subscription status returned by
BillSphere — not by local state.

BILLSPHERE CONNECTION DETAILS
- Base URL: <<BILLSPHERE_API_BASE_URL>>
- Platform tag to filter plans by: "elearning" (or <<YOUR_PLATFORM_TAG>>)
- Auth: JWT bearer tokens from BillSphere's /auth endpoints

WHAT TO BUILD

1. Account linking / auth bridge
   - If this app has its own learner accounts, add a step during signup/first
     enrollment attempt that creates a matching BillSphere customer via
     POST /auth/register (or logs in an existing one via POST /auth/login),
     and securely stores the returned JWT (httpOnly cookie or secure server-
     side session — never localStorage for the token).
   - Add token refresh via POST /auth/refresh so long study sessions don't
     get interrupted.
   - If this app does NOT have its own auth yet, use BillSphere as the auth
     provider directly.

2. Plans / Pricing page
   - Fetch live plans from GET /plans/plans?platform=elearning (or equivalent
     query param BillSphere exposes) — render tier name, price, billing
     cycle, trial period, and entitlements (course-catalog access level,
     certificate eligibility, number of mentor sessions, download limits)
     dynamically. Do not hardcode plan copy or limits in this repo.
   - Show the learner's current plan/status using
     GET /subscriptions/subscriptions.

3. Purchase / upgrade flow
   - "Enroll" / "Upgrade Plan" button → POST /subscriptions/subscriptions
     with selected plan_id and authenticated customer id.
   - Support trial periods if the plan has one — reflect BillSphere's
     `trialing` status in the UI (e.g. "Free for 7 days, then ₹1,499/mo").
   - After creating the subscription, poll/track payment status via
     GET /payments/payments/ until successful before unlocking paid course
     content, to stay consistent with BillSphere's
     "payment verified → subscription activated → invoice generated" flow.
   - On success: unlock the relevant course catalog tier, show confirmation,
     and refresh entitlements app-wide.
   - On failure: show retry path with BillSphere's failure reason if given.
   - Support mid-cycle plan changes (e.g. Basic → Premium mid-course) via
     the subscription update endpoint, reflecting BillSphere's proration
     result rather than computing prices locally.

4. Access control / content gating
   - Centralize entitlement checks in one service/hook (e.g.
     `useLearnerEntitlements()`) fed by BillSphere's subscription + plan
     data, exposing things like `catalogTier`, `canIssueCertificate`,
     `mentorSessionsRemaining`, `canDownloadOffline`.
   - Gate course enrollment, certificate generation, and mentor-booking
     features behind this single source of truth so access rules live in
     one place, not scattered per page/component.
   - Handle downgrade scenarios gracefully (e.g. learner mid-course when
     plan lapses — decide and implement a clear "grandfathered until X" or
     "locked until renewed" policy and surface it clearly in the UI).

5. Billing/account pages
   - "My Subscription" page shows current plan, renewal date, and status
     from GET /subscriptions/subscriptions.
   - Billing history page pulls GET /invoices/invoices and
     GET /payments/payments/ (include a link/download for PDF invoices,
     since BillSphere generates these via ReportLab).
   - Cancel flow calls the cancel endpoint and reflects resulting status
     (e.g. access continues until period end, per BillSphere's cancellation
     semantics).

6. Error handling & edge cases
   - Handle BillSphere being unreachable without locking out learners who
     already have verified entitlements (short local cache with grace
     period, clear "reconnecting to billing" state instead of hard failure).
   - Handle `past_due` status with a non-blocking payment-update banner,
     respecting BillSphere's retry/dunning schedule (Day 1 / Day 3 / Day 7)
     rather than instantly revoking course access.
   - Handle 401s with one token-refresh attempt, then redirect to login.

CONSTRAINTS
- No plan pricing, entitlement limits, or billing math hardcoded here —
  always source from BillSphere.
- No payment card data handled/stored in this app.
- All BillSphere calls go through a single API client module
  (e.g. `src/services/billsphere.ts`) — no scattered fetch calls.
- Add types for BillSphere's Plan, Subscription, Invoice, and Payment
  response shapes based on the schemas BillSphere returns.

DELIVERABLES
- `src/services/billsphere.ts` (or equivalent) — typed API client with
  auth, plans, subscriptions, invoices, payments methods + token refresh.
- Pricing/Plans page wired to live BillSphere data.
- Enrollment/upgrade flow with payment-confirmation tracking and trial
  handling.
- `useLearnerEntitlements` hook (or app-appropriate equivalent) for gating
  courses/certificates/mentor sessions.
- My Subscription / Billing History page with invoice download links.
- Basic tests for the API client and the gating logic.

Ask me for the exact BillSphere response schemas (from /docs Swagger) if you
need field-level detail before implementing the types.
```

---

## Notes before you run these

- Check `http://127.0.0.1:8000/docs` on the running BillSphere instance and copy the exact response shapes for `Plan`, `Subscription`, `Invoice`, and `Payment` — paste them into the Copilot conversation before it writes the TypeScript client, so the types aren't guessed.
- Confirm with your mentor whether each client app should have **its own login** (and just link to a BillSphere customer behind the scenes) or whether BillSphere **is** the login system for both apps. That decision changes step 1 in both prompts above — the prompts currently support either path but Copilot will need you to pick one explicitly.
- Decide the `platform` tag values ("spotify", "elearning", or whatever you actually seed in BillSphere's plan seeder) and make sure they match exactly what `python -m app.scripts.seed_plans` creates.
- If BillSphere doesn't yet expose a `platform` query filter on `/plans/plans`, that's a small addition to make on the BillSphere side first — flag it to Copilot in that repo separately.
