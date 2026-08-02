import { useMemo, useState } from "react";
import { FilePlus, Trash2, Search, ReceiptText, Sparkles } from "lucide-react";
import PageHeader from "../components/PageHeader";
import Card from "../components/common/Card";
import AppShell from "../components/layout/AppShell";
import DataTable from "../components/table/DataTable";
import { useToast } from "../components/ToastProvider";
import EmptyState from "../components/EmptyState";
import RoleGuard from "../components/RoleGuard";
import { useAuth } from "../contexts/AuthContext";

interface Invoice {
  id: number;
  customer: string;
  amount: number;
  status: string;
  date: string;
}

function Invoices() {
  const { role } = useAuth();
  const user: any = JSON.parse(localStorage.getItem("user") || "{}");
  const [invoices, setInvoices] = useState<Invoice[]>(user.invoicesList || []);
  const [customer, setCustomer] = useState("");
  const [amount, setAmount] = useState("");
  const [status, setStatus] = useState("Pending");
  const [search, setSearch] = useState("");
  const { notify } = useToast();

  function persist(updated: Invoice[]) {
    const totalRevenue = updated.filter((item) => item.status === "Paid").reduce((sum, item) => sum + Number(item.amount), 0);
    setInvoices(updated);
    localStorage.setItem(
      "user",
      JSON.stringify({
        ...user,
        invoicesList: updated,
        invoices: updated.length,
        revenue: `$${totalRevenue}`,
      })
    );
  }

  function createInvoice() {
    if (!customer.trim() || !amount.trim()) {
      notify({
        title: "Invoice missing data",
        description: "Provide both customer and amount to create an invoice.",
        variant: "error",
      });
      return;
    }

    const newInvoice: Invoice = {
      id: Date.now(),
      customer: customer.trim(),
      amount: Number(amount),
      status,
      date: new Date().toLocaleDateString(),
    };

    const updated = [newInvoice, ...invoices];
    persist(updated);
    setCustomer("");
    setAmount("");
    setStatus("Pending");

    notify({
      title: "Invoice created",
      description: `Invoice for ${newInvoice.customer} was added successfully.`,
      variant: "success",
    });
  }

  function deleteInvoice(id: number) {
    const updated = invoices.filter((invoice) => invoice.id !== id);
    persist(updated);
    notify({
      title: "Invoice removed",
      description: "The invoice has been deleted from the ledger.",
      variant: "info",
    });
  }

  const filteredInvoices = useMemo(
    () => invoices.filter((invoice) => invoice.customer.toLowerCase().includes(search.toLowerCase()) || invoice.status.toLowerCase().includes(search.toLowerCase())),
    [invoices, search]
  );

  // Customers only get a read-only view - no delete/manage action column
  const columns = useMemo(() => {
    const base: any[] = [
      { key: 'customer', title: 'Customer', sortable: true },
      { key: 'amount', title: 'Amount', sortable: true, render: (invoice: Invoice) => `$${invoice.amount.toFixed(2)}` },
      { key: 'status', title: 'Status', sortable: true },
      { key: 'date', title: 'Date', sortable: true },
    ];

    if (role === "admin") {
      base.push({
        key: 'actions',
        title: 'Actions',
        render: (invoice: Invoice) => (
          <button
            type="button"
            onClick={() => deleteInvoice(invoice.id)}
            className="inline-flex items-center gap-2 rounded-full border border-red-200 bg-red-50 px-3 py-2 text-sm font-semibold text-red-700 transition hover:bg-red-100 dark:border-red-900/40 dark:bg-red-950/40 dark:text-red-300"
          >
            <Trash2 size={16} />
            Delete
          </button>
        ),
      });
    }

    return base;
  }, [role, invoices]);

  return (
    <AppShell>
      <div className="fade-in">
      <PageHeader
        eyebrow="Billing"
        title={role === "admin" ? "Invoices" : "My Invoices"}
        description={
          role === "admin"
            ? "Create polished invoices and keep billing activity visible across your operations."
            : "Review your invoice history and payment status."
        }
        action={<span className="inline-flex items-center gap-2"><ReceiptText size={16} />{invoices.length} records</span>}
      />

      {/* Only admins can issue new invoices */}
      <RoleGuard allow={["admin"]}>
        <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
          <Card className="space-y-6">
            <div className="flex items-center gap-3">
              <div className="rounded-2xl bg-blue-500/10 p-3 text-blue-600">
                <FilePlus size={20} />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-slate-900 dark:text-white">Create invoice</h2>
                <p className="text-sm text-slate-600 dark:text-slate-400">Issue clean invoices with full status context.</p>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <input
                value={customer}
                onChange={(e) => setCustomer(e.target.value)}
                placeholder="Customer Name"
                className="input-field"
                aria-label="Customer name"
              />
              <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="Amount"
                className="input-field"
                aria-label="Invoice amount"
              />
              <select value={status} onChange={(e) => setStatus(e.target.value)} className="input-field" aria-label="Invoice status">
                <option>Pending</option>
                <option>Paid</option>
                <option>Overdue</option>
              </select>
            </div>

            <button onClick={createInvoice} className="btn-primary">
              <FilePlus size={18} />
              Create Invoice
            </button>
          </Card>

          <Card className="space-y-4">
            <div className="inline-flex items-center gap-2 rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-amber-700 dark:border-amber-900/40 dark:bg-amber-500/10 dark:text-amber-300">
              <Sparkles size={14} />
              Revenue pulse
            </div>
            <div className="rounded-2xl border border-slate-200/70 bg-slate-50/80 p-5 dark:border-slate-700/70 dark:bg-slate-950/50">
              <p className="text-sm text-slate-600 dark:text-slate-400">A quick snapshot of collected revenue from your paid invoices.</p>
              <div className="mt-4 flex items-end justify-between">
                <div>
                  <p className="text-3xl font-semibold text-slate-900 dark:text-white">${invoices.filter((invoice) => invoice.status === "Paid").reduce((sum, invoice) => sum + Number(invoice.amount), 0).toFixed(2)}</p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">Collected revenue</p>
                </div>
                <div className="rounded-full bg-emerald-500/10 px-3 py-1 text-sm font-medium text-emerald-600 dark:text-emerald-400">Healthy flow</div>
              </div>
            </div>
          </Card>
        </div>
      </RoleGuard>

      <Card className="mt-6">
        <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white">Invoice list</h2>
            <p className="text-sm text-slate-600 dark:text-slate-400">Find invoices quickly and take action on overdue or pending payments.</p>
          </div>
          <div className="flex items-center gap-2 rounded-2xl border border-slate-200/70 bg-white/70 px-3 py-2 shadow-sm dark:border-slate-700/70 dark:bg-slate-900/70">
            <Search size={18} className="text-slate-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search invoices"
              className="w-40 border-0 bg-transparent outline-none"
              aria-label="Search invoices"
            />
          </div>
        </div>

        {filteredInvoices.length === 0 ? (
          <EmptyState
            title="No invoices found"
            description={
              role === "admin"
                ? "Create your first invoice to start tracking payment progress and revenue performance."
                : "You don't have any invoices yet. Subscribe to a plan to get started."
            }
            primaryAction={
              role === "admin"
                ? { label: "New invoice", path: "/invoices" }
                : { label: "Browse plans", path: "/plans" }
            }
            icon={<ReceiptText size={24} />}
          />
        ) : (
          <DataTable
            columns={columns}
            data={filteredInvoices}
            searchable
            pageSize={10}
          />
        )}
      </Card>
      </div>
    </AppShell>
  );
}

export default Invoices;