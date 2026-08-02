import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { CheckCircle, Clock, XCircle, AlertTriangle, CreditCard, ArrowRight } from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getSubscriptionStats, getUpcomingRenewals, getPastDue } from "../assets/services/api";
import { useToast } from "../components/ToastProvider";
import KpiCard from "../components/KpiCard";
import AnalyticsChartCard from "../components/AnalyticsChartCard";
import Skeleton from "../components/Skeleton";
import StatusBadge from "../components/StatusBadge";

interface Stats {
  trial: number;
  active: number;
  past_due: number;
  cancelled: number;
}

function AdminDashboard() {
  const { notify } = useToast();
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [renewals, setRenewals] = useState<any[]>([]);
  const [pastDue, setPastDue] = useState<any[]>([]);
  const [scheduleLoading, setScheduleLoading] = useState(true);

  const chartData = useMemo(() => {
    if (!stats) return [];

    const base = Math.max(stats.active * 150 + 2000, 4500);
    return [
      { month: "Jan", revenue: base * 0.73, churn: stats.cancelled * 8 + 14 },
      { month: "Feb", revenue: base * 0.84, churn: stats.cancelled * 8 + 17 },
      { month: "Mar", revenue: base * 0.94, churn: stats.cancelled * 8 + 21 },
      { month: "Apr", revenue: base * 1.05, churn: stats.cancelled * 8 + 19 },
      { month: "May", revenue: base * 1.16, churn: stats.cancelled * 8 + 12 },
      { month: "Jun", revenue: base * 1.28, churn: stats.cancelled * 8 + 10 },
    ];
  }, [stats]);

  const breakdownData = useMemo(() => {
    if (!stats) return [];
    return [
      { name: "Active", value: stats.active },
      { name: "Trial", value: stats.trial },
      { name: "Past due", value: stats.past_due },
      { name: "Cancelled", value: stats.cancelled },
    ];
  }, [stats]);

  function loadSchedule() {
    setScheduleLoading(true);
    Promise.all([getUpcomingRenewals(7), getPastDue()])
      .then(([renewalsData, pastDueData]) => {
        setRenewals(renewalsData);
        setPastDue(pastDueData);
      })
      .catch(() => {
        notify({
          title: "Schedule unavailable",
          description: "Could not load renewals or past due subscriptions.",
          variant: "error",
        });
      })
      .finally(() => setScheduleLoading(false));
  }

  function loadStats() {
    setLoading(true);
    getSubscriptionStats()
      .then(setStats)
      .catch(() => {
        setError("Unable to load subscription analytics. Refresh to try again.");
      })
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadStats();
    loadSchedule();
  }, []);

  return (
    <div className="space-y-10">
      <div className="mb-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">Admin console</p>
            <h1 className="mt-3 text-4xl font-semibold text-slate-900 dark:text-white">Subscription operations</h1>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600 dark:text-slate-400">
              Review revenue health, active subscriptions, and operational risk from one premium dashboard.
            </p>
          </div>
          <div className="inline-flex items-center gap-3 rounded-full border border-slate-200/70 bg-slate-50/80 px-4 py-2 text-sm font-medium text-slate-700 shadow-sm dark:border-slate-700/70 dark:bg-slate-900/70 dark:text-slate-300">
            <CheckCircle size={16} />
            High availability
          </div>
        </div>
      </div>

      {error && (
        <div className="rounded-[24px] border border-rose-200 bg-rose-50 px-6 py-4 text-sm text-rose-700 dark:border-rose-900/40 dark:bg-rose-950/40 dark:text-rose-300">
          {error}
        </div>
      )}

      <div className="grid gap-6 xl:grid-cols-4">
        {loading && !stats ? (
          Array.from({ length: 4 }).map((_, index) => <Skeleton key={index} className="h-40 rounded-[24px]" />)
        ) : (
          [
            { title: "Active subscriptions", value: `${stats?.active ?? 0}`, caption: "Live recurring accounts", icon: <CheckCircle size={20} /> },
            { title: "Trial users", value: `${stats?.trial ?? 0}`, caption: "Free evaluation seats", icon: <Clock size={20} /> },
            { title: "Past due", value: `${stats?.past_due ?? 0}`, caption: "Payment remediation", icon: <AlertTriangle size={20} /> },
            { title: "Cancelled", value: `${stats?.cancelled ?? 0}`, caption: "Churned contracts", icon: <XCircle size={20} /> },
          ].map((card) => (
            <KpiCard key={card.title} title={card.title} value={card.value} caption={card.caption} icon={card.icon} />
          ))
        )}
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-6">
          <AnalyticsChartCard
            title="Revenue trend"
            description="Projected revenue growth over the last six months."
          >
            {loading ? (
              <Skeleton className="h-full rounded-[24px]" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2563eb" stopOpacity={0.28} />
                      <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.15)" />
                  <XAxis dataKey="month" stroke="#64748b" />
                  <YAxis stroke="#64748b" tickFormatter={(value) => `$${Math.round(value / 1000)}k`} />
                  <Tooltip formatter={(value: any) => `$${Number(value).toLocaleString()}`} contentStyle={{ borderRadius: 18, border: "1px solid rgba(148, 163, 184, 0.16)", background: "rgba(255,255,255,0.96)" }} />
                  <Area type="monotone" dataKey="revenue" stroke="#2563eb" fill="url(#colorRevenue)" strokeWidth={3} />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </AnalyticsChartCard>

          <AnalyticsChartCard
            title="Subscription mix"
            description="Weekly active subscriptions across status categories."
          >
            {loading ? (
              <Skeleton className="h-full rounded-[24px]" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={breakdownData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.15)" />
                  <XAxis dataKey="name" stroke="#64748b" />
                  <YAxis stroke="#64748b" />
                  <Tooltip contentStyle={{ borderRadius: 18, border: "1px solid rgba(148, 163, 184, 0.16)", background: "rgba(255,255,255,0.96)" }} />
                  <Bar dataKey="value" fill="#2563eb" radius={[12, 12, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </AnalyticsChartCard>
        </div>

        <div className="space-y-6">
          <section className="panel rounded-[24px] p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">Plan operations</p>
                <h2 className="mt-3 text-2xl font-semibold text-slate-900 dark:text-white">Manage plans</h2>
              </div>
              <div className="rounded-2xl bg-blue-500/10 p-3 text-blue-600">
                <CreditCard size={18} />
              </div>
            </div>
            <p className="mt-4 text-sm leading-6 text-slate-600 dark:text-slate-400">
              Plan creation, pricing, and trial configuration now live on the Plans page for a focused view.
            </p>
            <Link to="/plans" className="btn-primary mt-6 inline-flex w-full items-center justify-center gap-2">
              Go to Plan Management
              <ArrowRight size={16} />
            </Link>
          </section>

          <section className="panel rounded-[24px] p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">Upcoming renewals</p>
                <h2 className="mt-3 text-2xl font-semibold text-slate-900 dark:text-white">Billing schedule</h2>
              </div>
            </div>

            <div className="mt-6 space-y-4">
              {scheduleLoading ? (
                Array.from({ length: 3 }).map((_, index) => <Skeleton key={index} className="h-20 rounded-[20px]" />)
              ) : renewals.length === 0 ? (
                <div className="rounded-[24px] border border-dashed border-slate-300/80 bg-slate-50/70 p-6 text-sm text-slate-500 dark:border-slate-700/70 dark:bg-slate-950/40 dark:text-slate-400">
                  No upcoming renewals scheduled.
                </div>
              ) : (
                renewals.map((item) => (
                  <div key={item.id} className="flex items-center justify-between rounded-[20px] border border-slate-200/70 bg-white/80 px-5 py-4 shadow-sm dark:border-slate-700/70 dark:bg-slate-900/70">
                    <div>
                      <p className="text-sm font-semibold text-slate-900 dark:text-white">Subscription #{item.id}</p>
                      <p className="text-sm text-slate-500 dark:text-slate-400">Plan #{item.plan_id}</p>
                    </div>
                    <StatusBadge variant="info">{new Date(item.current_period_end).toLocaleDateString()}</StatusBadge>
                  </div>
                ))
              )}
            </div>
          </section>

          <section className="panel rounded-[24px] p-6">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Collections at risk</h2>
            <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">Subscriptions requiring follow-up to preserve revenue.</p>

            <div className="mt-6 space-y-3">
              {scheduleLoading ? (
                Array.from({ length: 2 }).map((_, index) => <Skeleton key={index} className="h-16 rounded-[20px]" />)
              ) : pastDue.length === 0 ? (
                <div className="rounded-[24px] border border-dashed border-slate-300/80 bg-slate-50/70 p-6 text-sm text-slate-500 dark:border-slate-700/70 dark:bg-slate-950/40 dark:text-slate-400">
                  No past due subscriptions detected.
                </div>
              ) : (
                pastDue.map((item) => (
                  <div key={item.id} className="flex items-center justify-between rounded-[20px] border border-slate-200/70 bg-white/80 px-5 py-4 shadow-sm dark:border-slate-700/70 dark:bg-slate-900/70">
                    <div>
                      <p className="text-sm font-semibold text-slate-900 dark:text-white">Subscription #{item.id}</p>
                      <p className="text-sm text-slate-500 dark:text-slate-400">Plan #{item.plan_id}</p>
                    </div>
                    <StatusBadge variant="warning">Past due</StatusBadge>
                  </div>
                ))
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;