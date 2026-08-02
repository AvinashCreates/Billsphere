import type { ReactNode } from "react";
import { useAuth } from "../contexts/AuthContext";

interface RoleGuardProps {
  /** Roles allowed to see the children, e.g. ["admin"] */
  allow: string[];
  children: ReactNode;
  /** Optional content to show instead, when role isn't permitted */
  fallback?: ReactNode;
}

/**
 * Wrap any UI block (button, section, table column, form...) to show it
 * only to specific roles. Use instead of repeating `{role === "admin" && ...}`.
 *
 * <RoleGuard allow={["admin"]}>
 *   <button onClick={createPlan}>Create Plan</button>
 * </RoleGuard>
 */
function RoleGuard({ allow, children, fallback = null }: RoleGuardProps) {
  const { role } = useAuth();

  if (!role || !allow.includes(role)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}

export default RoleGuard;