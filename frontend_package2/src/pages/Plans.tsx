import { useEffect, useState } from "react";
import { Crown, Sparkles, CheckCircle2 } from "lucide-react";
import { getPlans, subscribeToPlan } from "../assets/services/api";
import PageHeader from "../components/PageHeader";
import Card from "../components/common/Card";
import Skeleton from "../components/Skeleton";
import EmptyState from "../components/EmptyState";
import { useToast } from "../components/ToastProvider";
import AppShell from "../components/layout/AppShell";
import DataTable from "../components/table/DataTable";

interface Plan {
  id: number;
  name: string;
  price: number;
  billing_interval: string;
  trial_period_days: number;
}

function Plans() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedPlan, setSelectedPlan] = useState("");
  const [subscribingId, setSubscribingId] = useState<number | null>(null);
  const { notify } = useToast();

  useEffect(() => {
    loadPlans();
  }, []);

  async function loadPlans() {
    try {
      setLoading(true);
      const data = await getPlans();
      setPlans(data);
    } catch (err: any) {
      setError(err.message || "Could not load plans");
      notify({
        title: "Plan load failed",
        description: err.message || "Unable to fetch plan offerings.",
        variant: "error",
      });
    } finally {
      setLoading(false);
    }
  }

  async function choosePlan(plan: Plan) {
    setError("");
    setSubscribingId(plan.id);

    try {
      await subscribeToPlan(plan.id);
      setSelectedPlan(plan.name);
      notify({
        title: "Plan activated",
        description: `You are now subscribed to the ${plan.name} plan.`,
        variant: "success",
      });
    } catch (err: any) {
      setError(err.message || "Could not subscribe to this plan");
      notify({
        title: "Subscription failed",
        description: err.message || "Unable to activate this plan.",
        variant: "error",
      });
    } finally {
      setSubscribingId(null);
    }
  }

  return (
    <AppShell>
      <div className="fade-in">
      <PageHeader
        eyebrow="Billing"
        title="Plans"
        description="Offer the right level of access and keep every subscription experience polished."
        action={<span className="inline-flex items-center gap-2"><Crown size={16} />Flexible options</span>}
      />

      {error && (
        <div className="mb-6 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900/40 dark:bg-red-950/40 dark:text-red-300">
          {error}
        </div>
      )}

      {loading ? (
        <div className="grid gap-6 md:grid-cols-3">
          {Array.from({ length: 3 }).map((_, index) => (
            <Card key={index} className="overflow-hidden">
              <Skeleton className="h-72 rounded-[24px]" />
            </Card>
          ))}
        </div>
      ) : plans.length === 0 ? (
        <EmptyState
          title="No plans available"
          description="There are no billing plans available right now. Please check back later or refresh."
          primaryAction={{ label: "Reload plans", path: "/plans" }}
          icon={<Crown size={24} />}
        />
      ) : (
        <div className="grid gap-6 md:grid-cols-3">
          {plans.map((plan) => (
            <Card key={plan.id} className="relative overflow-hidden">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-600">{plan.billing_interval}</p>
                  <h2 className="mt-2 text-2xl font-semibold text-slate-900 dark:text-white">{plan.name}</h2>
                </div>
                <div className="rounded-2xl bg-blue-500/10 p-3 text-blue-600">
                  <Sparkles size={18} />
                </div>
              </div>

              {plan.trial_period_days > 0 && (
                <div className="mt-4 inline-flex items-center gap-2 rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-700 dark:text-emerald-300">
                  <CheckCircle2 size={14} />
                  {plan.trial_period_days}-day free trial
                </div>
              )}

              <div className="mt-6">
                <p className="text-4xl font-semibold text-slate-900 dark:text-white">${plan.price}</p>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">per {plan.billing_interval === "yearly" ? "year" : "month"}</p>
              </div>

              <button
                onClick={() => choosePlan(plan)}
                disabled={subscribingId === plan.id}
                className="btn-primary mt-8 w-full"
              >
                {subscribingId === plan.id ? "Subscribing..." : "Choose Plan"}
              </button>
            </Card>
          ))}
        </div>
      )}

      {selectedPlan && (
        <div className="mt-8 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-700 dark:border-emerald-900/40 dark:bg-emerald-500/10 dark:text-emerald-300">
          Current selected plan: <strong>{selectedPlan}</strong>
        </div>
      )}

      {/* Admin: table view for plans */}
      <div className="mt-8">
        <Card title="All Plans">
          <DataTable
            columns={[
              { key: 'id', title: 'ID' },
              { key: 'name', title: 'Name' },
              { key: 'price', title: 'Price', render: (p: Plan) => `$${p.price}` },
              { key: 'interval', title: 'Interval', render: (p: Plan) => p.billing_interval },
              { key: 'trial', title: 'Trial (days)', render: (p: Plan) => p.trial_period_days ?? 0 },
              { key: 'actions', title: 'Actions', render: (p: Plan) => (
                <button onClick={() => choosePlan(p)} className="btn-ghost">Subscribe</button>
              ) },
            ]}
            data={plans}
          />
        </Card>
      </div>
      </div>
    </AppShell>
  );
}

export default Plans;
