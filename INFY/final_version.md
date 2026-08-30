# BillSphere Final Commands

Run these commands from PowerShell.

## Clone and setup

```powershell
git clone <REPOSITORY_URL>
cd INFY

cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

cd ..\frontend
npm install
```

## Start services with Docker

```powershell
cd backend
docker compose up -d db redis
```

Native service checks:

```powershell
Get-Service *postgres*,*redis*
redis-cli -h localhost -p 6379 ping
psql -U postgres -h localhost -p 5432 -c "CREATE DATABASE billsphere;"
```

## Start the application

Terminal 1, backend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Terminal 2, Celery worker:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
celery -A app.workers.celery_app worker --loglevel=info --pool=solo
```

Terminal 3, Celery Beat:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
celery -A app.workers.celery_app beat --loglevel=info
```

Terminal 4, frontend:

```powershell
cd frontend
npm run dev -- --host 127.0.0.1
```

Open:

```text
http://127.0.0.1:5173
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc
```

## Database and tests

```powershell
cd backend
alembic upgrade head
pytest
pytest -v
```

## Check and stop services

```powershell
git status
Get-NetTCPConnection -LocalPort 8000,5173
docker compose ps
docker compose down
```

## GitHub workflow

```powershell
git remote -v
git branch
git checkout Sravanthi
git pull
git add .
git diff --cached
git commit -m "Update BillSphere billing features"
git push springboard Sravanthi
```

For another remote or branch:

```powershell
git push origin <BRANCH_NAME>
```

Never commit `.env` files, passwords, API keys, or JWT secrets.
