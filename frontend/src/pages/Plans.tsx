import { useEffect, useState } from "react";
import { Crown, Sparkles, CheckCircle2, Pencil, Trash2, Power, Download, Plus } from "lucide-react";
import * as XLSX from "xlsx";
import { getPlans, getAdminPlans, createPlan, updatePlan, setPlanStatus, deletePlan } from "../assets/services/api";
import { useAuth } from "../contexts/AuthContext";
import PageHeader from "../components/PageHeader";
import Card from "../components/common/Card";
import Skeleton from "../components/Skeleton";
import EmptyState from "../components/EmptyState";
import { useToast } from "../components/ToastProvider";
import AppShell from "../components/layout/AppShell";
import DataTable from "../components/table/DataTable";
import StatusBadge from "../components/StatusBadge";
import ChoosePlanModal from "../components/ChoosePlanModal";

interface Plan {
  id: number;
  name: string;
  price: number;
  billing_interval: string;
  trial_period_days: number;
  status: "active" | "inactive" | "deleted";
  created_at: string;
  deleted_at: string | null;
}

const emptyForm = { name: "", price: "", billing_interval: "monthly", trial_period_days: "0" };

function Plans() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";
  const { notify } = useToast();

  // ---- Customer-facing state ----
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedPlan, setSelectedPlan] = useState("");
  const [modalPlan, setModalPlan] = useState<Plan | null>(null);

  // ---- Admin-only state ----
  const [adminPlans, setAdminPlans] = useState<Plan[]>([]);
  const [adminLoading, setAdminLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [intervalFilter, setIntervalFilter] = useState<string>("");
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (isAdmin) {
      loadAdminPlans();
    } else {
      loadCustomerPlans();
    }
  }, [isAdmin]);

  useEffect(() => {
    if (isAdmin) loadAdminPlans();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter, intervalFilter]);

  async function loadCustomerPlans() {
    try {
      setLoading(true);
      const data = await getPlans();
      setPlans(data);
    } catch (err: any) {
      setError(err.message || "Could not load plans");
      notify({ title: "Plan load failed", description: err.message, variant: "error" });
    } finally {
      setLoading(false);
    }
  }

  async function loadAdminPlans() {
    try {
      setAdminLoading(true);
      const data = await getAdminPlans({
        status: statusFilter || undefined,
        billing_interval: intervalFilter || undefined,
      });
      setAdminPlans(data);
    } catch (err: any) {
      notify({ title: "Plan load failed", description: err.message, variant: "error" });
    } finally {
      setAdminLoading(false);
    }
  }

  function handleChange(e: any) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  function startEdit(plan: Plan) {
    setEditingId(plan.id);
    setForm({
      name: plan.name,
      price: String(plan.price),
      billing_interval: plan.billing_interval,
      trial_period_days: String(plan.trial_period_days),
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function cancelEdit() {
    setEditingId(null);
    setForm(emptyForm);
  }

  async function handleSubmit(e: any) {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        name: form.name,
        price: parseFloat(form.price),
        billing_interval: form.billing_interval,
        trial_period_days: parseInt(form.trial_period_days || "0", 10),
      };

      if (editingId) {
        await updatePlan(editingId, payload);
        notify({ title: "Plan updated", description: `${form.name} was updated.`, variant: "success" });
      } else {
        await createPlan(payload);
        notify({ title: "Plan created", description: `The ${form.name} plan is now available.`, variant: "success" });
      }

      cancelEdit();
      loadAdminPlans();
    } catch (err: any) {
      notify({ title: editingId ? "Update failed" : "Plan creation failed", description: err.message, variant: "error" });
    } finally {
      setSaving(false);
    }
  }

  async function handleToggleStatus(plan: Plan) {
    const next = plan.status === "active" ? "inactive" : "active";
    try {
      await setPlanStatus(plan.id, next);
      notify({ title: "Status updated", description: `${plan.name} is now ${next}.`, variant: "success" });
      loadAdminPlans();
    } catch (err: any) {
      notify({ title: "Could not change status", description: err.message, variant: "error" });
    }
  }

  async function handleDelete(plan: Plan) {
    if (!window.confirm(`Delete "${plan.name}"? It will be kept in history but hidden from customers.`)) return;
    try {
      await deletePlan(plan.id);
      notify({ title: "Plan deleted", description: `${plan.name} was moved to deleted plans.`, variant: "success" });
      loadAdminPlans();
    } catch (err: any) {
      notify({ title: "Could not delete plan", description: err.message, variant: "error" });
    }
  }

  function exportToExcel() {
    const rows = adminPlans.map((p) => ({
      ID: p.id,
      Name: p.name,
      Price: p.price,
      "Billing Interval": p.billing_interval,
      "Trial Days": p.trial_period_days,
      Status: p.status,
      "Created At": new Date(p.created_at).toLocaleString(),
      "Deleted At": p.deleted_at ? new Date(p.deleted_at).toLocaleString() : "-",
    }));
    const worksheet = XLSX.utils.json_to_sheet(rows);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Plans");
    XLSX.writeFile(workbook, `billsphere-plans-${new Date().toISOString().slice(0, 10)}.xlsx`);
  }

  const statusVariant = (status: string): "success" | "warning" | "danger" | "info" => {
    if (status === "active") return "success";
    if (status === "inactive") return "warning";
    return "danger"; // deleted
  };

  // ---- ADMIN VIEW ----
  if (isAdmin) {
    return (
      <AppShell>
        <div className="fade-in space-y-8">
          <PageHeader
            eyebrow="Billing · Admin"
            title="Plan management"
            description="Create, edit, deactivate, or delete plans. Deleted and inactive plans stay visible here for history and reporting."
            action={<span className="inline-flex items-center gap-2"><Crown size={16} />Admin console</span>}
          />

          <Card title={editingId ? "Edit plan" : "Create a new plan"}>
            <form onSubmit={handleSubmit} className="mt-2 space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <input type="text" name="name" placeholder="Plan name" required value={form.name} onChange={handleChange} className="input-field" />
                <input type="number" name="price" placeholder="Price" required step="0.01" value={form.price} onChange={handleChange} className="input-field" />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <select name="billing_interval" value={form.billing_interval} onChange={handleChange} className="input-field">
                  <option value="monthly">Monthly</option>
                  <option value="yearly">Yearly</option>
                </select>
                <input type="number" name="trial_period_days" placeholder="Trial days" min="0" value={form.trial_period_days} onChange={handleChange} className="input-field" />
              </div>
              <div className="flex gap-3">
                <button type="submit" disabled={saving} className="btn-primary flex-1 inline-flex items-center justify-center gap-2">
                  {editingId ? <Pencil size={16} /> : <Plus size={16} />}
                  {saving ? "Saving..." : editingId ? "Save changes" : "Create plan"}
                </button>
                {editingId && (
                  <button type="button" onClick={cancelEdit} className="btn-ghost">
                    Cancel
                  </button>
                )}
              </div>
            </form>
          </Card>

          <Card title="All plans">
            <div className="mb-6 flex flex-wrap items-center gap-3">
              <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="input-field w-auto">
                <option value="">All statuses</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="deleted">Deleted</option>
              </select>
              <select value={intervalFilter} onChange={(e) => setIntervalFilter(e.target.value)} className="input-field w-auto">
                <option value="">All intervals</option>
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
              </select>
              <button onClick={exportToExcel} className="btn-ghost ml-auto inline-flex items-center gap-2">
                <Download size={16} />
                Export to Excel
              </button>
            </div>

            {adminLoading ? (
              <Skeleton className="h-64 rounded-[24px]" />
            ) : adminPlans.length === 0 ? (
              <EmptyState
                title="No plans match these filters"
                description="Try adjusting the status or interval filter."
                icon={<Crown size={24} />}
              />
            ) : (
              <DataTable
                columns={[
                  { key: "id", title: "ID" },
                  { key: "name", title: "Name" },
                  { key: "price", title: "Price", render: (p: Plan) => `$${p.price}` },
                  { key: "interval", title: "Interval", render: (p: Plan) => p.billing_interval },
                  { key: "trial", title: "Trial (days)", render: (p: Plan) => p.trial_period_days ?? 0 },
                  { key: "status", title: "Status", render: (p: Plan) => <StatusBadge variant={statusVariant(p.status)}>{p.status}</StatusBadge> },
                  {
                    key: "actions",
                    title: "Actions",
                    render: (p: Plan) => (
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => startEdit(p)}
                          disabled={p.status === "deleted"}
                          className="btn-ghost inline-flex items-center gap-1 disabled:opacity-40"
                          title="Edit"
                        >
                          <Pencil size={14} />
                        </button>
                        <button
                          onClick={() => handleToggleStatus(p)}
                          disabled={p.status === "deleted"}
                          className="btn-ghost inline-flex items-center gap-1 disabled:opacity-40"
                          title={p.status === "active" ? "Deactivate" : "Activate"}
                        >
                          <Power size={14} />
                        </button>
                        <button
                          onClick={() => handleDelete(p)}
                          disabled={p.status === "deleted"}
                          className="btn-ghost inline-flex items-center gap-1 text-red-600 disabled:opacity-40"
                          title="Delete"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    ),
                  },
                ]}
                data={adminPlans}
              />
            )}
          </Card>
        </div>
      </AppShell>
    );
  }

  // ---- CUSTOMER VIEW ----
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

                <button onClick={() => setModalPlan(plan)} className="btn-primary mt-8 w-full">
                  Choose Plan
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

        {modalPlan && (
          <ChoosePlanModal
            plan={modalPlan}
            onClose={() => setModalPlan(null)}
            onSuccess={(planName) => {
              setSelectedPlan(planName);
              notify({ title: "Plan updated", description: `${planName} is now set up on your account.`, variant: "success" });
            }}
          />
        )}
      </div>
    </AppShell>
  );
}

export default Plans;