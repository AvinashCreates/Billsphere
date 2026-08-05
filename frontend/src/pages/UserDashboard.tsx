import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { CreditCard, CheckCircle, Clock, XCircle, Hourglass, ArrowUpCircle } from "lucide-react";
import {
  getMySubscriptions,
  cancelSubscription,
  renewSubscription,
  extendSubscription,
  convertTrialToPaid,
} from "../assets/services/api";
import { useToast } from "../components/ToastProvider";
import EmptyState from "../components/EmptyState";
import Skeleton from "../components/Skeleton";
import StatusBadge from "../components/StatusBadge";

interface Subscription {
  id: number;
  plan_id: number;
  plan_name: string | null;
  billing_interval: string | null;
  price: number | null;
  status: "active" | "trial" | "pending" | "past_due" | "cancelled";
  trial_ends_at: string | null;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
}

function daysBetween(a: Date, b: Date) {
  return Math.max(0, Math.ceil((a.getTime() - b.getTime()) / (1000 * 60 * 60 * 24)));
}

function UserDashboard() {
  const { notify } = useToast();
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionId, setActionId] = useState<number | null>(null);

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

  const active = useMemo(() => subscriptions.filter((s) => s.status === "active"), [subscriptions]);
  const trial = useMemo(() => subscriptions.filter((s) => s.status === "trial"), [subscriptions]);
  const pending = useMemo(() => subscriptions.filter((s) => s.status === "pending"), [subscriptions]);
  const pastDue = useMemo(() => subscriptions.filter((s) => s.status === "past_due"), [subscriptions]);

  const hasAnything = subscriptions.some((s) => s.status !== "cancelled");

  async function withAction(id: number, fn: () => Promise<any>, successMsg: string) {
    setActionId(id);
    try {
      await fn();
      notify({ title: "Done", description: successMsg, variant: "success" });
      load();
    } catch (err: any) {
      notify({ title: "Action failed", description: err.message || "Something went wrong.", variant: "error" });
    } finally {
      setActionId(null);
    }
  }

  return (
    <div className="space-y-10">
      <div className="mb-2">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">Subscriber dashboard</p>
        <h1 className="mt-3 text-4xl font-semibold text-slate-900 dark:text-white">Your subscriptions</h1>
        <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600 dark:text-slate-400">
          Everything you're subscribed to, queued, trialing, or need to renew — in one place.
        </p>
      </div>

      {loading && (
        <div className="grid gap-6 lg:grid-cols-2">
          <Skeleton className="h-48 rounded-[24px]" />
          <Skeleton className="h-48 rounded-[24px]" />
        </div>
      )}

      {!loading && !hasAnything && (
        <EmptyState
          title="No active plan found"
          description="Choose a plan to get started."
          primaryAction={{ label: "Explore plans", path: "/plans" }}
          icon={<CreditCard size={24} />}
        />
      )}

      {!loading && hasAnything && (
        <div className="space-y-10">
          {active.length > 0 && (
            <SectionBlock
              icon={<CheckCircle size={18} />}
              title="Active Plans"
              accent="text-emerald-600"
            >
              <div className="grid gap-6 md:grid-cols-2">
                {active.map((sub) => (
                  <ActiveCard
                    key={sub.id}
                    sub={sub}
                    busy={actionId === sub.id}
                    onCancelImmediate={() =>
                      withAction(sub.id, () => cancelSubscription(sub.id, true), `${sub.plan_name} cancelled immediately.`)
                    }
                    onCancelAtPeriodEnd={() =>
                      withAction(sub.id, () => cancelSubscription(sub.id, false), `${sub.plan_name} will cancel at period end.`)
                    }
                    onExtend={() =>
                      withAction(sub.id, () => extendSubscription(sub.id), `${sub.plan_name} extended by one more cycle.`)
                    }
                  />
                ))}
              </div>
            </SectionBlock>
          )}

          {trial.length > 0 && (
            <SectionBlock icon={<Clock size={18} />} title="Trial Plans" accent="text-blue-600">
              <div className="grid gap-6 md:grid-cols-2">
                {trial.map((sub) => (
                  <TrialCard
                    key={sub.id}
                    sub={sub}
                    busy={actionId === sub.id}
                    onContinueToPay={() =>
                      withAction(sub.id, () => convertTrialToPaid(sub.id), `${sub.plan_name} is now a paid plan.`)
                    }
                  />
                ))}
              </div>
            </SectionBlock>
          )}

          {pending.length > 0 && (
            <SectionBlock icon={<Hourglass size={18} />} title="Pending Plans" accent="text-indigo-600">
              <div className="grid gap-6 md:grid-cols-2">
                {pending.map((sub) => (
                  <PendingCard key={sub.id} sub={sub} />
                ))}
              </div>
            </SectionBlock>
          )}

          {pastDue.length > 0 && (
            <SectionBlock icon={<XCircle size={18} />} title="Past Due Plans" accent="text-rose-600">
              <div className="grid gap-6 md:grid-cols-2">
                {pastDue.map((sub) => (
                  <PastDueCard
                    key={sub.id}
                    sub={sub}
                    busy={actionId === sub.id}
                    onRenew={() => withAction(sub.id, () => renewSubscription(sub.id), `${sub.plan_name} renewed.`)}
                  />
                ))}
              </div>
            </SectionBlock>
          )}

          <div className="flex justify-end">
            <Link to="/plans" className="btn-ghost inline-flex items-center gap-2">
              <ArrowUpCircle size={16} />
              Explore more plans
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

function SectionBlock({ icon, title, accent, children }: { icon: React.ReactNode; title: string; accent: string; children: React.ReactNode }) {
  return (
    <section>
      <div className={`mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.2em] ${accent}`}>
        {icon}
        {title}
      </div>
      {children}
    </section>
  );
}

function PlanHeader({ sub, badgeVariant, badgeLabel }: { sub: Subscription; badgeVariant: "success" | "warning" | "danger" | "info" | "neutral"; badgeLabel: string }) {
  return (
    <div className="flex items-start justify-between gap-3">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">
          {sub.billing_interval || "—"}
        </p>
        <h3 className="mt-1 text-xl font-semibold text-slate-900 dark:text-white">{sub.plan_name || `Plan #${sub.plan_id}`}</h3>
      </div>
      <StatusBadge variant={badgeVariant}>{badgeLabel}</StatusBadge>
    </div>
  );
}

function ActiveCard({
  sub,
  busy,
  onCancelImmediate,
  onCancelAtPeriodEnd,
  onExtend,
}: {
  sub: Subscription;
  busy: boolean;
  onCancelImmediate: () => void;
  onCancelAtPeriodEnd: () => void;
  onExtend: () => void;
}) {
  return (
    <div className="panel rounded-[24px] p-6 shadow-sm">
      <PlanHeader sub={sub} badgeVariant="success" badgeLabel="Active" />

      <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
        <div className="rounded-2xl border border-slate-200/70 bg-slate-50/80 p-3 dark:border-slate-700/70 dark:bg-slate-950/50">
          <p className="text-xs text-slate-500 dark:text-slate-400">Started</p>
          <p className="mt-1 font-semibold text-slate-900 dark:text-white">{new Date(sub.current_period_start).toLocaleDateString()}</p>
        </div>
        <div className="rounded-2xl border border-slate-200/70 bg-slate-50/80 p-3 dark:border-slate-700/70 dark:bg-slate-950/50">
          <p className="text-xs text-slate-500 dark:text-slate-400">Renews</p>
          <p className="mt-1 font-semibold text-slate-900 dark:text-white">{new Date(sub.current_period_end).toLocaleDateString()}</p>
        </div>
      </div>

      {sub.cancel_at_period_end && (
        <div className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-2.5 text-xs text-amber-700 dark:border-amber-500/20 dark:bg-amber-500/10 dark:text-amber-300">
          Scheduled to cancel at the end of this period.
        </div>
      )}

      <div className="mt-5 flex flex-wrap gap-2">
        <button onClick={onExtend} disabled={busy} className="btn-primary text-sm px-4 py-2">
          Extend
        </button>
        {!sub.cancel_at_period_end && (
          <button onClick={onCancelAtPeriodEnd} disabled={busy} className="btn-ghost text-sm px-4 py-2">
            Cancel at period end
          </button>
        )}
        <button onClick={onCancelImmediate} disabled={busy} className="btn-ghost text-sm px-4 py-2 text-rose-600">
          Cancel immediately
        </button>
      </div>
    </div>
  );
}

function TrialCard({ sub, busy, onContinueToPay }: { sub: Subscription; busy: boolean; onContinueToPay: () => void }) {
  const daysLeft = sub.trial_ends_at ? daysBetween(new Date(sub.trial_ends_at), new Date()) : 0;

  return (
    <div className="panel rounded-[24px] p-6 shadow-sm">
      <PlanHeader sub={sub} badgeVariant="info" badgeLabel="Trial" />

      <div className="mt-5 rounded-2xl border border-blue-200/70 bg-blue-50/70 p-4 dark:border-blue-500/20 dark:bg-blue-500/10">
        <p className="text-3xl font-semibold text-blue-700 dark:text-blue-300">{daysLeft}</p>
        <p className="text-xs text-blue-700/80 dark:text-blue-300/80">
          day{daysLeft === 1 ? "" : "s"} left — trial ends {sub.trial_ends_at ? new Date(sub.trial_ends_at).toLocaleDateString() : "soon"}
        </p>
      </div>

      <button onClick={onContinueToPay} disabled={busy} className="btn-primary mt-5 w-full text-sm">
        Continue to Pay
      </button>
    </div>
  );
}

function PendingCard({ sub }: { sub: Subscription }) {
  return (
    <div className="panel rounded-[24px] p-6 shadow-sm opacity-90">
      <PlanHeader sub={sub} badgeVariant="neutral" badgeLabel="Pending" />
      <div className="mt-5 rounded-2xl border border-indigo-200/70 bg-indigo-50/70 p-4 text-sm text-indigo-700 dark:border-indigo-500/20 dark:bg-indigo-500/10 dark:text-indigo-300">
        Starts automatically on {new Date(sub.current_period_start).toLocaleDateString()}, once your current plan on this platform ends.
      </div>
    </div>
  );
}

function PastDueCard({ sub, busy, onRenew }: { sub: Subscription; busy: boolean; onRenew: () => void }) {
  return (
    <div className="panel rounded-[24px] p-6 shadow-sm border-rose-200/70 dark:border-rose-500/20">
      <PlanHeader sub={sub} badgeVariant="danger" badgeLabel="Past Due" />
      <div className="mt-5 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700 dark:border-rose-500/20 dark:bg-rose-500/10 dark:text-rose-300">
        This plan was due on {new Date(sub.current_period_end).toLocaleDateString()} and hasn't been renewed.
      </div>
      <button onClick={onRenew} disabled={busy} className="btn-primary mt-5 w-full text-sm">
        Renew now
      </button>
    </div>
  );
}

export default UserDashboard;