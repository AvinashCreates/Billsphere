import {
  BrowserRouter,
  Routes,
  Route,
  useLocation,
} from "react-router-dom";

import { lazy, Suspense, useEffect } from "react";

// ======================================================
// PAGES
// ======================================================

const Usage = lazy(() => import("./pages/Usage"));
const ConfirmSubscription = lazy(() => import("./pages/ConfirmSubscription"));
const DemoDashboard = lazy(() => import("./pages/DemoDashboard"));
const Landing = lazy(() => import("./pages/Landing"));
const Login = lazy(() => import("./pages/Login"));
const Register = lazy(() => import("./pages/Register"));
const PlanDetails = lazy(() => import("./pages/PlanDetails"));
const AdminDashboard = lazy(() => import("./pages/AdminDashboard"));
const AdminUsers = lazy(() => import("./pages/AdminUsers"));
const UserDashboard = lazy(() => import("./pages/UserDashboard"));
const Payment = lazy(() => import("./pages/Payment"));
const PaymentConfirmation = lazy(() => import("./pages/PaymentConfirmation"));
const Customers = lazy(() => import("./pages/Customers"));
const Invoices = lazy(() => import("./pages/Invoices"));
const Plans = lazy(() => import("./pages/Plans"));
const Settings = lazy(() => import("./pages/Settings"));
const Profile = lazy(() => import("./pages/Profile"));
const PaymentHistory = lazy(() => import("./pages/PaymentHistory"));
const MyPlan = lazy(() => import("./pages/MyPlan"));
const Billing = lazy(() => import("./pages/Billing"));
const ForgotPassword = lazy(() => import("./pages/ForgotPassword"));
const SetPassword = lazy(() => import("./pages/SetPassword"));
const Notifications = lazy(() => import("./pages/Notifications"));
const HelpSupport = lazy(() => import("./pages/HelpSupport"));
const AdminSupport = lazy(() => import("./pages/AdminSupport"));
const ELearning = lazy(() => import("./pages/ELearning"));

// ======================================================
// LAYOUTS
// ======================================================

import DashboardLayout from "./layouts/DashboardLayout";
import CustomerLayout from "./layouts/CustomerLayout";

// ======================================================
// APP CONTENT
// ======================================================

function AppContent() {
  const location = useLocation();

  // ====================================================
  // THEME
  // ====================================================

  useEffect(() => {
    const mode = document.documentElement.getAttribute("data-mode") || "light";
    document.documentElement.classList.toggle("dark", mode === "dark");
    document.documentElement.style.colorScheme = mode;
  }, [location.pathname]);

  return (
    <Suspense fallback={<div className="app-loading" role="status">Loading...</div>}>
      <Routes>

      {/* ==================================================
          LANDING
      ================================================== */}

      <Route
        path="/"
        element={<Landing />}
      />

      {/* ==================================================
          AUTHENTICATION
      ================================================== */}

      <Route
        path="/login"
        element={<Login />}
      />

      <Route
        path="/register"
        element={<Register />}
      />

      <Route
        path="/forgot-password"
        element={<ForgotPassword />}
      />

      <Route
        path="/set-password"
        element={<SetPassword />}
      />

      {/* ==================================================
          PUBLIC DEMO
      ================================================== */}

      <Route
        path="/demo-dashboard"
        element={<DemoDashboard />}
      />

      {/* ==================================================
          CUSTOMER DASHBOARD HOME
          
          UserDashboard contains its own:
          - Navbar
          - Sidebar
          - Main content
      ================================================== */}

      <Route
        path="/customer/dashboard"
        element={<UserDashboard />}
      />

      {/* ==================================================
          CUSTOMER AREA

          CustomerLayout provides:
          - Customer navbar
          - Customer sidebar
          - Main content area
      ================================================== */}

      <Route element={<CustomerLayout />}>

        <Route
          path="/customer/learning"
          element={<ELearning />}
        />

        {/* ==================================================
            CUSTOMER MY PLAN
        ================================================== */}

        <Route
          path="/customer/subscriptions"
          element={<MyPlan />}
        />

        {/* ==================================================
            CUSTOMER PLANS
        ================================================== */}

        <Route
          path="/customer/plans"
          element={<Plans />}
        />

        {/* ==================================================
            CUSTOMER PLAN DETAILS
        ================================================== */}

        <Route
          path="/customer/plans/:planId"
          element={<PlanDetails />}
        />

        {/* ==================================================
            CONFIRM SUBSCRIPTION
        ================================================== */}

        <Route
          path="/customer/plans/:planId/confirm"
          element={<ConfirmSubscription />}
        />

        {/* ==================================================
            CUSTOMER INVOICES
        ================================================== */}

        <Route
          path="/customer/invoices"
          element={<Invoices />}
        />

        {/* ==================================================
            CUSTOMER PAYMENTS
        ================================================== */}

        <Route
          path="/customer/payments"
          element={<Payment />}
        />

        {/* ==================================================
            CUSTOMER PAYMENT HISTORY
        ================================================== */}

        <Route
          path="/customer/payment-history"
          element={<PaymentHistory />}
        />

        {/* ==================================================
            CUSTOMER BILLING
        ================================================== */}

        <Route
          path="/customer/billing"
          element={<Billing />}
        />

        {/* ==================================================
            CUSTOMER USAGE
        ================================================== */}

        <Route
          path="/customer/usage"
          element={<Usage />}
        />

        {/* ==================================================
            CUSTOMER NOTIFICATIONS
        ================================================== */}

        <Route
          path="/customer/notifications"
          element={<Notifications />}
        />

        {/* ==================================================
            CUSTOMER SETTINGS
        ================================================== */}

        <Route
          path="/customer/settings"
          element={<Settings />}
        />

        {/* ==================================================
            CUSTOMER HELP & SUPPORT
        ================================================== */}

        <Route
          path="/customer/help"
          element={<HelpSupport />}
        />

        {/* ==================================================
            CUSTOMER ADMIN SUPPORT

            Customers can:
            - Raise support tickets
            - View ticket status
            - Communicate with BillSphere admin
        ================================================== */}

        <Route
          path="/customer/admin-support"
          element={<AdminSupport />}
        />

        {/* ==================================================
            CUSTOMER PLAN PAYMENT
        ================================================== */}

        <Route
          path="/customer/plans/:planId/payment"
          element={<Payment />}
        />

        {/* ==================================================
            PAYMENT EMAIL CONFIRMATION

            Opens inside the existing CustomerLayout
            so the YES / NO email confirmation flow
            remains inside the BillSphere customer shell.
        ================================================== */}

        <Route
          path="/payment-confirmation"
          element={<PaymentConfirmation />}
        />

      </Route>

      {/* ==================================================
          ADMIN DASHBOARD HOME
      ================================================== */}

      <Route
        path="/admin/dashboard"
        element={<AdminDashboard />}
      />

      {/* ==================================================
          ADMIN / APPLICATION PAGES

          These continue using DashboardLayout.
      ================================================== */}

      <Route element={<DashboardLayout />}>

        {/* ==================================================
            ADMIN CUSTOMERS
        ================================================== */}

        <Route
          path="/customers"
          element={<Customers />}
        />

        {/* ==================================================
            ADMIN INVOICES
        ================================================== */}

        <Route
          path="/invoices"
          element={<Invoices />}
        />

        {/* ==================================================
            ADMIN SETTINGS
        ================================================== */}

        <Route
          path="/settings"
          element={<Settings />}
        />

        {/* ==================================================
            ADMIN PROFILE
        ================================================== */}

        <Route
          path="/profile"
          element={<Profile />}
        />

      </Route>

      {/* ==================================================
          LEGACY ADMIN USERS
      ================================================== */}

      <Route
        path="/admin/users"
        element={<AdminUsers />}
      />

      </Routes>
    </Suspense>
  );
}

// ======================================================
// APP
// ======================================================

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;