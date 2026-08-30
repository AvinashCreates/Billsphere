import { useEffect, useMemo, useState, type ReactNode } from "react";
import { getElearningPlans, getMySubscriptions, type BillSpherePlan, type BillSphereSubscription } from "../services/billsphere";
import { LearnerEntitlementsContext } from "./LearnerEntitlementsContext";

function activeSubscription(subscriptions: BillSphereSubscription[]) {
  return subscriptions
    .filter((subscription) => ["active", "trial", "trialing", "past_due"].includes(subscription.status.toLowerCase()))
    .sort((left, right) => new Date(right.start_date).getTime() - new Date(left.start_date).getTime())[0] || null;
}

function featureValue(plan: BillSpherePlan | null, names: string[]) {
  const features = plan?.feature_entitlements;
  if (!features || Array.isArray(features)) return undefined;
  const match = Object.entries(features).find(([key]) => names.includes(key.toLowerCase()));
  return match?.[1];
}

export function LearnerEntitlementsProvider({ children }: { children: ReactNode }) {
  const [plans, setPlans] = useState<BillSpherePlan[]>([]);
  const [subscription, setSubscription] = useState<BillSphereSubscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = async () => {
    setLoading(true);
    try {
      const [nextPlans, nextSubscriptions] = await Promise.all([getElearningPlans(), getMySubscriptions()]);
      setPlans(nextPlans);
      setSubscription(activeSubscription(nextSubscriptions));
      setError(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Billing data is temporarily unavailable");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => { void refresh(); }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  const plan = useMemo(() => plans.find((candidate) => candidate.id === subscription?.plan_id) || null, [plans, subscription]);
  const hasEntitlement = (name: string) => {
    const features = plan?.feature_entitlements;
    if (Array.isArray(features)) return features.some((feature) => feature.toLowerCase() === name.toLowerCase());
    return Boolean(featureValue(plan, [name.toLowerCase()]));
  };
  const catalogTier = String(featureValue(plan, ["catalog_tier", "course_catalog", "catalog_access"]) || "standard");
  const mentorValue = featureValue(plan, ["mentor_sessions", "mentor_sessions_per_month"]);

  return <LearnerEntitlementsContext.Provider value={{
    plans, subscription, plan, loading, error, refresh, catalogTier,
    canIssueCertificate: hasEntitlement("can_issue_certificate") || hasEntitlement("certificates"),
    mentorSessionsRemaining: typeof mentorValue === "number" ? mentorValue : null,
    canDownloadOffline: hasEntitlement("can_download_offline") || hasEntitlement("offline_downloads"),
    hasEntitlement,
  }}>{children}</LearnerEntitlementsContext.Provider>;
}
