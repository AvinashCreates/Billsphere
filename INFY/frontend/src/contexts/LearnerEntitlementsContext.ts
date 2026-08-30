import { createContext } from "react";
import type { BillSpherePlan, BillSphereSubscription } from "../services/billsphere";

export interface LearnerEntitlements {
  plans: BillSpherePlan[];
  subscription: BillSphereSubscription | null;
  plan: BillSpherePlan | null;
  loading: boolean;
  error: string | null;
  catalogTier: string;
  canIssueCertificate: boolean;
  mentorSessionsRemaining: number | null;
  canDownloadOffline: boolean;
  hasEntitlement: (name: string) => boolean;
  refresh: () => Promise<void>;
}

export const LearnerEntitlementsContext = createContext<LearnerEntitlements | undefined>(undefined);
