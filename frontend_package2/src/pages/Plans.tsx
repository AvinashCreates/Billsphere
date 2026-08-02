import { useEffect, useMemo, useState } from "react";
import { Crown, Sparkles, CheckCircle2, Pencil, Trash2, Users } from "lucide-react";
import {
  getPlans,
  subscribeToPlan,
  updatePlan,
  deletePlan,
  getAllSubscriptions,
  getMySubscriptions,
  getCurrentUser,
} from "../assets/services/api";
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

interface AdminSubscriptionRow {
  id: number;
  status: string;
  trial_ends_at: string | null;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  customer_id: number;
  customer_name: string | null;
  customer_email: string | null;
  plan_id: number;
  plan_name: string | null;
  plan_price: number | null;
}

interface MySubscription {
  id: number;
  plan_id: number;
  status: string;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
}

const statusLabel: Record<string, string> = {
  trial: "Trial session",
  active: "Paid",
  past_due: "Unpaid",
  cancelled: "Cancelled",
};

const statusBadgeClass: Record<string, string> = {
  trial: "bg-blue-50 text-blue-600",
  active: "bg-emerald-50 text-emerald-600",
  past_due: "bg-red-50 text-red-600",
  cancelled: "bg-slate-100 text-slate-500",
};

// green -> amber -> red as the deadline approaches
function deadlineStyle(periodEnd: string) {
  const daysLeft = Math.ceil((new Date(periodEnd).getTime() - Date.now()) / (1000 * 60 * 60 * 24));

  if (daysLeft <= 0) {
    return { label: "Overdue", className: "bg-red-100 text-red-700 border border-red-200" };
  }
  if (daysLeft <= 3) {
    return { label: `${daysLeft} day${daysLeft === 1 ? "" : "s"} left`, className: "bg-red-50 text-red-600 border border-red-200" };
  }
  if (daysLeft <= 7) {
    return { label: `${daysLeft} days left`, className: "bg-amber-50 text-amber-600 border border-amber-200" };
  }
  return { label: `${daysLeft} days left`, className: "bg-emerald-50 text-emerald-600 border border-emerald-200" };
}

function Plans() {
  const [role, setRole] = useState<string | null>(null);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [subscribingId, setSubscribingId] = useState<number | null>(null);
  const { notify } = useToast();

  // admin-only state
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState({ name: "", price: "", billing_interval: "monthly", trial_period_days: "0" });
  const [savingEdit, setSavingEdit] = useState(false);
  const [subscriptions, setSubscriptions] = useState<AdminSubscriptionRow[]>([]);
  const [subsLoading, setSubsLoading] = useState(true);

  // customer-only state
  const [mySub, setMySub] = useState<MySubscription | null>(null);

  useEffect(() => {
    getCurrentUser()
      .then((user) => setRole(user.role))
      .catch(() => setRole("customer"));
    loadPlans();
  }, []);

  useEffect(() => {
    if (role === "admin") {
      loadSubscriptions();
    } else if (role === "customer") {
      loadMySubscription();
    }
  }, [role]);

  async function loadPlans() {
    try {
      setLoading(true);
      const data = await getPlans();
      setPlans(data);
    } catch (err: any) {
      setError(err.message || "Could not load plans");
      notify({ title: "Plan load failed", description: err.message || "Unable to fetch plan offerings.", variant: "error" });
    } finally {
      setLoading(false);
    }
  }

  function loadSubscriptions() {
    setSubsLoading(true);
    getAllSubscriptions()
      .then(setSubscriptions)
      .catch((err: any) => {
        notify({ title: "Could not load customers", description: err.message || "Failed to fetch subscriptions.", variant: "error" });
      })
      .finally(() => setSubsLoading(false));
  }

  function loadMySubscription() {
    getMySubscriptions()
      .then((subs: MySubscription[]) => {
        const active = subs.find((s) => s.status === "active" || s.status === "trial" || s.status === "past_due");
        setMySub(active || null);
      })
      .catch(() => {});
  }

  async function choosePlan(plan: Plan) {
    setError("");
    setSubscribingId(plan.id);
    try {
      await subscribeToPlan(plan.id);
      notify({ title: "Plan activated", description: `You are now subscribed to the ${plan.name} plan.`, variant: "success" });
      loadMySubscription();
    } catch (err: any) {
      setError(err.message || "Could not subscribe to this plan");
      notify({ title: "Subscription failed", description: err.message || "Unable to activate this plan.", variant: "error" });
    } finally {
      setSubscribingId(null);
    }
  }

  function startEdit(plan: Plan) {
    setEditingId(plan.id);
    setEditForm({
      name: plan.name,
      price: String(plan.price),
      billing_interval: plan.billing_interval,
      trial_period_days: String(plan.trial_period_days ?? 0),
    });
  }

  async function saveEdit(planId: number) {
    setSavingEdit(true);
    try {
      await updatePlan(planId, {
        name: editForm.name,
        price: parseFloat(editForm.price),
        billing_interval: editForm.billing_interval,
        trial_period_days: parseInt(editForm.trial_period_days || "0", 10),
      });
      notify({ title: "Plan updated", description: `${editForm.name} was updated.`, variant: "success" });
      setEditingId(null);
      loadPlans();
    } catch (err: any) {
      notify({ title: "Update failed", description: err.message || "Could not update plan.", variant: "error" });
    } finally {
      setSavingEdit(false);
    }
  }

  async function removePlan(plan: Plan) {
    if (!confirm(`Delete the ${plan.name} plan?`)) return;
    try {
      await deletePlan(plan.id);
      notify({ title: "Plan deleted", description: `${plan.name} was removed.`, variant: "info" });
      loadPlans();
    } catch (err: any) {
      notify({ title: "Delete failed", description: err.message || "Could not delete plan.", variant: "error" });
    }
  }

  const subscriptionColumns = useMemo(
    () => [
      { key: "customer_name", title: "Customer", render: (r: AdminSubscriptionRow) => r.customer_name || "—" },
      { key: "customer_email", title: "Email", render: (r: AdminSubscriptionRow) => r.customer_email || "—" },
      { key: "plan_name", title: "Plan", render: (r: AdminSubscriptionRow) => r.plan_name || `#${r.plan_id}` },
      {
        key: "status",
        title: "Status",
        render: (r: AdminSubscriptionRow) => (
          <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusBadgeClass[r.status] || "bg-slate-100 text-slate-600"}`}>
            {statusLabel[r.status] || r.status}
          </span>
        ),
      },
      {
        key: "current_period_end",
        title: "Renews / Due",
        render: (r: AdminSubscriptionRow) => new Date(r.current_period_end).toLocaleDateString(),
      },
    ],
    []
  );

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

        {/* Active plan card — customers only */}
        {role === "customer" && mySub && (
          <Card className="mb-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Active plan</p>
                <h2 className="mt-2 text-2xl font-semibold text-slate-900 dark:text-white">
                  {plans.find((p) => p.id === mySub.plan_id)?.name || `Plan #${mySub.plan_id}`}
                </h2>
                <p className="mt-1 text-sm text-slate-500">
                  Status: <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${statusBadgeClass[mySub.status]}`}>{statusLabel[mySub.status]}</span>
                </p>
              </div>
              <div className="text-right">
                {(() => {
                  const d = deadlineStyle(mySub.current_period_end);
                  return <span className={`inline-block rounded-full px-4 py-2 text-sm font-semibold ${d.className}`}>{d.label}</span>;
                })()}
                <p className="mt-2 text-sm text-slate-500">
                  Pay again by <strong>{new Date(mySub.current_period_end).toLocaleDateString()}</strong>
                </p>
              </div>
            </div>
          </Card>
        )}

        {loading ? (
          <div className="grid gap-6 md:grid-cols-3">
            {Array.from({ length: 3 }).map((_, index) => (
              <Card key={index} className="overflow-hidden"><Skeleton className="h-72 rounded-[24px]" /></Card>
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
                {editingId === plan.id ? (
                  <div className="space-y-3">
                    <input
                      className="input-field"
                      value={editForm.name}
                      onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                      placeholder="Plan name"
                    />
                    <input
                      className="input-field"
                      type="number"
                      step="0.01"
                      value={editForm.price}
                      onChange={(e) => setEditForm({ ...editForm, price: e.target.value })}
                      placeholder="Price"
                    />
                    <select
                      className="input-field"
                      value={editForm.billing_interval}
                      onChange={(e) => setEditForm({ ...editForm, billing_interval: e.target.value })}
                    >
                      <option value="monthly">Monthly</option>
                      <option value="yearly">Yearly</option>
                    </select>
                    <input
                      className="input-field"
                      type="number"
                      min="0"
                      value={editForm.trial_period_days}
                      onChange={(e) => setEditForm({ ...editForm, trial_period_days: e.target.value })}
                      placeholder="Trial days"
                    />
                    <div className="flex gap-2">
                      <button className="btn-primary flex-1" disabled={savingEdit} onClick={() => saveEdit(plan.id)}>
                        {savingEdit ? "Saving..." : "Save"}
                      </button>
                      <button className="btn-ghost flex-1" onClick={() => setEditingId(null)}>Cancel</button>
                    </div>
                  </div>
                ) : (
                  <>
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

                    {role === "admin" ? (
                      <div className="mt-8 flex gap-3">
                        <button onClick={() => startEdit(plan)} className="btn-ghost flex-1">
                          <Pencil size={16} /> Edit
                        </button>
                        <button
                          onClick={() => removePlan(plan)}
                          className="flex-1 inline-flex items-center justify-center gap-2 rounded-full border border-red-200 bg-red-50 px-3 py-2 text-sm font-semibold text-red-700 transition hover:bg-red-100"
                        >
                          <Trash2 size={16} /> Delete
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => choosePlan(plan)}
                        disabled={subscribingId === plan.id}
                        className="btn-primary mt-8 w-full"
                      >
                        {subscribingId === plan.id ? "Subscribing..." : "Choose Plan"}
                      </button>
                    )}
                  </>
                )}
              </Card>
            ))}
          </div>
        )}

        {/* Admin: customers-on-plans table */}
        {role === "admin" && (
          <div className="mt-8">
            <Card title="Customers on plans">
              <div className="mb-4 flex items-center gap-2 text-sm text-slate-500">
                <Users size={16} />
                {subscriptions.length} subscription{subscriptions.length === 1 ? "" : "s"}
              </div>
              {subsLoading ? (
                <Skeleton className="h-40 rounded-[20px]" />
              ) : subscriptions.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-slate-300/80 p-6 text-sm text-slate-500">
                  No one has subscribed to a plan yet.
                </div>
              ) : (
                <DataTable columns={subscriptionColumns} data={subscriptions} searchable pageSize={10} />
              )}
            </Card>
          </div>
        )}
      </div>
    </AppShell>
  );
}

export default Plans;