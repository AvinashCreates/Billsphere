# BillSphere Contribution and Operations Runbook

This document records the complete local workflow for running and exercising the BillSphere platform.
It covers the React frontend, FastAPI backend, PostgreSQL, Redis, Celery worker, Celery Beat, Docker Compose,
Alembic migrations, seed data, Swagger, API actions, tests, and the move from SQLite test storage to PostgreSQL.

## 1. Project Layout

```text
INFY/
  backend/       FastAPI application, SQLAlchemy models, Alembic, Celery tasks, tests
  frontend/      React + TypeScript + Vite customer and admin interface
  README.md      Project overview
  my_contriution.md  This runbook
```

The normal production-like local stack is:

```text
React/Vite :5173
FastAPI    :8000
PostgreSQL :5432
Redis      :6379
Celery     -> Redis broker/backend
Celery Beat -> Redis broker/backend
```

## 2. Prerequisites on Windows

Install these tools:

- Python 3.11 or newer
- Node.js 20 or newer and npm
- PostgreSQL 15 or newer, if running PostgreSQL natively
- Docker Desktop, if using Docker Compose
- Git

Check versions in PowerShell:

```powershell
python --version
py --version
node --version
npm --version
docker --version
docker compose version
psql --version
```

Docker commands require Docker Desktop to be open and its Linux engine to be running. If Docker reports that
`dockerDesktopLinuxEngine` cannot be found, open Docker Desktop and wait until it says it is running.

## 3. Environment Files

### Backend

Copy the backend example file:

```powershell
Set-Location C:\Users\pc\Desktop\INfY\INFY\backend
Copy-Item .env.example .env
```

Use these local PostgreSQL and Redis values in `backend/.env`:

```dotenv
ENVIRONMENT=development
DEBUG=true
HOST=127.0.0.1
PORT=8000
API_V1_PREFIX=/api/v1

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=billsphere
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/billsphere

REDIS_URL=redis://localhost:6379/0
SECRET_KEY=replace-this-with-a-long-random-development-secret
```

Use the actual PostgreSQL password if it is not `postgres`. Do not commit `backend/.env`.

PowerShell environment variables override values loaded from `.env`. If this terminal was previously used for SQLite
tests, clear the temporary override before starting the real application:

```powershell
Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:REDIS_URL -ErrorAction SilentlyContinue
```

Open a new terminal after changing `.env` when in doubt.

### Frontend

The frontend files already use the API variable. Create or verify `frontend/.env.local`:

```powershell
Set-Location C:\Users\pc\Desktop\INfY\INFY\frontend
Set-Content .env.local 'VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1'
```

The committed template is `frontend/.env.example`:

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

Restart Vite after changing an environment file.

## 4. Option A: Run PostgreSQL and Redis with Docker

This is the recommended local path because it avoids native service configuration.

From the backend directory:

```powershell
Set-Location C:\Users\pc\Desktop\INfY\INFY\backend
docker compose up -d db redis
docker compose ps
```

Expected services are `db` and `redis` with running status.

Check PostgreSQL:

```powershell
docker compose exec db pg_isready -U postgres -d billsphere
```

Check Redis:

```powershell
docker compose exec redis redis-cli ping
```

Expected Redis output:

```text
PONG
```

Stop only the dependencies:

```powershell
docker compose stop db redis
```

Remove containers but keep the database volume:

```powershell
docker compose down
```

Remove containers and all Docker database data. This is destructive:

```powershell
docker compose down -v
```

## 5. Option B: Run PostgreSQL and Redis Natively

Start the PostgreSQL Windows service from an Administrator PowerShell if needed:

```powershell
Get-Service *postgres*
Start-Service postgresql-x64-16
```

The service name can differ by installed version. Use the name returned by `Get-Service`.

Create the database using `psql`:

```powershell
psql -U postgres -h localhost -p 5432 -c "CREATE DATABASE billsphere;"
```

If the database already exists, PostgreSQL reports that it already exists; that is harmless.

Verify the connection:

```powershell
psql -U postgres -h localhost -p 5432 -d billsphere -c "SELECT current_database(), current_user;"
```

Redis must listen on port 6379. Verify it with:

```powershell
redis-cli -h localhost -p 6379 ping
```

If Redis is not installed natively, use Docker only for Redis:

```powershell
docker run --name billsphere-redis -p 6379:6379 -d redis:7-alpine
docker exec billsphere-redis redis-cli ping
```

## 6. Install and Prepare the Backend

Create a virtual environment once:

```powershell
Set-Location C:\Users\pc\Desktop\INfY\INFY\backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation for the current user, run this once in a normal PowerShell window:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Activate again afterward:

```powershell
.\.venv\Scripts\Activate.ps1
```

Confirm that the application sees PostgreSQL:

```powershell
python -c "from app.core.config import settings; print(settings.DATABASE_URL)"
```

## 7. Move from SQLite Tests to PostgreSQL

The test suite intentionally uses an in-memory SQLite database through `backend/tests/conftest.py`. This keeps tests
fast and independent from external services. It is not the application database.

To run the real application on PostgreSQL:

1. Start PostgreSQL and Redis.
2. Set `DATABASE_URL` in `backend/.env` to the PostgreSQL URL.
3. Apply migrations.
4. Start FastAPI.
5. Seed plans.
6. Start Celery and the frontend.

Example PostgreSQL URL:

```dotenv
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/billsphere
```

Do not use `sqlite:///./test_billsphere.db` in `backend/.env` for normal application work. That URL is only used by tests.

Apply the schema:

```powershell
Set-Location C:\Users\pc\Desktop\INfY\INFY\backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
```

If a development database is completely empty and migrations are unavailable, the application startup can create missing
tables, but `alembic upgrade head` is the correct repeatable workflow.

Inspect the current migration:

```powershell
alembic current
alembic history
```

Create a migration after a model change:

```powershell
alembic revision --autogenerate -m "describe the schema change"
alembic upgrade head
```

Never point a shared or production database at a test SQLite file.

## 8. Seed E-learning Plans

After migrations, seed the plan catalog:

```powershell
Set-Location C:\Users\pc\Desktop\INfY\INFY\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.seed_plans
```

The e-learning frontend requests plans with `platform=elearning`. Confirm that seeded records use exactly the lowercase
platform value `elearning`:

```powershell
python -c "from app.core.database import SessionLocal; from app.models.plan import Plan; db=SessionLocal(); print([(p.id, p.platform, p.name, p.billing_cycle) for p in db.query(Plan).filter(Plan.platform == 'elearning').all()]); db.close()"
```

The e-learning plan `feature_entitlements` object should use keys that the frontend understands, for example:

```json
{
  "catalog_tier": "premium",
  "can_issue_certificate": true,
  "mentor_sessions": 4,
  "can_download_offline": true
}
```

Prices, plan names, trial days, and limits are loaded from BillSphere. They are not hardcoded in the learner page.

## 9. Start the Backend API

Open Terminal 1:

```powershell
Set-Location C:\Users\pc\Desktop\INfY\INFY\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Verify the API:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/docs -UseBasicParsing
```

Open these URLs in a browser:

```text
Swagger UI: http://127.0.0.1:8000/docs
ReDoc:      http://127.0.0.1:8000/redoc
OpenAPI:    http://127.0.0.1:8000/openapi.json
```

## 10. Start Celery Worker and Celery Beat

Celery uses Redis for its broker and result backend. Start the worker in Terminal 2:

```powershell
Set-Location C:\Users\pc\Desktop\INfY\INFY\backend
.\.venv\Scripts\Activate.ps1
celery -A app.workers.celery_app worker --loglevel=info --pool=solo
```

`--pool=solo` is the reliable Windows development option.

Start Beat in Terminal 3:

```powershell
Set-Location C:\Users\pc\Desktop\INfY\INFY\backend
.\.venv\Scripts\Activate.ps1
celery -A app.workers.celery_app beat --loglevel=info
```

Celery Beat schedules recurring billing work, including subscription renewal checks and payment retry checks. Keep only
one Beat process for a given environment so tasks are not scheduled twice.

Check Redis keys while Celery is running:

```powershell
docker compose exec redis redis-cli keys "*"
```

If Redis is native, use:

```powershell
redis-cli keys "*"
```

## 11. Start the Frontend

Open Terminal 4:

```powershell
Set-Location C:\Users\pc\Desktop\INfY\INFY\frontend
npm install
npm run dev -- --host 127.0.0.1
```

Open:

```text
http://127.0.0.1:5173/
```

The e-learning customer surface is:

```text
http://127.0.0.1:5173/customer/learning
```

The frontend expects the backend at:

```text
http://127.0.0.1:8000/api/v1
```

## 12. Full Docker Compose Run

Docker Compose can run PostgreSQL, Redis, API, Celery worker, and Celery Beat together:

```powershell
Set-Location C:\Users\pc\Desktop\INfY\INFY\backend
docker compose up -d --build
docker compose ps
docker compose logs -f backend
```

In a second terminal, inspect workers:

```powershell
Set-Location C:\Users\pc\Desktop\INfY\INFY\backend
docker compose logs -f celery_worker
```

In a third terminal, inspect Beat:

```powershell
docker compose logs -f celery_beat
```

The current Compose file runs the backend and workers, but the Vite frontend is run separately from `frontend/`.

Stop the full backend stack:

```powershell
docker compose down
```

## 13. Complete Platform Actions

### Authentication

Current API routes are mounted below `/api/v1`:

```text
POST /api/v1/register
POST /api/v1/login
GET  /api/v1/me
POST /api/v1/refresh
POST /api/v1/forgot-password
POST /api/v1/reset-password
```

Use the current registration shape:

```json
{
  "first_name": "Learner",
  "last_name": "Example",
  "email": "learner@example.com",
  "phone": "9999999999",
  "password": "password123",
  "role": "customer"
}
```

Login returns an access token and refresh token. Send the access token on protected routes:

```text
Authorization: Bearer ACCESS_TOKEN
```

### Plans

```text
POST   /api/v1/plans
GET    /api/v1/plans
GET    /api/v1/plans/{plan_id}
PUT    /api/v1/plans/{plan_id}
DELETE /api/v1/plans/{plan_id}
```

For the e-learning client, use:

```text
GET /api/v1/plans?platform=elearning&page=1&page_size=100
```

Plan creation requires `platform`, `name`, `price`, and `billing_cycle`. Optional fields include currency, trial days,
feature entitlements, and usage limits.

### Customers

```text
POST   /api/v1/customers
GET    /api/v1/customers
GET    /api/v1/customers/{customer_id}
PUT    /api/v1/customers/{customer_id}
DELETE /api/v1/customers/{customer_id}
```

A customer payload requires `company_name`, `contact_name`, and `email`.

### Subscriptions

```text
POST /api/v1/subscriptions
GET  /api/v1/subscriptions
GET  /api/v1/subscriptions/me
GET  /api/v1/subscriptions/{subscription_id}
PUT  /api/v1/subscriptions/{subscription_id}
POST /api/v1/subscriptions/{id}/activate
POST /api/v1/subscriptions/{id}/cancel
PUT  /api/v1/subscriptions/{id}/cancel
POST /api/v1/subscriptions/{id}/cancel-at-period-end
POST /api/v1/subscriptions/{id}/pause
POST /api/v1/subscriptions/{id}/resume
POST /api/v1/subscriptions/{id}/change-plan
GET  /api/v1/subscriptions/{id}/history
```

The frontend checkout endpoint is preferred for a normal customer purchase because it creates and links the payment,
invoice, and subscription:

```text
POST /api/v1/payments/checkout
```

### Invoices

```text
POST /api/v1/invoices
GET  /api/v1/invoices
GET  /api/v1/invoices/{invoice_id}
GET  /api/v1/invoices/{invoice_id}/line-items
GET  /api/v1/invoices/{invoice_id}/pdf
PUT  /api/v1/invoices/{invoice_id}
DELETE /api/v1/invoices/{invoice_id}
```

### Payments

```text
POST /api/v1/payments
GET  /api/v1/payments
GET  /api/v1/payments/{payment_id}
PUT  /api/v1/payments/{payment_id}
POST /api/v1/payments/{id}/success?transaction_id=TXN-123
POST /api/v1/payments/{id}/failed
POST /api/v1/payments/{id}/refund
POST /api/v1/payments/checkout
GET  /api/v1/payments/confirmation?token=TOKEN
POST /api/v1/payments/confirmation
```

Checkout accepts the current mock methods:

```json
{
  "plan_id": 1,
  "payment_method": "mock_success"
}
```

Use `mock_failure` to exercise the failed-payment path. Do not send or store real card data in this application.

### Usage, retries, reports, and notifications

```text
POST /api/v1/usage
GET  /api/v1/usage/subscription/{subscription_id}
GET  /api/v1/payment-retries
GET  /api/v1/analytics/...
GET  /api/v1/reports/...
GET  /api/v1/notifications/...
GET  /api/v1/audit-logs/...
```

Exact parameters and response schemas are available in Swagger.

## 14. E-learning User Journey

1. Open the frontend and register or log in.
2. Open `/customer/learning`.
3. The page fetches only active `elearning` plans from BillSphere.
4. Select a plan and start checkout.
5. BillSphere creates the payment, invoice, and subscription.
6. The client polls the payment status.
7. The client refreshes subscription and plan data only after payment success.
8. `useLearnerEntitlements()` exposes catalog tier, certificate access, mentor sessions, and offline access.
9. Download invoice PDFs from the billing history section.
10. Test a declined payment with the backend/API `mock_failure` payment method.
11. Test `past_due` and retry behavior with Celery worker and Beat running.
12. Test plan changes and cancellation in the existing subscription pages or Swagger.

## 15. API Smoke Tests with PowerShell

Check service availability:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/docs -UseBasicParsing
Invoke-WebRequest http://127.0.0.1:5173/customer/learning -UseBasicParsing
```

Register a customer:

```powershell
$body = @{
  first_name = "Learner"
  last_name = "Example"
  email = "learner-$([guid]::NewGuid())@example.com"
  password = "password123"
  role = "customer"
} | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8000/api/v1/register -Method Post -ContentType "application/json" -Body $body
```

Login:

```powershell
$loginBody = @{ email = "learner@example.com"; password = "password123" } | ConvertTo-Json
$login = Invoke-RestMethod http://127.0.0.1:8000/api/v1/login -Method Post -ContentType "application/json" -Body $loginBody
$headers = @{ Authorization = "Bearer $($login.access_token)" }
```

List e-learning plans:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/plans?platform=elearning&page=1&page_size=100" -Headers $headers
```

The exact plan ID depends on the seed data. Use the returned ID for checkout:

```powershell
$checkout = @{ plan_id = 1; payment_method = "mock_success" } | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8000/api/v1/payments/checkout -Method Post -Headers $headers -ContentType "application/json" -Body $checkout
```

List the authenticated learner's subscriptions, invoices, and payments:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/subscriptions/me -Headers $headers
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/invoices?page=1&page_size=100" -Headers $headers
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/payments?page=1&page_size=100" -Headers $headers
```

## 16. Test and Quality Commands

### Backend tests

The test fixture uses isolated in-memory SQLite and does not require PostgreSQL or Redis:

```powershell
Set-Location C:\Users\pc\Desktop\INfY\INFY\backend
.\.venv\Scripts\Activate.ps1
python -m pytest -q
```

Expected current result:

```text
87 passed
```

### Frontend checks

```powershell
Set-Location C:\Users\pc\Desktop\INfY\INFY\frontend
npm run lint
npm run build
```

Both commands must finish with exit code 0. The production build may print a non-failing large JavaScript chunk warning.

### Full verification order

```powershell
Set-Location C:\Users\pc\Desktop\INfY\INFY\backend
.\.venv\Scripts\Activate.ps1
python -m pytest -q
Set-Location ..\frontend
npm run lint
npm run build
```

## 17. Troubleshooting

### Port 8000 is busy

```powershell
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
```

Stop the owning process only when you recognize it:

```powershell
Stop-Process -Id PROCESS_ID
```

### Port 5173 is busy

Start Vite on another port:

```powershell
npm run dev -- --host 127.0.0.1 --port 5174
```

### PostgreSQL password authentication failed

Check the password in `backend/.env`, then verify it directly:

```powershell
psql -U postgres -h localhost -p 5432 -d billsphere -c "SELECT 1;"
```

If using Docker, do not mix a native PostgreSQL server and Docker PostgreSQL on the same port. Stop one of them or
change the published port and update `DATABASE_URL`.

### Docker engine unavailable

Open Docker Desktop and wait for the Linux engine to become ready. Then retry:

```powershell
docker info
docker compose up -d db redis
```

### Redis connection refused

```powershell
docker compose ps redis
docker compose logs redis
```

Then check:

```powershell
docker compose exec redis redis-cli ping
```

### Celery cannot import the application

Run the command from `backend/` with the backend virtual environment active:

```powershell
celery -A app.workers.celery_app worker --loglevel=info --pool=solo
```

### Frontend shows an empty learner plan list

Confirm all of the following:

- FastAPI is running on port 8000.
- The browser is using `VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1`.
- The user is authenticated.
- Plans are seeded with `platform=elearning`.
- The browser console has no CORS or 401 error.
- The API responds to `/api/v1/plans?platform=elearning`.

## 18. Safe Shutdown

Stop the frontend with `Ctrl+C` in its terminal.

Stop FastAPI, Celery worker, and Beat with `Ctrl+C` in their terminals.

Stop Docker services:

```powershell
Set-Location C:\Users\pc\Desktop\INfY\INFY\backend
docker compose down
```

Keep the PostgreSQL volume for the next run. Use `docker compose down -v` only when you intentionally want to
remove all local database data.
