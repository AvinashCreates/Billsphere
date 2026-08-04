# ⚡ BillSphere - Subscription & Billing Management Platform

BillSphere is a full-stack automated subscription, billing, customer invoicing, and revenue operations platform built with **FastAPI** (Python), **React + Vite + TypeScript**, **Redis**, **Celery Workers & Beat Scheduler**, and **PostgreSQL / SQLite**.

---

## 📋 System Prerequisites

Ensure the following tools are installed on your environment before launching:

- **Python 3.10+** (with `pip` & `venv`)
- **Node.js v18+** & **npm v9+**
- **Redis Server** (v6.0+) — Message broker for Celery background tasks & beat schedulers.
- **Docker & Docker Compose** *(Optional for full containerized deployment)*

---

## ⚙️ Environment Configuration (`backend/.env`)

Create a file named `.env` inside the `backend/` directory (`backend/.env`). You can use `backend/.env.example` as a template.

### `.env` File Parameters

```ini
# ==========================================
# Database Configuration
# ==========================================
# SQLite Database (Default for local development)
DATABASE_URL=sqlite:///./billsphere.db

# PostgreSQL (Alternative for production/testing)
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=billing_platform
# DB_USER=postgres
# DB_PASSWORD=your_postgres_password

# ==========================================
# JWT Security & Authentication
# ==========================================
JWT_SECRET_KEY=your_generated_secure_jwt_secret_key_here
SECRET_KEY=your_generated_secure_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ==========================================
# Redis & Celery Message Broker
# ==========================================
REDIS_URL=redis://localhost:6379/0

# ==========================================
# SMTP Email Service Configuration
# ==========================================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
EMAIL_FROM=your_email@gmail.com

# ==========================================
# Frontend Application URL (for Email Links)
# ==========================================
FRONTEND_URL=http://localhost:5173
```

> 💡 **Gmail SMTP Setup Note**: You must enable **2-Step Verification** on your Google Account and generate an **App Password** via [Google Security Settings](https://myaccount.google.com/apppasswords). Use this 16-character passcode for `SMTP_PASSWORD`.

---

## 🚀 Step-by-Step Commands to Run the Project

To run BillSphere locally, open separate terminal windows for each service:

### 1️⃣ Terminal 1: Redis Server
Start the local Redis server instance on default port `6379`:

```bash
# Option A: Local Redis Service
redis-server

# Option B: Docker Container
docker run -p 6379:6379 -d redis:7-alpine
```

---

### 2️⃣ Terminal 2: FastAPI Backend Server
Navigate into the `backend/` directory, activate virtual environment, install dependencies, run migrations, and launch Uvicorn:

```bash
# Navigate to backend directory
cd backend

# Create & activate Python virtual environment
# On Windows:
python -m venv .venv
.venv\Scripts\activate

# On Linux / Mac:
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database table migrations
python migrate_plan_status.py

# Launch FastAPI Server
python -m uvicorn main:app --reload --port 8000
```
> 🌐 Backend API running at: `http://localhost:8000`  
> 📖 Swagger API Documentation: `http://localhost:8000/docs`

---

### 3️⃣ Terminal 3: Celery Worker (Email Queue Listener)
Launch Celery worker process to process asynchronous background tasks (Welcome emails, Invite links, Confirmation emails):

```bash
cd backend
.venv\Scripts\activate   # (or source .venv/bin/activate on Linux/Mac)

# On Windows:
celery -A app.workers.celery_app worker --loglevel=info -P solo

# On Linux / Mac:
celery -A app.workers.celery_app worker --loglevel=info
```

---

### 4️⃣ Terminal 4: Celery Beat (Scheduled Deadline Reminders)
Launch Celery Beat scheduler to automatically check for upcoming renewal deadlines daily:

```bash
cd backend
.venv\Scripts\activate   # (or source .venv/bin/activate on Linux/Mac)

celery -A app.workers.celery_app beat --loglevel=info
```

---

### 5️⃣ Terminal 5: Vite React Frontend
Navigate into `frontend/` directory, install node modules, and start the development server:

```bash
cd frontend

# Install node dependencies
npm install

# Start Vite React development server
npm run dev
```
> 🌐 Frontend application running at: `http://localhost:5173`

---

## 🐳 Running with Docker Compose (Alternative)

You can spin up the entire application stack (FastAPI Backend, Redis, Celery Worker, Celery Beat) in containerized mode with a single command:

```bash
docker-compose up --build
```

---

## 🛠️ Summary of Required Active Terminals

| Service | Terminal Location | Command | Listening Address / Details |
| :--- | :--- | :--- | :--- |
| **Redis** | Any | `redis-server` / `docker run -p 6379:6379 redis` | `localhost:6379` |
| **FastAPI Backend** | `backend/` | `python -m uvicorn main:app --reload` | `http://localhost:8000` |
| **Celery Worker** | `backend/` | `celery -A app.workers.celery_app worker --loglevel=info -P solo` | Task Queue Listener |
| **Celery Beat** | `backend/` | `celery -A app.workers.celery_app beat --loglevel=info` | Daily Renewal Cron |
| **React Frontend** | `frontend/` | `npm run dev` | `http://localhost:5173` |

---

## 📁 Project Structure

```
Billsphere/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI Endpoint Routers (auth, customers, plans, subscriptions, schedule)
│   │   ├── core/            # Security, JWT, Dependencies & HTML Email Templates
│   │   ├── database/        # Database session & engine setup
│   │   ├── models/          # SQLAlchemy Database Models (User, Customer, Plan, Subscription, AuditLog)
│   │   ├── schemas/         # Pydantic Request/Response Models
│   │   └── workers/         # Celery App Configuration & Email Background Tasks
│   ├── .env.example         # Template for Backend Environment Variables
│   ├── Dockerfile           # Backend Container Image Definition
│   ├── main.py              # Application Entrypoint & CORS Middleware
│   ├── migrate_plan_status.py # Database Migration Script
│   └── requirements.txt     # Python Package Dependencies
├── frontend/
│   ├── src/
│   │   ├── assets/          # API Service Layer (`api.ts`)
│   │   ├── components/      # Shared Reusable UI Components (DataTable, KpiCard, StatusBadge, Sidebar)
│   │   ├── contexts/        # React Contexts (`AuthContext`, `ThemeContext`)
│   │   ├── layouts/         # App Layout Shell (`DashboardLayout`)
│   │   ├── pages/           # Views (AdminDashboard, UserDashboard, Customers, Plans, Invoices, SetPassword)
│   │   └── style.css        # Central Design System Tokens & Tailwind CSS Configuration
│   └── package.json         # Node Dependencies & Scripts
├── docker-compose.yml       # Docker Multi-Container Orchestration Setup
└── README.md                # Comprehensive Documentation & Setup Guide
```
