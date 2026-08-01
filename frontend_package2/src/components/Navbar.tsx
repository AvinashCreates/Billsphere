import { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { Menu, X } from "lucide-react";
import ThemeToggle from "./ThemeToggle";

const navItems = [
  { label: "Dashboard", path: "/dashboard" },
  { label: "Customers", path: "/customers" },
  { label: "Plans", path: "/plans" },
  { label: "Subscriptions", path: "/" },
  { label: "Invoices", path: "/invoices" },
  { label: "Payments", path: "/" },
  { label: "Analytics", path: "/dashboard" },
  { label: "Pricing", path: "/" },
  { label: "Documentation", path: "/" },
];

function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="site-header border-b border-slate-200/80 bg-white/95 backdrop-blur-xl dark:border-slate-800/80 dark:bg-slate-950/95">
      <div className="page-container flex h-[72px] items-center justify-between gap-4 px-4 sm:h-[64px] sm:px-6 lg:px-8">
        <div className="flex items-center gap-4 text-sm font-semibold text-slate-900 dark:text-white">
          <Link to="/" className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-900 text-white">B</div>
            <div className="hidden min-w-0 flex-col sm:flex">
              <span className="truncate text-base">BillSphere</span>
              <span className="truncate text-xs font-normal text-slate-500 dark:text-slate-400">Revenue Automation Platform</span>
            </div>
          </Link>
        </div>

        <nav className="hidden flex-1 items-center justify-center gap-6 text-sm font-medium text-slate-600 dark:text-slate-300 lg:flex">
          {navItems.map((item) => (
            <NavLink
              key={item.label}
              to={item.path}
              className={({ isActive }) =>
                `transition duration-200 ${isActive ? "text-slate-900 dark:text-white" : "hover:text-slate-900 dark:hover:text-white"}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          <ThemeToggle />
          <div className="hidden items-center gap-3 lg:flex">
            <Link to="/login" className="btn-ghost">
              Login
            </Link>
            <Link to="/register" className="btn-primary">
              Get started
            </Link>
          </div>
          <button
            type="button"
            aria-label={mobileOpen ? "Close menu" : "Open menu"}
            onClick={() => setMobileOpen((value) => !value)}
            className="inline-flex h-11 w-11 items-center justify-center rounded-xl border border-slate-200/80 bg-white/90 text-slate-700 transition hover:border-slate-300 hover:bg-slate-50 dark:border-slate-700/80 dark:bg-slate-950/90 dark:text-slate-200 lg:hidden"
          >
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {mobileOpen ? (
        <div className="border-t border-slate-200/80 bg-white/95 px-4 py-4 dark:border-slate-800/80 dark:bg-slate-950/95 lg:hidden">
          <nav className="flex flex-col gap-3">
            {navItems.slice(0, 6).map((item) => (
              <Link
                key={item.label}
                to={item.path}
                onClick={() => setMobileOpen(false)}
                className="block rounded-2xl px-4 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-900"
              >
                {item.label}
              </Link>
            ))}
            <div className="mt-3 flex flex-col gap-3">
              <Link
                to="/login"
                onClick={() => setMobileOpen(false)}
                className="inline-flex w-full items-center justify-center rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 transition hover:bg-slate-50 dark:border-slate-700/80 dark:bg-slate-900 dark:text-slate-100"
              >
                Login
              </Link>
              <Link
                to="/register"
                onClick={() => setMobileOpen(false)}
                className="inline-flex w-full items-center justify-center rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
              >
                Get started
              </Link>
            </div>
          </nav>
        </div>
      ) : null}
    </header>
  );
}

export default Navbar;
