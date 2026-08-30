import { useContext } from "react";
import { LearnerEntitlementsContext } from "./LearnerEntitlementsContext";

export function useLearnerEntitlements() {
  const context = useContext(LearnerEntitlementsContext);
  if (!context) throw new Error("useLearnerEntitlements must be used within LearnerEntitlementsProvider");
  return context;
}
