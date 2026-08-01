import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import { loginUser } from "../assets/services/api";
import { useToast } from "../components/ToastProvider";

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { notify } = useToast();

  async function handleLogin(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const result = await loginUser({ email, password });
      localStorage.setItem("access_token", result.access_token);
      localStorage.setItem("loggedIn", "true");
      notify({
        title: "Welcome back",
        description: "You have successfully signed in to BillSphere.",
        variant: "success",
      });
      navigate("/dashboard");
    } catch (err: any) {
      const message = err.message || "Invalid email or password.";
      setError(message);
      notify({
        title: "Login failed",
        description: message,
        variant: "error",
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 py-12 text-slate-900 dark:bg-slate-950 dark:text-white">
      <div className="page-container">
        <div className="auth-grid overflow-hidden rounded-[28px] border border-slate-200/70 bg-white shadow-[0_20px_70px_rgba(15,23,42,0.08)] dark:border-slate-800/70 dark:bg-slate-950/95">
          <section className="auth-hero bg-gradient-to-br from-slate-950 via-indigo-950 to-blue-700 p-8 text-white sm:p-10 lg:px-14 lg:py-16">
            <div className="space-y-8">
              <div className="space-y-4">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-300">Enterprise access</p>
                <h1 className="text-4xl font-semibold leading-tight sm:text-5xl">Secure access to your billing workspace.</h1>
                <p className="max-w-2xl text-base leading-7 text-slate-300">Manage subscriptions, invoices, and revenue performance with confidence from one unified dashboard.</p>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
                  <p className="text-sm font-semibold text-white">Multi-tenant ready</p>
                  <p className="mt-2 text-sm text-slate-300">Scale securely across teams and global customers.</p>
                </div>
                <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
                  <p className="text-sm font-semibold text-white">Data-driven insights</p>
                  <p className="mt-2 text-sm text-slate-300">Turn recurring revenue into predictable growth.</p>
                </div>
              </div>
            </div>
          </section>

          <section className="auth-form p-8 sm:p-10 lg:p-12">
            <div className="mx-auto max-w-xl">
              <div className="mb-8">
                <h2 className="text-3xl font-semibold text-slate-900 dark:text-white">Welcome back</h2>
                <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-400">Sign in to continue your revenue operations.</p>
              </div>

              {error && (
                <div className="mb-6 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 dark:border-rose-900/40 dark:bg-rose-950/40 dark:text-rose-300">
                  {error}
                </div>
              )}

              <form onSubmit={handleLogin} className="space-y-6">
                <div className="space-y-3">
                  <label htmlFor="email" className="text-sm font-semibold text-slate-900 dark:text-slate-100">Email</label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    placeholder="name@company.com"
                    className="input-field"
                  />
                </div>

                <div className="space-y-3">
                  <label htmlFor="password" className="text-sm font-semibold text-slate-900 dark:text-slate-100">Password</label>
                  <div className="relative">
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      placeholder="Enter password"
                      className="input-field pr-12"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword((prev) => !prev)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 transition hover:text-slate-900 dark:hover:text-white"
                      aria-label={showPassword ? "Hide password" : "Show password"}
                    >
                      {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                </div>

                <button type="submit" disabled={loading} className="btn-primary w-full">
                  {loading ? "Signing in..." : "Log in"}
                </button>
              </form>

              <p className="mt-6 text-center text-sm text-slate-600 dark:text-slate-400">
                Need an account? <Link to="/register" className="font-semibold text-slate-900 underline decoration-slate-300 dark:text-white">Create one</Link>
              </p>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}

export default Login;
