# ⚡ BillSphere Backend

BillSphere is a SaaS Subscription & Billing Management Platform built with **FastAPI**, **Python**, **SQLAlchemy**, **PostgreSQL/SQLite**, **JWT Authentication**, **Redis**, and **Celery**.

This repository contains the backend API and billing engine for the BillSphere platform.

---

## 🚀 Backend Features

- JWT Authentication
- User Registration & Login
- Customer Management
- Subscription Plan Management
- Subscription Management
- Billing Cycle Management
- Invoice Management
- Payment Management
- Payment Retry Handling
- Subscription Lifecycle Management
- Trial Subscriptions
- Subscription Renewal
- Subscription Cancellation
- Tax Calculation Support
- Proration Support
- Notification & Email System
- Background Tasks with Celery
- Redis Message Broker
- Automated Billing Jobs
- FastAPI Swagger Documentation
- SQLAlchemy Database Models
- CORS Configuration

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Backend Language |
| FastAPI | REST API Framework |
| SQLAlchemy | ORM |
| PostgreSQL / SQLite | Database |
| Pydantic | Data Validation |
| JWT | Authentication |
| Redis | Message Broker |
| Celery | Background Tasks |
| Uvicorn | ASGI Server |
| ReportLab | PDF Generation |

---

# 📋 Prerequisites

Install the following before running the backend:

- Python 3.10+
- pip
- Git
- Redis
- PostgreSQL *(if using PostgreSQL instead of SQLite)*

Docker is recommended for running Redis.

---

# 📁 Backend Structure

```text
backend/
│
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── customers.py
│   │   ├── plans.py
│   │   ├── subscriptions.py
│   │   └── schedule.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── ...
│   │
│   ├── database/
│   │   └── ...
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── customer.py
│   │   ├── plan.py
│   │   ├── subscription.py
│   │   ├── invoice.py
│   │   ├── payment.py
│   │   └── ...
│   │
│   ├── schemas/
│   │   └── ...
│   │
│   ├── services/
│   │   └── ...
│   │
│   └── workers/
│       ├── tasks.py
│       └── ...
│
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md