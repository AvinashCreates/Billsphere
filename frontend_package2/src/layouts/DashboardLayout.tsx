import { Link, Outlet, useLocation } from "react-router-dom";
import { ChevronRight, LayoutGrid, ShieldCheck, User } from "lucide-react";
import Sidebar from "../components/Sidebar";
import ThemeToggle from "../components/ThemeToggle";
import { useAuth } from "../contexts/AuthContext";

function DashboardLayout() {
  const location = useLocation();
  const { role } = useAuth();
  const title = location.pathname.replace("/", "").replace(/(^|\/)(.)/g, (_, __, ch) => ch.toUpperCase()) || "Dashboard";

  return (
    <div className="flex min-h-screen bg-transparent">
      <Sidebar />

      <main className="flex-1 overflow-y-auto px-3 py-3 sm:px-6 lg:px-8">
        <div className="mx-auto flex max-w-7xl flex-col gap-5">
          <header className="panel flex items-center justify-between gap-4 rounded-[24px] px-4 py-4 sm:px-6">
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <div className="section-pill">
                  <LayoutGrid size={14} />
                  {title}
                </div>
                {role && (
                  <div
                    className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${
                      role === "admin"
                        ? "bg-indigo-500/10 text-indigo-700 dark:text-indigo-300"
                        : "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300"
                    }`}
                  >
                    {role === "admin" ? <ShieldCheck size={13} /> : <User size={13} />}
                    {role === "admin" ? "Admin" : "Customer"}
                  </div>
                )}
              </div>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
                Premium billing operations for every customer moment.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <ThemeToggle />
              <Link to="/settings" className="btn-ghost hidden sm:inline-flex">
                Open settings
                <ChevronRight size={16} />
              </Link>
            </div>
          </header>

          <div className="panel-soft rounded-[28px] p-3 sm:p-6 lg:p-8">
            <Outlet />
          </div>
        </div>
      </main>
    </div>
  );
}

export default DashboardLayout;