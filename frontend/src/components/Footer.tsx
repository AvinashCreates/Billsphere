import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="mt-12 border-t border-slate-200/70 bg-transparent py-8 dark:border-slate-700/70">
      <div className="page-container flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-2xl bg-slate-900 text-white flex items-center justify-center font-semibold">BS</div>
          <div>
            <div className="text-sm font-semibold text-slate-900 dark:text-white">BillSphere</div>
            <div className="text-xs text-slate-500 dark:text-slate-400">Revenue Automation Platform</div>
          </div>
        </div>

        <nav className="flex flex-wrap items-center gap-4 text-sm text-slate-600 dark:text-slate-300">
          <Link to="/features" className="hover:underline">Features</Link>
          <Link to="/pricing" className="hover:underline">Pricing</Link>
          <Link to="/docs" className="hover:underline">Documentation</Link>
          <Link to="/api" className="hover:underline">API</Link>
          <Link to="/support" className="hover:underline">Support</Link>
          <Link to="/privacy" className="hover:underline">Privacy</Link>
        </nav>

        <div className="text-xs text-slate-500 dark:text-slate-400">© {new Date().getFullYear()} BillSphere — v0.1.0</div>
      </div>
    </footer>
  );
}
