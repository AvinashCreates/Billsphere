import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import { registerUser } from "../assets/services/api";
import { useToast } from "../components/ToastProvider";

function Register() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [agree, setAgree] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { notify } = useToast();

  const [form, setForm] = useState({ email: "", password: "", confirmPassword: "", role: "customer" });

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function register(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");

    if (form.password !== form.confirmPassword) {
      const message = "Passwords do not match.";
      setError(message);
      notify({ title: "Registration failed", description: message, variant: "error" });
      return;
    }

    if (!agree) {
      const message = "Please accept the terms to continue.";
      setError(message);
      notify({ title: "Registration failed", description: message, variant: "error" });
      return;
    }

    setLoading(true);

    try {
      await registerUser({ email: form.email, password: form.password, role: form.role });
      notify({ title: "Account created", description: "Your billing workspace is ready.", variant: "success" });
      navigate("/login");
    } catch (err: any) {
      const message = err.message || "Something went wrong.";
      setError(message);
      notify({ title: "Registration failed", description: message, variant: "error" });
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 py-12 text-slate-900 dark:bg-slate-950 dark:text-white">
      <div className="page-container">
        <div className="auth-grid overflow-hidden rounded-[28px] border border-slate-200/70 bg-white shadow-[0_20px_70px_rgba(15,23,42,0.08)] dark:border-slate-800/70 dark:bg-slate-950/95">
          <section className="auth-hero bg-slate-900 text-white sm:p-10 lg:px-14 lg:py-16">
            <div className="flex flex-col justify-between gap-8 py-8 sm:py-10">
              <div className="space-y-6">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-300">Secure onboarding</p>
                <h1 className="max-w-2xl text-4xl font-semibold leading-tight sm:text-5xl">Create your enterprise-grade billing account.</h1>
                <p className="max-w-xl text-base leading-7 text-slate-300">Start managing recurring revenue with clarity and confidence across your whole organization.</p>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
                  <p className="text-sm font-semibold text-white">SOC 2 Type II</p>
                  <p className="mt-2 text-sm text-slate-300">Compliance built for enterprise workflows.</p>
                </div>
                <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
                  <p className="text-sm font-semibold text-white">Reliable uptime</p>
                  <p className="mt-2 text-sm text-slate-300">Designed for high-volume subscription operations.</p>
                </div>
              </div>
            </div>
          </section>

          <section className="auth-form p-8 sm:p-10 lg:p-12">
            <div className="mx-auto max-w-xl">
              <div className="mb-8">
                <h2 className="text-3xl font-semibold text-slate-900 dark:text-white">Create account</h2>
                <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-400">Launch your secure billing workspace in minutes.</p>
              </div>

              {error && (
                <div className="mb-6 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 dark:border-rose-900/40 dark:bg-rose-950/40 dark:text-rose-300">
                  {error}
                </div>
              )}

              <form onSubmit={register} className="space-y-6">
                <div className="space-y-3">
                  <label htmlFor="email" className="text-sm font-semibold text-slate-900 dark:text-slate-100">Work email</label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    value={form.email}
                    onChange={handleChange}
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
                      value={form.password}
                      onChange={handleChange}
                      required
                      placeholder="Create a password"
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
                  <p className="text-sm text-slate-500 dark:text-slate-400">Use 8+ characters with letters, numbers, and symbols.</p>
                </div>

                <div className="space-y-3">
                  <label htmlFor="confirmPassword" className="text-sm font-semibold text-slate-900 dark:text-slate-100">Confirm password</label>
                  <div className="relative">
                    <input
                      id="confirmPassword"
                      name="confirmPassword"
                      type={showConfirmPassword ? "text" : "password"}
                      value={form.confirmPassword}
                      onChange={handleChange}
                      required
                      placeholder="Confirm password"
                      className="input-field pr-12"
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword((prev) => !prev)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 transition hover:text-slate-900 dark:hover:text-white"
                      aria-label={showConfirmPassword ? "Hide confirm password" : "Show confirm password"}
                    >
                      {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                </div>

                <div className="space-y-3">
                  <label htmlFor="role" className="text-sm font-semibold text-slate-900 dark:text-slate-100">Account type</label>
                  <select
                    id="role"
                    name="role"
                    value={form.role}
                    onChange={handleChange}
                    className="input-field"
                  >
                    <option value="customer">Customer</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>

                <label className="flex items-start gap-3 text-sm text-slate-600 dark:text-slate-400">
                  <input
                    type="checkbox"
                    checked={agree}
                    onChange={(e) => setAgree(e.target.checked)}
                    className="mt-1 h-4 w-4 rounded border-slate-300 text-slate-900 focus:ring-slate-900"
                  />
                  <span>I agree to the terms of service and privacy policy.</span>
                </label>

                <button type="submit" disabled={loading} className="btn-primary w-full">
                  {loading ? "Creating account..." : "Create account"}
                </button>
              </form>

              <p className="mt-6 text-center text-sm text-slate-600 dark:text-slate-400">
                Already have an account? <Link to="/login" className="font-semibold text-slate-900 underline decoration-slate-300 dark:text-white">Log in</Link>
              </p>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}

export default Register;
