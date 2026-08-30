# BillSphere Backend Endpoints Documentation

Generated: August 29, 2026

## Status Overview

This document outlines all critical backend endpoints for BillSphere billing platform.

---

## ✅ IMPLEMENTED ENDPOINTS

### Authentication & Users
- **POST** `/auth/register` - User registration
- **POST** `/auth/login` - User login with JWT
- **GET** `/users/me` - Get current user profile
- **PUT** `/users/me` - Update user profile
- **POST** `/auth/password-reset` - Request password reset
- **POST** `/auth/password-reset-confirm` - Confirm password reset

### Customers
- **POST** `/customers` - Create customer (linked to current user)
- **GET** `/customers` - List customers for current user
- **GET** `/customers/{customer_id}` - Get customer details
- **PUT** `/customers/{customer_id}` - Update customer
- **DELETE** `/customers/{customer_id}` - Delete customer

### Plans
- **POST** `/plans` - Create subscription plan
- **GET** `/plans` - List all plans with pagination
- **GET** `/plans/{plan_id}` - Get plan details
- **PUT** `/plans/{plan_id}` - Update plan
- **DELETE** `/plans/{plan_id}` - Delete plan

### Subscriptions
- **POST** `/subscriptions` - Create subscription
- **GET** `/subscriptions` - List subscriptions
- **GET** `/subscriptions/{subscription_id}` - Get subscription details
- **PUT** `/subscriptions/{subscription_id}` - Update subscription
- **POST** `/subscriptions/{subscription_id}/cancel` - Cancel subscription
- **POST** `/subscriptions/{subscription_id}/pause` - Pause subscription
- **POST** `/subscriptions/{subscription_id}/resume` - Resume subscription

### Invoices
- **POST** `/invoices` - Create invoice
- **GET** `/invoices` - List invoices with pagination
- **GET** `/invoices/{invoice_id}` - Get invoice details
- **GET** `/invoices/{invoice_id}/download` - Download invoice as PDF
- **POST** `/invoices/{invoice_id}/send` - Send invoice via email

### Payments
- **POST** `/payments` - Create payment
- **GET** `/payments` - List payments with pagination
- **GET** `/payments/{payment_id}` - Get payment details
- **POST** `/payments/checkout` - Create and process checkout
- **POST** `/payments/{payment_id}/success` - Mark payment successful
- **POST** `/payments/{payment_id}/failed` - Mark payment failed
- **GET** `/payments/confirmation` - Get payment confirmation details (for email tokens)
- **POST** `/payments/confirmation` - Confirm payment action from email link

### Refunds ✨ **NEWLY ADDED**
- **POST** `/refunds` - Create a refund for a payment
- **GET** `/refunds` - List all refunds with reason and status
- **GET** `/refunds/{refund_id}` - Get refund details

### Audit Logs
- **GET** `/audit-logs` - List audit log entries
  - Filters: entity_type, entity_id
  - Returns: Actor, Action, Timestamp, Target record

---

## 📋 AUDIT LOG FIELDS

The audit log system tracks all billing actions:

```
- id: Unique audit log ID
- actor_id: User ID who performed the action
- action: Action type (e.g., PAYMENT_CREATED, INVOICE_SENT, SUBSCRIPTION_CANCELLED)
- entity_type: Resource type (payment, invoice, subscription, customer, plan, refund)
- entity_id: ID of the affected resource
- description: Human-readable description of action
- timestamp: When action occurred
- details: JSON data with additional context
```

### Actions Logged

- **User Actions**
  - USER_CREATED
  - USER_UPDATED
  - USER_DELETED

- **Customer Actions**
  - CUSTOMER_CREATED
  - CUSTOMER_UPDATED
  - CUSTOMER_DELETED

- **Plan Actions**
  - PLAN_CREATED
  - PLAN_UPDATED
  - PLAN_DELETED
  - PLAN_ACTIVATED
  - PLAN_DEACTIVATED

- **Subscription Actions**
  - SUBSCRIPTION_CREATED
  - SUBSCRIPTION_UPDATED
  - SUBSCRIPTION_ACTIVATED
  - SUBSCRIPTION_CANCELLED
  - SUBSCRIPTION_PAUSED
  - SUBSCRIPTION_RESUMED
  - SUBSCRIPTION_EXPIRED

- **Invoice Actions**
  - INVOICE_CREATED
  - INVOICE_SENT
  - INVOICE_PAID
  - INVOICE_PARTIALLY_PAID
  - INVOICE_OVERDUE
  - INVOICE_REFUNDED

- **Payment Actions**
  - PAYMENT_CREATED
  - PAYMENT_SUCCESS
  - PAYMENT_FAILED
  - PAYMENT_RETRY
  - REFUND_CREATED
  - REFUND_PROCESSED

---

## 📧 EMAIL CONFIRMATIONS

### Implemented Email Templates

1. **Invoice Generated**
   - Sent when invoice is created
   - Contains invoice number and amount

2. **Payment Successful**
   - Sent when payment is completed
   - Contains payment reference and amount

3. **Payment Failed**
   - Sent when payment fails
   - Prompts user to retry payment

4. **Payment Confirmation Required**
   - Sent when payment needs email confirmation
   - Contains unique confirmation token link

5. **Subscription Activated**
   - Sent when subscription starts
   - Contains plan details

6. **Subscription Cancelled**
   - Sent when subscription is cancelled
   - Contains effective date

### Email Configuration

Set these environment variables:
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_STARTTLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@billsphere.com
MAIL_FROM_NAME=BillSphere
FRONTEND_URL=http://localhost:5173
```

---

## 🔗 USER-CUSTOMER RELATIONSHIP

### Database Model

**Users Table**
- id (Primary Key)
- email (Unique)
- first_name
- last_name
- hashed_password
- role (admin, user)
- is_active
- created_at

**Customers Table**
- id (Primary Key)
- owner_id (Foreign Key → users.id) **[Links user to customer]**
- company_name
- contact_name
- email (Unique)
- phone
- tax_id
- is_active
- created_at

### Creating Customer for User

When a user creates a customer:
1. User's auth token is validated (extract user_id from JWT)
2. owner_id is set to the current user_id
3. Customer is associated with that user
4. Only the user can see/modify their own customers
5. Audit log records the action

```
POST /customers
{
    "company_name": "Acme Corp",
    "contact_name": "John Doe",
    "email": "john@acme.com",
    "phone": "+1-555-1234"
}
```

Response:
```json
{
    "id": 42,
    "owner_id": 1,
    "company_name": "Acme Corp",
    "contact_name": "John Doe",
    "email": "john@acme.com",
    "created_at": "2026-08-29T10:30:00Z"
}
```

---

## 🔄 BILLING ENGINE FLOW

### Complete Billing Lifecycle

1. **User Creates Customer** → audit log
2. **Admin Creates Plan** → audit log (includes platform, pricing, billing cycle)
3. **Customer Subscribes to Plan** → audit log, confirmation email
4. **Billing Cycle Triggers** → invoice created, audit log
5. **Invoice Sent to Customer** → email confirmation
6. **Payment Processing** → audit log
7. **Payment Confirmation Email** → customer confirms or denies
8. **Payment Success** → email confirmation, audit log
9. **Optional: Refund Process** → audit log, refund recorded, email sent

### Audit Log Verification

Every action above creates a corresponding audit log entry. Query:
```
GET /audit-logs?entity_type=subscription&entity_id=123
```

---

## 🚀 PERFORMANCE OPTIMIZATION

### Query Optimization
- Pagination: All list endpoints support `page` and `page_size` parameters (default: 10, max: 100)
- Filtering: Use entity_type and entity_id to filter audit logs
- Indexing: owner_id indexed on customers, subscriptions, invoices, payments for fast lookups

### Cache Strategy
- Plans: Cached on frontend after initial load
- Customers: Paginated to reduce payload
- Audit logs: Most recent entries paginated

### Latency Reduction
- Database connections pooled (SQLAlchemy)
- FastAPI uvicorn with 4 workers
- Redis for caching and job queue
- Celery for async email sending

---

## 🔐 SECURITY

- **Authentication**: JWT tokens (10-hour expiration)
- **Authorization**: All endpoints verify ownership (owner_id == current_user_id)
- **Email Confirmations**: Token-based verification with 30-minute expiration
- **Audit Logging**: All privileged operations logged
- **Password**: Hashed with bcrypt (12 rounds)

---

## 📊 DASHBOARD INTEGRATION

### Admin Dashboard Data Points

```
GET /subscriptions → Active/Trialing subscriptions count
GET /invoices → Failed invoices, overdue count
GET /payments → Successful payment count and total revenue
GET /plans → Plan records, active subscriber count per plan
GET /customers → Customer records, creation dates
GET /audit-logs → Recent actions for compliance audit
GET /refunds → Refund records with reason and status
```

**Note**: All endpoints now use correct paths (e.g., `/customers` not `/customers/customers`)

---

## 🐛 KNOWN ISSUES & FIXES

### FIXED Issues
1. ✅ Admin dashboard was calling `/plans/plans` instead of `/plans` → **FIXED**
2. ✅ Admin dashboard was calling `/customers/customers` instead of `/customers` → **FIXED**
3. ✅ Refunds endpoints were missing → **ADDED** `/refunds` (GET/POST)
4. ✅ Refund tracking was only via payment model → **IMPROVED** with dedicated refunds endpoint

### Next Steps
1. Ensure all billing actions trigger email confirmations
2. Add loading animations to dashboard
3. Test full billing flow end-to-end
4. Verify audit logs capture all actions

---

## 📞 Testing Instructions

### Test Endpoints with cURL

**List Plans:**
```bash
curl -H "Authorization: Bearer YOUR_JWT" \
  http://127.0.0.1:8000/api/v1/plans
```

**List Customers:**
```bash
curl -H "Authorization: Bearer YOUR_JWT" \
  http://127.0.0.1:8000/api/v1/customers
```

**List Refunds:**
```bash
curl -H "Authorization: Bearer YOUR_JWT" \
  http://127.0.0.1:8000/api/v1/refunds
```

**List Audit Logs:**
```bash
curl -H "Authorization: Bearer YOUR_JWT" \
  http://127.0.0.1:8000/api/v1/audit-logs
```

**View API Docs:**
```
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc
```

---

**Document Version**: 1.0  
**Last Updated**: August 29, 2026  
**Maintainer**: BillSphere Development Team
