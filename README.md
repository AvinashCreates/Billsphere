# Billing Platform

A full-stack Billing Platform built using **FastAPI**, **PostgreSQL**, **SQLAlchemy**, and **Streamlit**. The platform provides secure authentication, role-based authorization, customer management, and is being extended with Plans and Subscription Management.

---

## Project Overview

The Billing Platform is designed to manage users, customers, billing operations, and subscription plans.

Current Features:

- User Registration
- User Login
- JWT Authentication
- Role-Based Authorization (Admin/User)
- Admin Dashboard
- User Dashboard
- Customer API
- Profile Page
- Streamlit Frontend
- FastAPI Backend
- PostgreSQL Database

Upcoming Features:

- Plans Management
- Subscription Management
- Billing & Invoice Generation
- Reports & Analytics
- Email Notifications
- Dashboard Charts

---

## Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT Authentication
- Passlib (Password Hashing)
- Uvicorn

### Frontend

- Streamlit

### Database

- PostgreSQL

### Version Control

- Git
- GitHub

---

## Project Structure

```
billing-platform/

│
├── app/
│   ├── api/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── repositories/
│   ├── utils/
│   ├── database.py
│   └── main.py
│
├── frontend/
│   ├── pages/
│   ├── app.py
│   ├── auth.py
│   ├── config.py
│   └── utils.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Authentication

The application uses JWT (JSON Web Tokens).

Workflow:

```
Register
      │
      ▼
Login
      │
      ▼
Generate JWT Token
      │
      ▼
Store Token
      │
      ▼
Access Protected APIs
```

---

## Authorization

Two user roles are currently supported.

### Admin

- Login
- View Dashboard
- Manage Customers
- Manage Plans (Upcoming)
- Manage Subscriptions (Upcoming)

### User

- Login
- View Dashboard
- View Plans (Upcoming)
- Subscribe to Plans (Upcoming)
- Manage Profile

---

## Current API Endpoints

### Authentication

```
POST /auth/register

POST /auth/login
```

### User

```
GET /users/me
```

### Customers

```
GET /customers
```

---

## Planned APIs

### Plans

```
GET /plans

GET /plans/{id}

POST /plans

PUT /plans/{id}

DELETE /plans/{id}
```

### Subscriptions

```
POST /subscriptions

GET /subscriptions/me

DELETE /subscriptions/{id}
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/sarada-02092004/billing-platform.git
```

Move into project

```bash
cd billing-platform
```

Create virtual environment

```bash
python -m venv venv
```

Activate virtual environment

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Running Backend

```bash
uvicorn app.main:app --reload
```

Backend URL

```
http://127.0.0.1:8000
```

Swagger Documentation

```
http://127.0.0.1:8000/docs
```

---

## Running Frontend

```bash
streamlit run frontend/app.py
```

or

```bash
python -m streamlit run frontend/app.py
```

Frontend URL

```
http://localhost:8501
```

---

## Git Workflow

Every team member works on their own branch.

Example

```
feature/plans

feature/subscriptions

feature/customers

feature/frontend

feature/testing
```

Daily Workflow

```
git checkout main

git pull origin main

git checkout feature/<branch-name>
```

After completing work

```
git add .

git commit -m "Meaningful commit message"

git push origin feature/<branch-name>
```

Create a Pull Request before merging into `main`.

---

## Team Responsibilities

| Member | Module |
|----------|---------|
| Member 1 | Authentication & Plans |
| Member 2 | Customers |
| Member 3 | Subscriptions |
| Member 4 | Frontend |
| Member 5 | Database, Testing & Documentation |

---

## Future Enhancements

- Plans Management
- Subscription Module
- Billing System
- Invoice Generation
- Reports
- Revenue Dashboard
- Email Notifications
- Charts & Analytics
- Deployment

---

## Contributors

- Sarada Prasad Sahoo
- Team Members

---

## License

This project is developed for learning and internship purposes.
