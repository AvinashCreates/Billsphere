import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { CreditCard, CheckCircle, Clock, XCircle, AlertTriangle } from "lucide-react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getMySubscriptions, cancelSubscription, renewSubscription } from "../assets/services/api";
import { useToast } from "../components/ToastProvider";
import EmptyState from "../components/EmptyState";
import Skeleton from "../components/Skeleton";
import AnalyticsChartCard from "../components/AnalyticsChartCard";
import StatusBadge from "../components/StatusBadge";

interface Subscription {
  id: number;
  plan_id: number;
  status: string;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
}

const statusStyles: Record<string, { color: string; icon: ReactNode; label: string }> = {
  active: { color: "text-green-600 bg-green-50", icon: <CheckCircle size={20} />, label: "Active" },
  trial: { color: "text-blue-600 bg-blue-50", icon: <Clock size={20} />, label: "Trial" },
  past_due: { color: "text-amber-600 bg-amber-50", icon: <Clock size={20} />, label: "Past Due" },
  cancelled: { color: "text-red-600 bg-red-50", icon: <XCircle size={20} />, label: "Cancelled" },
};

// How many days out counts as "deadline is near" -> triggers the red warning styling
const DEADLINE_WARNING_DAYS = 5;

function UserDashboard() {
  const { notify } = useToast();
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  function load() {
    setLoading(true);
    getMySubscriptions()
      .then(setSubscriptions)
      .catch(() => {
        notify({
          title: "Subscription load failed",
          description: "Unable to fetch your current subscription status.",
          variant: "error",
        });
      })
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
  }, []);

  const activeSub = subscriptions.find((s) => s.status === "active" || s.status === "trial" || s.status === "past_due");

  // Days remaining until the current period ends (negative = already past due)
  const daysRemaining = useMemo(() => {
    if (!activeSub) return null;
    const end = new Date(activeSub.current_period_end).getTime();
    return Math.ceil((end - Date.now()) / (1000 * 60 * 60 * 24));
  }, [activeSub]);

  const deadlineIsNear =
    activeSub != null &&
    activeSub.status !== "cancelled" &&
    daysRemaining != null &&
    daysRemaining <= DEADLINE_WARNING_DAYS;

  async function handleCancel(immediate: boolean) {
    if (!activeSub) return;
    setActionLoading(true);
    try {
      await cancelSubscription(activeSub.id, immediate);
      notify({
        title: "Subscription updated",
        description: immediate ? "Cancelled immediately." : "Will cancel at period end.",
        variant: "info",
      });
      load();
    } catch (err: any) {
      notify({
        title: "Action failed",
        description: err.message || "Could not cancel subscription.",
        variant: "error",
      });
    } finally {
      setActionLoading(false);
    }
  }

  async function handleRenew() {
    if (!activeSub) return;
    setActionLoading(true);
    try {
      await renewSubscription(activeSub.id);
      notify({
        title: "Subscription renewed",
        description: "Your plan is renewed for the next billing period.",
        variant: "success",
      });
      load();
    } catch (err: any) {
      notify({
        title: "Renewal failed",
        description: err.message || "Could not renew subscription.",
        variant: "error",
      });
    } finally {
      setActionLoading(false);
    }
  }

  const chartData = useMemo(() => {
    const baseValue = activeSub ? Math.max(activeSub.plan_id * 120 + 4200, 4200) : 4500;
    return [
      { label: "Week 1", value: baseValue * 0.8 },
      { label: "Week 2", value: baseValue * 0.88 },
      { label: "Week 3", value: baseValue * 0.96 },
      { label: "Week 4", value: baseValue * 1.04 },
    ];
  }, [activeSub]);

  return (
    <div className="space-y-8">
      <div className="mb-6">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">Subscriber dashboard</p>
        <h1 className="mt-3 text-4xl font-semibold text-slate-900 dark:text-white">Subscription health</h1>
        <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600 dark:text-slate-400">
          Track your plan, renewal cadence, and action items in a centered enterprise workspace.
        </p>
      </div>

      {loading && (
        <div className="grid gap-6 lg:grid-cols-2">
          <Skeleton className="h-60 rounded-[24px]" />
          <Skeleton className="h-60 rounded-[24px]" />
        </div>
      )}

      {!loading && !activeSub && (
        <EmptyState
          title="No active plan found"
          description="Choose a plan to unlock billing automation, invoices, and revenue reporting."
          primaryAction={{ label: "Explore plans", path: "/plans" }}
          secondaryAction={{ label: "Visit invoices", path: "/invoices" }}
          icon={<CreditCard size={24} />}
        />
      )}

      {!loading && activeSub && (
        <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <section className="panel rounded-[24px] p-8 shadow-sm">
            <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">Current plan</p>
                <h2 className="mt-3 text-3xl font-semibold text-slate-900 dark:text-white">Plan #{activeSub.plan_id}</h2>
              </div>
              <StatusBadge variant={deadlineIsNear ? "danger" : activeSub.status === "active" ? "success" : activeSub.status === "trial" ? "info" : activeSub.status === "past_due" ? "warning" : "danger"}>
                {statusStyles[activeSub.status]?.label || activeSub.status}
              </StatusBadge>
            </div>

            <div className="mt-8 grid gap-5 sm:grid-cols-2">
              <div className="rounded-[24px] border border-slate-200/70 bg-slate-50/80 p-5 dark:border-slate-700/70 dark:bg-slate-950/50">
                <p className="text-sm text-slate-500 dark:text-slate-400">Billing period start</p>
                <p className="mt-2 text-lg font-semibold text-slate-900 dark:text-white">{new Date(activeSub.current_period_start).toLocaleDateString()}</p>
              </div>

              <div
                className={`rounded-[24px] border p-5 transition-colors ${
                  deadlineIsNear
                    ? "border-red-300 bg-red-50 dark:border-red-500/40 dark:bg-red-950/40"
                    : "border-slate-200/70 bg-slate-50/80 dark:border-slate-700/70 dark:bg-slate-950/50"
                }`}
              >
                <p className={`text-sm ${deadlineIsNear ? "text-red-600 dark:text-red-300" : "text-slate-500 dark:text-slate-400"}`}>
                  Next renewal
                </p>
                <p className={`mt-2 text-lg font-semibold ${deadlineIsNear ? "text-red-700 dark:text-red-200" : "text-slate-900 dark:text-white"}`}>
                  {new Date(activeSub.current_period_end).toLocaleDateString()}
                </p>
                {deadlineIsNear && (
                  <p className="mt-2 flex items-center gap-1.5 text-xs font-semibold text-red-600 dark:text-red-300">
                    <AlertTriangle size={13} />
                    {daysRemaining != null && daysRemaining >= 0
                      ? `Renews in ${daysRemaining} day${daysRemaining === 1 ? "" : "s"}`
                      : "Renewal is overdue"}
                  </p>
                )}
              </div>
            </div>

            {activeSub.cancel_at_period_end && (
              <div className="mt-6 rounded-[24px] border border-amber-200 bg-amber-50 px-5 py-4 text-sm text-amber-700 dark:border-amber-500/20 dark:bg-amber-500/10 dark:text-amber-300">
                This subscription is scheduled to cancel at the end of the current period.
              </div>
            )}

            <div className="mt-8 flex flex-wrap gap-4">
              <Link to="/plans" className="btn-ghost">
                Change plan
              </Link>
              {activeSub.status !== "cancelled" && !activeSub.cancel_at_period_end && (
                <button
                  onClick={() => handleCancel(false)}
                  disabled={actionLoading}
                  className="btn-ghost"
                >
                  Cancel at period end
                </button>
              )}
              {activeSub.status !== "cancelled" && (
                <button
                  onClick={() => handleCancel(true)}
                  disabled={actionLoading}
                  className="btn-ghost"
                >
                  Cancel immediately
                </button>
              )}
              {(activeSub.status === "past_due" || activeSub.cancel_at_period_end || deadlineIsNear) && (
                <button
                  onClick={handleRenew}
                  disabled={actionLoading}
                  className="btn-primary"
                >
                  Renew now
                </button>
              )}
            </div>
          </section>

          <AnalyticsChartCard title="Billing forecast" description="Expected revenue movement for your current plan.">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 20, right: 20, left: -10, bottom: 0 }}>
                <defs>
                  <linearGradient id="userRevenue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563eb" stopOpacity={0.28} />
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.15)" />
                <XAxis dataKey="label" stroke="#64748b" />
                <YAxis stroke="#64748b" tickFormatter={(value) => `$${Math.round(value / 1000)}k`} />
                <Tooltip contentStyle={{ borderRadius: 18, border: "1px solid rgba(148, 163, 184, 0.16)", background: "rgba(255,255,255,0.96)" }} formatter={(value: any) => `$${Number(value).toLocaleString()}`} />
                <Area type="monotone" dataKey="value" stroke="#2563eb" fill="url(#userRevenue)" strokeWidth={3} />
              </AreaChart>
            </ResponsiveContainer>
          </AnalyticsChartCard>
        </div>
      )}
    </div>
  );
}

export default UserDashboard;