# PulseFlow External App

This folder contains a separate subscription app that is linked to the existing BillSphere application.

## Purpose

The app demonstrates an external product or brand experience where a user selects a subscription plan and is redirected to BillSphere's payment flow for checkout.

## How it works

1. User selects a plan in this app.
2. The app redirects to the BillSphere subscription confirmation page.
3. Billsphere handles the actual billing flow using the selected plan ID.

## Redirect target

The payment redirect uses the following format:

```
http://localhost:5173/customer/plans/{planId}/confirm?source=external-app&planName={planName}
```

The redirect preserves the selected plan through BillSphere login. If the user
is not logged in, BillSphere sends them to login and returns them to the same
plan confirmation page after authentication.

## Plans Available

- **Mini**: ₹199/month - Basic listening
- **Premium**: ₹499/month - Unlimited skips & high quality (Popular)
- **Family**: ₹799/month - 6 users with parental controls

## Run locally

### Step 1: Start the external app
From the app directory:

```bash
cd app
python -m http.server 3001
```

Then open: http://127.0.0.1:3001

### Step 2: Make sure BillSphere is running

The BillSphere services must be running:

```bash
# Terminal 1: Backend
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: External App
cd app
python -m http.server 3001
```

### Step 3: Test the flow

1. Open http://localhost:5173
2. Register or log in
3. Open http://127.0.0.1:3001 in same browser
4. Select a plan
5. You'll be redirected back to BillSphere
6. Complete the subscription

## Configuration

Edit `app/script.js` to change:

```javascript
const billsphereBase = 'http://localhost:5173'; // Change this URL
```

## Features

- 🎨 Spotify-inspired design
- 📱 Responsive layout
- 💳 Seamless redirect to BillSphere
- 🎵 Plan showcase with features
- ✨ Smooth animations and transitions

---

**Status**: ✅ Fully Integrated with BillSphere

