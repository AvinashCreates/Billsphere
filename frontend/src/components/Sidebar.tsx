import { LayoutDashboard, Users, FileText, CreditCard, Settings, User, LogOut, Sparkles } from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";
import ThemeToggle from "./ThemeToggle";
import { useToast } from "./ToastProvider";
import { useAuth } from "../contexts/AuthContext";

function Sidebar() {
  const navigate = useNavigate();
  const { notify } = useToast();
  const { user, logout: authLogout } = useAuth();
  const isAdmin = user?.role === "admin";

  const menuItems = [
    { name: "Dashboard", path: "/dashboard", icon: <LayoutDashboard size={18} /> },
    ...(isAdmin ? [{ name: "Customers", path: "/customers", icon: <Users size={18} /> }] : []),
    { name: "Invoices", path: "/invoices", icon: <FileText size={18} /> },
    { name: "Plans", path: "/plans", icon: <CreditCard size={18} /> },
    { name: "Settings", path: "/settings", icon: <Settings size={18} /> },
  ];

  function logout() {
    authLogout();
    notify({
      title: "Signed out",
      description: "You have safely logged out of the billing workspace.",
      variant: "info",
    });
    navigate("/login");
  }

  return (
    <aside className="sticky top-0 hidden h-screen w-72 flex-col border-r border-slate-200/70 bg-white/70 px-5 py-6 backdrop-blur-xl dark:border-slate-700/70 dark:bg-slate-950/70 lg:flex" aria-label="Application sidebar">
      <div className="mb-8 rounded-[24px] border border-slate-200/70 bg-gradient-to-br from-blue-600/10 via-white to-indigo-600/10 p-4 dark:border-slate-700/70 dark:from-blue-500/10 dark:via-slate-900 dark:to-indigo-500/10">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-700 text-sm font-semibold text-white shadow-lg shadow-blue-600/20">
            BS
          </div>
          <div>
            <h1 className="text-lg font-semibold text-slate-900 dark:text-white">BillSphere</h1>
            <p className="text-sm text-slate-500 dark:text-slate-400">Billing OS</p>
          </div>
        </div>
        <div className="mt-4 inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.2em] text-emerald-700 dark:border-emerald-400/20 dark:bg-emerald-500/10 dark:text-emerald-300">
          <Sparkles size={12} />
          Secure by design
        </div>
      </div>

      <nav className="flex-1 space-y-2" aria-label="Sidebar navigation">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-2xl px-3.5 py-3 text-sm font-medium transition-all duration-200 ${
                isActive
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white"
              }`
            }
          >
            {item.icon}
            <span>{item.name}</span>
          </NavLink>
        ))}
      </nav>

      <div className="space-y-3 border-t border-slate-200/70 pt-4 dark:border-slate-700/70">
        <div className="flex items-center justify-between rounded-2xl border border-slate-200/70 bg-slate-50/80 px-3 py-3 dark:border-slate-700/70 dark:bg-slate-900/70">
          <div>
            <p className="text-sm font-semibold text-slate-700 dark:text-slate-200">Theme</p>
            <p className="text-xs text-slate-500 dark:text-slate-400">Switch instantly</p>
          </div>
          <ThemeToggle />
        </div>

        <button
          onClick={() => navigate("/profile")}
          className="flex w-full items-center gap-3 rounded-2xl px-3.5 py-3 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white"
        >
          <User size={18} />
          Profile
        </button>

        <button
          onClick={logout}
          className="flex w-full items-center gap-3 rounded-2xl px-3.5 py-3 text-sm font-medium text-red-500 transition hover:bg-red-50 dark:hover:bg-red-950/40"
        >
          <LogOut size={18} />
          Logout
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
