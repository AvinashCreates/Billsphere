# BillSphere - Verification & Testing Guide

**Purpose**: Quick reference for testing all features  
**Date**: August 29, 2026

---

## 🚀 START THE APPLICATION

Run from PowerShell in `c:\Users\pc\Desktop\INfY\INFY`:

```powershell
# Terminal 1 - Backend API
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 - Frontend Dev Server  
cd frontend
npm run dev

# Terminal 3 - Celery Worker (optional, for async tasks)
cd backend
celery -A app.workers.celery_app worker --loglevel=info --pool=solo

# Terminal 4 - Celery Beat (optional, for scheduled tasks)
cd backend
celery -A app.workers.celery_app beat --loglevel=info
```

**Access Points**:
- Frontend: `http://localhost:5173`
- Backend API: `http://127.0.0.1:8000`
- API Docs: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## ✅ VERIFICATION TESTS

### Test 1: Dashboard Data Loading

**Expected**: Plans and customers show actual counts (not "0 records")

```bash
# 1. Go to http://localhost:5173/admin (or admin dashboard)
# 2. Watch loading animation (should show dual spinners + checklist)
# 3. Wait for page to load
# 4. Verify:
#    - Plans loaded: X plan records available (not 0)
#    - Customers loaded: X customer records available (not 0)
```

**If Still Showing "0 Records**:
```bash
# Check backend is running
curl http://127.0.0.1:8000/docs

# Test the endpoints directly
curl -H "Authorization: Bearer YOUR_JWT" \
  http://127.0.0.1:8000/api/v1/plans

curl -H "Authorization: Bearer YOUR_JWT" \
  http://127.0.0.1:8000/api/v1/customers
```

---

### Test 2: API Endpoints (All Paths Corrected)

```bash
# Set your JWT token
$JWT = "your_jwt_token_here"

# Test Plans Endpoint
curl -H "Authorization: Bearer $JWT" `
  http://127.0.0.1:8000/api/v1/plans
# Should return: { "total": X, "page": 1, "page_size": 10, "items": [...] }

# Test Customers Endpoint
curl -H "Authorization: Bearer $JWT" `
  http://127.0.0.1:8000/api/v1/customers
# Should return: { "total": X, "page": 1, "page_size": 10, "items": [...] }

# Test Subscriptions Endpoint
curl -H "Authorization: Bearer $JWT" `
  http://127.0.0.1:8000/api/v1/subscriptions
# Should return: { "total": X, "page": 1, "page_size": 10, "items": [...] }

# Test Invoices Endpoint
curl -H "Authorization: Bearer $JWT" `
  http://127.0.0.1:8000/api/v1/invoices
# Should return: { "total": X, "page": 1, "page_size": 10, "items": [...] }

# Test Payments Endpoint
curl -H "Authorization: Bearer $JWT" `
  http://127.0.0.1:8000/api/v1/payments
# Should return: { "total": X, "page": 1, "page_size": 10, "items": [...] }
```

---

### Test 3: Refunds Endpoints (NEW)

```bash
# List all refunds
curl -H "Authorization: Bearer $JWT" `
  http://127.0.0.1:8000/api/v1/refunds
# Should return: { "total": 0, "page": 1, "page_size": 10, "items": [] }

# Create a refund for payment ID 1
curl -X POST -H "Authorization: Bearer $JWT" `
  -H "Content-Type: application/json" `
  -d '{"amount": 100, "reason": "Customer requested"}' `
  "http://127.0.0.1:8000/api/v1/refunds?payment_id=1"
# Should return: { "id": X, "refund_status": "refunded", "message": "..." }

# Get specific refund details
curl -H "Authorization: Bearer $JWT" `
  http://127.0.0.1:8000/api/v1/refunds/1
# Should return: { "id": 1, "payment_id": 1, "refund_reason": "Customer requested", ... }
```

---

### Test 4: Audit Logging

```bash
# List all audit logs
curl -H "Authorization: Bearer $JWT" `
  http://127.0.0.1:8000/api/v1/audit-logs
# Should return: { "total": X, "page": 1, "page_size": 20, "items": [...] }

# Filter by entity type (payment)
curl -H "Authorization: Bearer $JWT" `
  "http://127.0.0.1:8000/api/v1/audit-logs?entity_type=payment"
# Should return: All payment-related audit logs

# Filter by entity ID
curl -H "Authorization: Bearer $JWT" `
  "http://127.0.0.1:8000/api/v1/audit-logs?entity_type=payment&entity_id=1"
# Should return: Audit logs for payment #1 only

# Filter by multiple parameters
curl -H "Authorization: Bearer $JWT" `
  "http://127.0.0.1:8000/api/v1/audit-logs?entity_type=subscription&page=1&page_size=50"
# Should return: Paginated subscription audit logs
```

---

### Test 5: Create Customer (Tests User-Customer Link)

```bash
# Create a new customer
$body = @{
    company_name = "Test Corp"
    contact_name = "John Doe"
    email = "john@testcorp.com"
    phone = "+1-555-1234"
} | ConvertTo-Json

curl -X POST `
  -H "Authorization: Bearer $JWT" `
  -H "Content-Type: application/json" `
  -d $body `
  http://127.0.0.1:8000/api/v1/customers

# Response should include:
# "id": X
# "owner_id": <current_user_id>  ⭐ This proves user-customer linking
# "company_name": "Test Corp"
# "email": "john@testcorp.com"
```

---

### Test 6: Create Subscription (Tests Full Billing Flow)

```bash
# First get customer ID from previous test
# First get plan ID from plans list

$body = @{
    customer_id = 1
    plan_id = 1
} | ConvertTo-Json

curl -X POST `
  -H "Authorization: Bearer $JWT" `
  -H "Content-Type: application/json" `
  -d $body `
  http://127.0.0.1:8000/api/v1/subscriptions

# Check audit log for subscription creation
curl -H "Authorization: Bearer $JWT" `
  "http://127.0.0.1:8000/api/v1/audit-logs?entity_type=subscription"

# Check email was sent (check backend logs or email service)
```

---

### Test 7: Create Payment (Tests Email Confirmation)

```bash
# First get invoice ID from invoices list
# Or create an invoice first

$body = @{
    invoice_id = 1
    amount = 5000
    payment_method = "card"
} | ConvertTo-Json

curl -X POST `
  -H "Authorization: Bearer $JWT" `
  -H "Content-Type: application/json" `
  -d $body `
  http://127.0.0.1:8000/api/v1/payments

# Check backend logs for email send attempt
# Check audit log for payment creation
```

---

### Test 8: Database State Verification

```bash
# Connect to PostgreSQL
psql -U postgres -h localhost -d billsphere

# Check customers are linked to users
SELECT c.id, c.company_name, c.owner_id, u.email
FROM customers c
JOIN users u ON c.owner_id = u.id;

# Check audit logs exist
SELECT id, actor_id, action, entity_type, timestamp
FROM audit_logs
ORDER BY timestamp DESC
LIMIT 10;

# Check refunds are tracked
SELECT p.id, p.refunded_amount, p.refund_reason, p.status
FROM payments p
WHERE p.refunded_amount > 0;

# Check subscriptions
SELECT id, customer_id, plan_id, status, start_date
FROM subscriptions;
```

---

## 🧪 AUTOMATED TEST SUITE

```bash
# Run all backend tests
cd backend
pytest -v

# Run specific test file
pytest tests/test_billing_flow.py -v

# Run with coverage
pytest --cov=app tests/ -v

# Run audit log tests
pytest tests/test_audit_logs.py -v

# Run payment tests
pytest tests/test_payments.py -v

# Run subscription tests
pytest tests/test_subscriptions.py -v
```

---

## 🔍 DEBUGGING TOOLS

### Check Backend Logs

```bash
# View real-time logs
Get-Content -Path "backend/logs/billsphere.log" -Tail 50 -Wait

# Search for specific actions
Select-String "PAYMENT_SUCCESS" "backend/logs/billsphere.log"

# Search for errors
Select-String "ERROR" "backend/logs/billsphere.log"
```

### Monitor API Requests

```bash
# Use browser Developer Tools (F12)
# Go to Network tab
# Make request (e.g., refresh dashboard)
# Click request and check:
# - Request URL (should not have duplicate paths)
# - Request headers (Authorization should have Bearer token)
# - Response status (should be 200)
# - Response body (should have data)
```

### Test API with Postman

1. Install Postman
2. Create new request
3. Set method to GET
4. Set URL to `http://127.0.0.1:8000/api/v1/plans`
5. Go to "Authorization" tab
6. Select "Bearer Token"
7. Paste your JWT
8. Send request
9. Should see plans data in response

---

## 📧 TESTING EMAIL CONFIRMATIONS

### Configure Email Service

```powershell
# Set environment variables
$env:MAIL_SERVER = "smtp.gmail.com"
$env:MAIL_PORT = "587"
$env:MAIL_STARTTLS = "true"
$env:MAIL_USERNAME = "your-email@gmail.com"
$env:MAIL_PASSWORD = "your-gmail-app-password"
$env:MAIL_FROM = "billing@billsphere.com"
$env:MAIL_FROM_NAME = "BillSphere"
$env:FRONTEND_URL = "http://localhost:5173"

# Restart backend to apply changes
```

### Monitor Email Sending

```bash
# Check backend logs for email send attempts
grep -i "email sent" backend/logs/billsphere.log

# Check for email errors
grep -i "email.*error" backend/logs/billsphere.log

# For Gmail: enable "Less Secure Apps"
# https://myaccount.google.com/lesssecureapps

# Or use Gmail App Password:
# https://myaccount.google.com/apppasswords
```

---

## 🚨 TROUBLESHOOTING COMMANDS

### Issue: "0 records" still showing

```bash
# 1. Clear browser cache
Remove-Item "$env:APPDATA\Local\BraveSoftware\Brave-Browser\User Data\Default\Cache\*" -Recurse

# 2. Check backend is running
curl http://127.0.0.1:8000/docs

# 3. Check database connection
psql -U postgres -c "SELECT version();"

# 4. Check API returns data
curl http://127.0.0.1:8000/api/v1/plans

# 5. Check JWT is valid
# Go to https://jwt.io and paste your token
```

### Issue: Port already in use

```bash
# Find process using port 8000
Get-NetTCPConnection -LocalPort 8000

# Kill process (replace PID with actual value)
Stop-Process -Id <PID> -Force

# Find process using port 5173
Get-NetTCPConnection -LocalPort 5173

# Kill process
Stop-Process -Id <PID> -Force
```

### Issue: Database connection failed

```bash
# Check PostgreSQL is running
Get-Service postgresql*

# Start PostgreSQL if stopped
Start-Service postgresql-x64-18

# Test connection
psql -U postgres -h localhost -c "SELECT NOW();"

# Check password
psql -U postgres -h localhost -W -c "SELECT NOW();"
```

### Issue: Email not sending

```bash
# Check email configuration
echo $env:MAIL_USERNAME
echo $env:MAIL_PASSWORD

# Test SMTP connection (Python)
python -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'your-app-password')
print('SMTP connection successful')
server.quit()
"

# Check Gmail app password
# Use 16-character app password, not regular password
```

---

## 📊 PERFORMANCE TESTING

```bash
# Install locust (load testing)
pip install locust

# Run load test
cd backend
locust -f loadtest/locustfile.py

# This will start a web interface at http://localhost:8089
# Set number of users and spawn rate
# Monitor response times and errors
```

---

## 🔒 SECURITY CHECKS

```bash
# Verify JWT is working
curl -X POST http://127.0.0.1:8000/api/v1/auth/login `
  -d '{"email":"test@example.com","password":"wrongpass"}' `
  -H "Content-Type: application/json"
# Should return 401 Unauthorized

# Verify unauthorized requests are blocked
curl http://127.0.0.1:8000/api/v1/customers
# Should return 403 Forbidden

# Verify password hashing
# Check in database: SELECT email, hashed_password FROM users;
# Should NOT see plain text passwords (starts with $2b$ from bcrypt)
```

---

## ✨ QUICK REFERENCE

| Component | Port | URL |
|-----------|------|-----|
| Frontend | 5173 | http://localhost:5173 |
| Backend | 8000 | http://127.0.0.1:8000 |
| API Docs | 8000 | http://127.0.0.1:8000/docs |
| ReDoc | 8000 | http://127.0.0.1:8000/redoc |
| PostgreSQL | 5432 | postgres://postgres@localhost:5432/billsphere |
| Redis | 6379 | redis://localhost:6379 |

| Endpoint | Method | Purpose |
|----------|--------|---------|
| /plans | GET | List plans |
| /customers | GET | List customers |
| /subscriptions | GET | List subscriptions |
| /invoices | GET | List invoices |
| /payments | GET | List payments |
| /refunds | GET | List refunds (NEW) |
| /refunds | POST | Create refund (NEW) |
| /audit-logs | GET | List audit logs |

---

## ✅ FINAL VERIFICATION CHECKLIST

- [ ] Backend running on 8000
- [ ] Frontend running on 5173
- [ ] Dashboard shows plans (not "0 records")
- [ ] Dashboard shows customers (not "0 records")
- [ ] All API endpoints return 200
- [ ] Refunds endpoints working
- [ ] Audit logs recording actions
- [ ] Emails configured and sending
- [ ] Database contains test data
- [ ] JWT authentication working

---

**Once All Tests Pass**: Application is ready for production deployment! 🚀

Document Version: 1.0  
Last Updated: August 29, 2026
