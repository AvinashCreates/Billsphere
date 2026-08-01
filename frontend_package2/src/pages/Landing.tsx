import { ArrowRight, BarChart3, ShieldCheck, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

const highlights = [
  {
    title: "Revenue intelligence",
    description: "Track MRR, expansion signals, and customer health from a single command center.",
    icon: <BarChart3 size={18} />,
  },
  {
    title: "Trusted workflows",
    description: "Automate renewals, invoicing, and recovery flows with enterprise-grade controls.",
    icon: <ShieldCheck size={18} />,
  },
  {
    title: "Fast execution",
    description: "Launch premium billing experiences with elegant, frictionless operations.",
    icon: <Sparkles size={18} />,
  },
];

function Landing() {
  return (
    <div className="min-h-screen bg-transparent px-4 py-8 sm:px-6 lg:px-8">
      <section className="hero-grid mx-auto flex max-w-7xl flex-col items-center rounded-[36px] border border-slate-200/70 bg-white/70 px-6 py-16 text-center shadow-[0_25px_80px_rgba(15,23,42,0.08)] backdrop-blur-2xl dark:border-slate-700/70 dark:bg-slate-900/70 sm:px-10 lg:px-16 lg:py-24">
        <div className="section-pill">
          <Sparkles size={14} />
          Premium billing & revenue automation
        </div>
        <h1 className="mt-6 text-4xl font-semibold tracking-tight text-slate-900 dark:text-white sm:text-5xl lg:text-7xl">
          Modern finance operations for ambitious growth.
        </h1>
        <p className="mx-auto mt-6 max-w-3xl text-lg leading-8 text-slate-600 dark:text-slate-400 sm:text-xl">
          BillSphere brings together subscription management, invoices, analytics, and revenue health in one polished operating system.
        </p>

        <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
          <Link to="/register" className="btn-primary">
            Start free
            <ArrowRight size={16} />
          </Link>
          <Link to="/login" className="btn-ghost">
            Explore platform
          </Link>
        </div>
      </section>

      <section className="mx-auto mt-10 grid max-w-7xl gap-6 md:grid-cols-3">
        {highlights.map((item) => (
          <div key={item.title} className="panel rounded-[24px] p-7 text-left">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-50 text-blue-700 dark:bg-blue-500/10 dark:text-blue-300">
              {item.icon}
            </div>
            <h2 className="mt-5 text-xl font-semibold text-slate-900 dark:text-white">{item.title}</h2>
            <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-400">{item.description}</p>
          </div>
        ))}
      </section>
    </div>
  );
}

export default Landing;
