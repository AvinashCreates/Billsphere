import { useEffect, useState } from "react";
import { ShieldCheck, Trash2, Users } from "lucide-react";
import PageHeader from "../components/PageHeader";
import { useToast } from "../components/ToastProvider";
import { deleteAdminUser, getAdminUsers, updateAdminUser } from "../services/api";
import type { AdminUser } from "../services/api";

function AdminUsers() {
  const { notify } = useToast();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadUsers() {
    try {
      setLoading(true);
      setError("");
      const result = await getAdminUsers();
      setUsers(result.items);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unable to load users";
      setError(message);
      notify({ title: "Users unavailable", description: message, variant: "error" });
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadUsers(); }, []);

  async function changeUser(user: AdminUser, field: "role" | "is_active", value: string | boolean) {
    try {
      const updated = await updateAdminUser(user.id, { [field]: value });
      setUsers((current) => current.map((item) => item.id === updated.id ? updated : item));
      notify({ title: "User updated", description: `${updated.first_name} ${updated.last_name} was updated.`, variant: "success" });
    } catch (err) {
      notify({ title: "Update failed", description: err instanceof Error ? err.message : "Unable to update user", variant: "error" });
    }
  }

  async function removeUser(user: AdminUser) {
    if (!window.confirm(`Delete ${user.email}? This cannot be undone.`)) return;
    try {
      await deleteAdminUser(user.id);
      setUsers((current) => current.filter((item) => item.id !== user.id));
      notify({ title: "User deleted", description: `${user.email} was removed.`, variant: "success" });
    } catch (err) {
      notify({ title: "Delete failed", description: err instanceof Error ? err.message : "Unable to delete user", variant: "error" });
    }
  }

  return (
    <div>
      <PageHeader title="User management" description="Control access, roles, and account status." />
      {error && <div className="mb-5 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>}
      <div className="overflow-hidden rounded-2xl border border-slate-200/70 bg-white/70 dark:border-slate-700/70 dark:bg-slate-900/60">
        <div className="flex items-center gap-3 border-b border-slate-200/70 px-5 py-4 dark:border-slate-700/70">
          <Users size={18} /> <span className="font-semibold">{loading ? "Loading users..." : `${users.length} users`}</span>
        </div>
        {!loading && users.length === 0 ? (
          <div className="p-10 text-center text-sm text-slate-500">No users found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[680px] text-left text-sm">
              <thead className="bg-slate-50/80 text-xs uppercase tracking-wide text-slate-500 dark:bg-slate-800/60">
                <tr><th className="px-5 py-3">User</th><th className="px-5 py-3">Role</th><th className="px-5 py-3">Status</th><th className="px-5 py-3">Joined</th><th className="px-5 py-3 text-right">Actions</th></tr>
              </thead>
              <tbody className="divide-y divide-slate-200/70 dark:divide-slate-700/70">
                {users.map((user) => (
                  <tr key={user.id}>
                    <td className="px-5 py-4"><div className="font-medium">{user.first_name} {user.last_name}</div><div className="text-xs text-slate-500">{user.email}</div></td>
                    <td className="px-5 py-4"><label className="sr-only" htmlFor={`role-${user.id}`}>Role for {user.email}</label><select id={`role-${user.id}`} className="rounded-lg border border-slate-300 bg-transparent px-2 py-1.5" value={user.role} onChange={(event) => changeUser(user, "role", event.target.value)}><option value="customer">Customer</option><option value="admin">Admin</option></select></td>
                    <td className="px-5 py-4"><button type="button" className={`rounded-lg px-3 py-1.5 text-xs font-semibold ${user.is_active ? "bg-emerald-100 text-emerald-700" : "bg-slate-200 text-slate-600"}`} onClick={() => changeUser(user, "is_active", !user.is_active)}>{user.is_active ? "Active" : "Inactive"}</button></td>
                    <td className="px-5 py-4 text-slate-500">{new Date(user.created_at).toLocaleDateString()}</td>
                    <td className="px-5 py-4 text-right"><button type="button" title="Delete user" aria-label={`Delete ${user.email}`} className="text-slate-400 hover:text-red-600" onClick={() => removeUser(user)}><Trash2 size={17} /></button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      <div className="mt-4 flex items-center gap-2 text-xs text-slate-500"><ShieldCheck size={14} /> Changes are protected by admin authorization.</div>
    </div>
  );
}

export default AdminUsers;