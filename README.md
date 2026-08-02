<<<<<<< HEAD
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

## Upcoming Modules

- Subscription Module
- Billing Module
- Invoice Module
- Payment Module

---

# Folder Structure

```
billing-platform/

backend/
│
├── app/
├── database/
├── routers/
├── models/
├── schemas/
├── services/

frontend/
│
├── pages/
├── utils.py
├── config.py

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

---

# Run Frontend

```
streamlit run app.py
```

---

# API Endpoints

## Authentication

- POST /login

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

# Project Status

| Module | Status |
|---------|--------|
| Authentication | ✅ Completed |
| Customer | ✅ Completed |
| Plans | ✅ Completed |
| Subscription | 🚧 In Progress |
| Billing | ⏳ Pending |
| Invoice | ⏳ Pending |
| Payment | ⏳ Pending |

---

# Team Members

- Sarada Prasad Sahoo (Lead Developer)
- Sonal
- Manju
- Prameela
- Siddhi

---

# Git Workflow

Each team member works in their own feature branch.

```
main
│
├── feature/subscription-backend
├── feature/subscription-frontend
├── feature/billing-frontend
├── feature/invoice-frontend
└── feature/dashboard-ui
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

Only the Team Lead merges approved changes into `main`.

---

# Future Enhancements

- Email Notifications
- Payment Gateway
- Invoice PDF Download
- Analytics Dashboard
- Reports
=======
# Recurring-Revenue--Subscription---Billing-Automation-Platform-July-2026
>>>>>>> 406fbd299848be5a819f9db59cd63ae6fcd3d2c0
