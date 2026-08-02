import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

interface ProtectedRouteProps {
  /** Roles allowed to view this route. Omit to allow any logged-in user. */
  allow?: string[];
  children: ReactNode;
}

/**
 * Wrap a <Route element={...}> with this to:
 *  - redirect to /login if not authenticated
 *  - redirect to /dashboard if authenticated but role isn't in `allow`
 */
function ProtectedRoute({ allow, children }: ProtectedRouteProps) {
  const { isAuthenticated, role, loading } = useAuth();

  if (loading) {
    // Auth status still resolving (checking token) - render nothing briefly
    // rather than flashing a redirect.
    return null;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allow && role && !allow.includes(role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}

export default ProtectedRoute;