import { useMemo, useState, useEffect } from "react";
import { Search, UserPlus, Trash2, Users, Sparkles } from "lucide-react";
import PageHeader from "../components/PageHeader";
import Card from "../components/common/Card";
import AppShell from "../components/layout/AppShell";
import DataTable from "../components/table/DataTable";
import { useToast } from "../components/ToastProvider";
import EmptyState from "../components/EmptyState";
import { getCustomers, createCustomer as apiCreateCustomer, deleteCustomer as apiDeleteCustomer } from "../assets/services/api";

interface Customer {
  id: number;
  name: string;
  email: string;
  joined: string;
}

function Customers() {
  const user: any = JSON.parse(localStorage.getItem("user") || "{}");
  const [customers, setCustomers] = useState<Customer[]>(user.customersList || []);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [search, setSearch] = useState("");
  const { notify } = useToast();

  function persist(updated: Customer[]) {
    setCustomers(updated);
    localStorage.setItem(
      "user",
      JSON.stringify({
        ...user,
        customersList: updated,
        customers: updated.length,
      })
    );
  }

  function addCustomer() {
    if (!name.trim() || !email.trim()) {
      notify({
        title: "Missing customer data",
        description: "Please enter both name and email before adding a customer.",
        variant: "error",
      });
      return;
    }

    // create on server
    apiCreateCustomer({ name: name.trim(), email: email.trim(), billing_country: "US" })
      .then((created: any) => {
        const createdCustomer: Customer = {
          id: created.id,
          name: created.name,
          email: created.email,
          joined: new Date(created.created_at).toLocaleDateString(),
        };
        const updated = [createdCustomer, ...customers];
        persist(updated);
        setName("");
        setEmail("");
        notify({
          title: "Customer added",
          description: `${createdCustomer.name} was added to the customer roster.`,
          variant: "success",
        });
      })
      .catch((err) => {
        notify({ title: "Add failed", description: err.message || "Could not add customer", variant: "error" });
      });
  }

  function deleteCustomer(id: number) {
    apiDeleteCustomer(id)
      .then(() => {
        const updated = customers.filter((customer) => customer.id !== id);
        persist(updated);
        notify({ title: "Customer removed", description: "The customer record has been archived.", variant: "info" });
      })
      .catch((err) => {
        notify({ title: "Delete failed", description: err.message || "Could not delete customer", variant: "error" });
      });
  }

  useEffect(() => {
    // load customers from API on mount
    getCustomers()
      .then((list: any[]) => {
        const mapped = list.map((c) => ({ id: c.id, name: c.name, email: c.email, joined: new Date(c.created_at).toLocaleDateString() }));
        persist(mapped);
      })
      .catch(() => {
        // keep local fallback
      });
  }, []);

  const filteredCustomers = useMemo(
    () => customers.filter((customer) => customer.name.toLowerCase().includes(search.toLowerCase()) || customer.email.toLowerCase().includes(search.toLowerCase())),
    [customers, search]
  );

  const columns = useMemo(
    () => [
      { key: 'name', title: 'Name', sortable: true },
      { key: 'email', title: 'Email', sortable: true },
      { key: 'joined', title: 'Joined', sortable: true, render: (customer: Customer) => customer.joined },
      { key: 'tenure', title: 'Tenure', sortable: true, render: (customer: Customer) => {
        const joinedDate = new Date(customer.joined);
        const days = Math.max(1, Math.round((Date.now() - joinedDate.getTime()) / (1000 * 60 * 60 * 24)));
        return `${days} days`;
      } },
      { key: 'actions', title: 'Actions', render: (customer: Customer) => (
        <button
          type="button"
          onClick={() => deleteCustomer(customer.id)}
          className="inline-flex items-center gap-2 rounded-full border border-red-200 bg-red-50 px-3 py-2 text-sm font-semibold text-red-700 transition hover:bg-red-100 dark:border-red-900/40 dark:bg-red-950/40 dark:text-red-300"
        >
          <Trash2 size={16} />
          Delete
        </button>
      ) },
    ],
    []
  );

  return (
    <AppShell>
      <div className="fade-in">
      <PageHeader
        eyebrow="Customer success"
        title="Customers"
        description="Manage your accounts with clarity, context, and a premium operational dashboard."
        action={<span className="inline-flex items-center gap-2"><Users size={16} />{customers.length} accounts</span>}
      />

      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <Card className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-blue-500/10 p-3 text-blue-600">
              <UserPlus size={20} />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white">Add a new customer</h2>
              <p className="text-sm text-slate-600 dark:text-slate-400">Create customer records quickly and keep the pipeline moving.</p>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Customer Name"
              className="input-field"
              aria-label="Customer name"
            />
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Customer Email"
              className="input-field"
              aria-label="Customer email"
            />
            <button onClick={addCustomer} className="btn-primary w-full">
              <UserPlus size={18} />
              Add Customer
            </button>
          </div>
        </Card>

        <Card className="space-y-4">
          <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700 dark:border-emerald-900/40 dark:bg-emerald-500/10 dark:text-emerald-300">
            <Sparkles size={14} />
            Relationship health
          </div>
          <div className="rounded-2xl border border-slate-200/70 bg-slate-50/80 p-5 dark:border-slate-700/70 dark:bg-slate-950/50">
            <p className="text-sm text-slate-600 dark:text-slate-400">Your customer roster is growing steadily and all records are in one place.</p>
            <div className="mt-4 flex items-end justify-between">
              <div>
                <p className="text-3xl font-semibold text-slate-900 dark:text-white">{customers.length}</p>
                <p className="text-sm text-slate-500 dark:text-slate-400">Registered customers</p>
              </div>
              <div className="rounded-full bg-blue-500/10 px-3 py-1 text-sm font-medium text-blue-700 dark:text-blue-300">Customer insights</div>
            </div>
          </div>
        </Card>
      </div>

      <Card className="mt-6">
        <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white">Customer list</h2>
            <p className="text-sm text-slate-600 dark:text-slate-400">Search, review, and manage customer accounts all from one dashboard.</p>
          </div>
          <div className="flex items-center gap-2 rounded-2xl border border-slate-200/70 bg-white/70 px-3 py-2 shadow-sm dark:border-slate-700/70 dark:bg-slate-900/70">
            <Search size={18} className="text-slate-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search customers"
              className="w-40 border-0 bg-transparent outline-none"
              aria-label="Search customers"
            />
          </div>
        </div>

        {filteredCustomers.length === 0 ? (
          <EmptyState
            title="No customers available"
            description="Add your first customer to start tracking accounts and revenue health."
            primaryAction={{ label: "Add customer", path: "/customers" }}
            icon={<Users size={24} />}
          />
        ) : (
          <DataTable
            columns={columns}
            data={filteredCustomers}
            searchable
            pageSize={10}
          />
        )}
      </Card>
      </div>
    </AppShell>
  );
}

export default Customers;
