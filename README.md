# Billing Platform

A full-stack Billing Platform built using FastAPI, PostgreSQL, SQLAlchemy, JWT Authentication, and Streamlit.

---

# Tech Stack

## Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT Authentication
- Pydantic

## Frontend

- Streamlit

---

# Features

## Authentication

- User Login
- JWT Authentication
- Role Based Authorization

---

## Customer Module ✅

### Admin

- Create Customer
- View Customers
- Update Customer
- Delete Customer

### Customer

- View Profile

---

## Plans Module ✅

### Admin

- View All Plans
- View Plan Details
- Create New Plan
- Update Existing Plan
- Deactivate Plan

### Customer

- View Active Plans
- View Plan Details

---

## Subscription Module ✅

### Customer

- Subscribe to an active plan
- View current subscription (plan, status, start date, renewal/end date)
- Cancel subscription
- Renew an expired/cancelled subscription

---

## Invoice Module ✅

### Customer

- Invoices are generated **automatically** on subscribe/renew — no manual step required
- View list of own invoices (paginated, filterable by status/payment status)
- View full invoice detail — billing period, plan fee, proration, taxes, usage charges, line items

### Admin

- View all invoices
- View invoice detail
- Mark invoice as paid

---

## Upcoming Modules

- Payment Module (gateway integration)
- Billing usage/metering
- Email notifications on invoice generation

---

# Folder Structure

```
billing-platform/

app/
│
├── api/            (route handlers — auth, customers, plans, subscriptions, invoices)
├── database/
├── dependencies/   (auth guards: get_current_user, require_admin)
├── models/
├── repositories/   (raw DB queries)
├── schemas/        (Pydantic request/response models)
├── services/        (business logic)

frontend/
│
├── pages/
│   ├── Login.py
│   ├── Register.py
│   ├── Profile.py
│   ├── AdminDashboard.py
│   ├── Admin.py
│   ├── Customers.py             (admin)
│   ├── CustomerDashboard.py     (customer)
│   ├── Plans.py                 (admin + customer, subscribe action)
│   ├── Subscriptions.py         (customer — My Subscription)
│   ├── Invoices.py              (admin)
│   ├── MyInvoices.py            (customer — My Invoices)
│   ├── utils.py
│   ├── config.py
│   ├── auth.py
│   └── styles.py

README.md
requirements.txt
```

---

# Installation

Clone Repository

```bash
git clone <repository_url>
```

Move inside project

```bash
cd billing-platform
```

Create Virtual Environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```

Install Requirements

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file.

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/billing_platform

SECRET_KEY=your_secret_key

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

# Run Backend

```
uvicorn app.main:app --reload
```

Interactive API docs available at `http://127.0.0.1:8000/docs`.

---

# Run Frontend

```
cd frontend
streamlit run app.py
```

---

# API Endpoints

## Authentication

- POST /auth/login

---

## Customers

- GET /customers
- GET /customers/{id}
- POST /customers
- PUT /customers/{id}
- DELETE /customers/{id}

---

## Plans

### Admin

- GET /plans
- GET /plans/{id}
- POST /plans
- PUT /plans/{id}
- DELETE /plans/{id}

### Customer

- GET /plans
- GET /plans/{id}

---

## Subscriptions

### Customer

- POST /subscriptions/ — subscribe to a plan (auto-generates first invoice)
- GET /subscriptions/my — view own current subscription
- POST /subscriptions/{id}/cancel
- POST /subscriptions/{id}/renew — auto-generates a new invoice

### Admin

- GET /subscriptions/{id}
- GET /subscriptions/ — view all subscriptions

---

## Invoices

### Customer

- GET /invoices/my — paginated list of own invoices
- GET /invoices/my/{invoice_id} — own invoice detail (ownership-checked)

### Admin

- GET /invoices/ — paginated list, all customers
- GET /invoices/{invoice_id} — full detail
- POST /invoices/{invoice_id}/pay — mark as paid

---

# Project Status

| Module | Status |
|---------|--------|
| Authentication | ✅ Completed |
| Customer | ✅ Completed |
| Plans | ✅ Completed |
| Subscription | ✅ Completed |
| Invoice | ✅ Completed |
| Billing (usage/metering) | ⏳ Pending |
| Payment (gateway) | ⏳ Pending |

---

# Team Members

- Sarada Prasad Sahoo (Lead Developer)
- Sonal
- Manju
- Prameela
- Siddhi

---

# Git Workflow

Each team member works in their own feature branch. Work is merged into a shared `integration`
branch for combined testing before going to `main`.

```
main
│
├── integration                        (combined branch — all features merged here first)
│   ├── feature/subscription-backend
│   ├── feature/billing-frontend
│   ├── feature/dashboard-ui-frontend
│   ├── feature/invoices-frontend
│   └── feature/plan-module
```

Workflow:

```
git checkout main
git pull origin main
git checkout -b feature/<task>
git add .
git commit -m "Completed feature"
git push origin feature/<task>
```

To pick up the latest combined work from `integration`:

```
git fetch origin
git checkout -b integration origin/integration
```

(if you already have a local `integration` branch, use `git pull origin integration` instead)

Only the Team Lead merges approved changes from `integration` into `main`.

---

# Future Enhancements

- Payment Gateway integration
- Invoice PDF download
- Email notifications on subscribe/renew/invoice generation
- Analytics Dashboard
- Usage-based billing / metering
- Reports
