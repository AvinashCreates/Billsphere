import { Navigate, Outlet } from "react-router-dom";

interface ProtectedRouteProps {
  adminOnly?: boolean;
  customerOnly?: boolean;
}

/**
 * Wraps a route and redirects away if the logged-in user's role
 * doesn't match what the route requires. Role is read from localStorage,
 * which is set right after login (see Login.tsx).
 */
function ProtectedRoute({ adminOnly = false, customerOnly = false }: ProtectedRouteProps) {
  const role = localStorage.getItem("role");
  const isAdmin = role === "admin";

  if (adminOnly && !isAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  if (customerOnly && isAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}

export default ProtectedRoute;