# Billsphere - Subscription & Billing Platform

Billsphere is a full-stack automated subscription, billing, and invoicing management platform built with a **FastAPI** backend and a **React + Vite + TypeScript** frontend.

---

## 📋 System Prerequisites

Before running the application, ensure you have the following installed on your machine:

- **Python 3.10+** (with `pip` and `venv`)
- **Node.js v18+** & **npm v9+**
- **Redis Server** (v6.0+) — Required as the message broker for Celery background tasks (email dispatch & scheduled subscription billing checks).

---

## ⚙️ Environment Configuration (`.env`)

Create a file named `.env` inside the `backend/` directory (`backend/.env`). You can use `backend/.env.example` as a template.

### `.env` File Template & Parameter Details

```ini
# ==========================================
# Database Configuration
# ==========================================
# SQLite Database (default for quick local dev)
DATABASE_URL=sqlite:///./billsphere.db

# PostgreSQL (Alternative for production/testing)
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=billing_platform
# DB_USER=postgres
# DB_PASSWORD=your_password

# ==========================================
# Security & JWT Token Configuration
# ==========================================
JWT_SECRET_KEY=your_generated_secure_jwt_secret_key_here
SECRET_KEY=your_generated_secure_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ==========================================
# Redis & Celery Worker Configuration
# ==========================================
# Connection URL for local Redis instance
REDIS_URL=redis://localhost:6379/0

# ==========================================
# SMTP Email Configuration
# ==========================================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
EMAIL_FROM=your_email@gmail.com
```

### 🔴 Mandatory Configuration Requirements

1. **Redis URL (`REDIS_URL`)**:
   - Must point to an active Redis instance. Default: `redis://localhost:6379/0`.
   - If Redis is not running, Celery workers and background email sending tasks will fail to connect.

2. **Mail Configuration (`SMTP_*`)**:
   - `SMTP_HOST`: `smtp.gmail.com` (or your custom SMTP host).
   - `SMTP_PORT`: `587` (TLS) or `465` (SSL).
   - `SMTP_USER`: Sender email address (e.g., `support.billsphere@gmail.com`).
   - `SMTP_PASSWORD`: **Gmail App Password** (16-character passcode).
     > 💡 **Note for Gmail Users**: You cannot use your regular Gmail password. You must enable 2-Step Verification on your Google Account and generate an **App Password** via [Google Account Security Settings](https://myaccount.google.com/apppasswords).
   - `EMAIL_FROM`: Display email address for sent invoice/welcome emails.

3. **Database URL (`DATABASE_URL`)**:
   - Defaults to SQLite (`sqlite:///./billsphere.db`). The database file will automatically be created on launch.

---

## 🚀 Running the Application Locally

### 1️⃣ Start Redis Server
Ensure Redis is running locally on port `6379`:
- **Windows (WSL / Native Redis service)**: `redis-server`
- **Docker**: `docker run -p 6379:6379 -d redis`
- **Mac**: `brew services start redis`

---

### 2️⃣ Backend Setup & Execution

Navigate into the `backend/` directory:

```bash
cd backend
```

#### A. Create and Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / Mac
python3 -m venv .venv
source .venv/bin/activate
```

#### B. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

#### C. Start FastAPI Backend Server
```bash
python -m uvicorn main:app --reload --port 8000
```
> The API server will run at: `http://localhost:8000`  
> Interactive API Docs (Swagger): `http://localhost:8000/docs`

#### D. Start Celery Worker (In a separate terminal tab/window)
```bash
# Windows
celery -A app.workers.celery_app worker --loglevel=info -P solo

# Linux / Mac
celery -A app.workers.celery_app worker --loglevel=info
```

#### E. Start Celery Beat Scheduler (In a separate terminal tab/window)
```bash
celery -A app.workers.celery_app beat --loglevel=info
```

---

### 3️⃣ Frontend Setup & Execution

Navigate into the `frontend/` directory:

```bash
cd frontend
```

#### A. Install Node Dependencies
```bash
npm install
```

#### B. Start Frontend Development Server
```bash
npm run dev
```
> The React Frontend will run at: `http://localhost:5173`

---

## 🐳 Docker Setup (Alternative)

You can run the entire stack (FastAPI, PostgreSQL, Redis, Celery Worker, Celery Beat) using Docker Compose:

```bash
docker-compose up --build
```

---

## 🛠️ Summary of Required Services

To run Billsphere smoothly without error, ensure the following processes are active:

| Service | Port / Details | Command |
| :--- | :--- | :--- |
| **Redis** | `6379` | `redis-server` / Docker |
| **FastAPI Backend** | `8000` | `uvicorn main:app --reload` |
| **Celery Worker** | Background Email Queue | `celery -A app.workers.celery_app worker --loglevel=info -P solo` |
| **Celery Beat** | Scheduled Billing Tasks | `celery -A app.workers.celery_app beat --loglevel=info` |
| **Vite Frontend** | `5173` | `npm run dev` |
