import { useEffect, useState } from "react";
import { BookOpen, Check, Download, FileText, GraduationCap, Loader2, RefreshCw, Sparkles, Users } from "lucide-react";
import { useLearnerEntitlements } from "../contexts/useLearnerEntitlements";
import { createCheckout, downloadInvoicePdf, getMyInvoices, waitForPayment, type BillSphereInvoice, type BillSpherePlan } from "../services/billsphere";
import { useToast } from "../components/ToastProvider";
import "./ELearning.css";

function money(plan: BillSpherePlan) {
  try { return new Intl.NumberFormat("en-IN", { style: "currency", currency: plan.currency || "INR", maximumFractionDigits: 0 }).format(Number(plan.price)); }
  catch { return `${plan.currency || "INR"} ${plan.price}`; }
}

function featureList(plan: BillSpherePlan) {
  if (Array.isArray(plan.feature_entitlements)) return plan.feature_entitlements;
  return Object.entries(plan.feature_entitlements || {}).filter(([, value]) => Boolean(value)).map(([key, value]) => `${key.replaceAll("_", " ")}${typeof value === "boolean" ? "" : `: ${value}`}`);
}

function formatDate(value?: string | null) { return value ? new Date(value).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }) : "Not scheduled"; }

export default function ELearning() {
  const { notify } = useToast();
  const { plans, plan, subscription, loading, error, refresh, catalogTier, canIssueCertificate, canDownloadOffline, mentorSessionsRemaining } = useLearnerEntitlements();
  const [selectedPlanId, setSelectedPlanId] = useState<number | null>(null);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [invoices, setInvoices] = useState<BillSphereInvoice[]>([]);

  useEffect(() => { getMyInvoices().then(setInvoices).catch(() => setInvoices([])); }, [subscription]);

  async function startCheckout(planId: number) {
    setCheckoutLoading(true);
    try {
      const checkout = await createCheckout(planId);
      const payment = await waitForPayment(checkout.payment_id);
      if (["failed", "declined"].includes(payment.status.toLowerCase())) throw new Error(payment.failure_reason || "Payment was declined");
      await refresh();
      notify({ title: "Learning access updated", description: "Your BillSphere subscription is now reflected in your learner account.", variant: "success" });
    } catch (cause) {
      notify({ title: "Enrollment could not be completed", description: cause instanceof Error ? cause.message : "Please try again.", variant: "error" });
    } finally { setCheckoutLoading(false); setSelectedPlanId(null); }
  }

  async function download(invoiceId: number) {
    try {
      const blob = await downloadInvoicePdf(invoiceId);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a"); link.href = url; link.download = `invoice-${invoiceId}.pdf`; link.click(); URL.revokeObjectURL(url);
    } catch (cause) { notify({ title: "Download failed", description: cause instanceof Error ? cause.message : "Please try again.", variant: "error" }); }
  }

  return <div className="learning-page">
    <header className="learning-hero">
      <div><p className="eyebrow"><GraduationCap size={16} /> BILLSPHERE LEARNING</p><h1>Build your next skill.</h1><p className="hero-copy">One subscription, a living course catalog, and access rules powered by your verified BillSphere plan.</p></div>
      <div className="hero-mark"><BookOpen size={34} /><span>LEARN<br />FORWARD</span></div>
    </header>

    {error && <div className="learning-alert"><span>{error}</span><button className="icon-button" title="Retry billing connection" onClick={() => void refresh()}><RefreshCw size={16} /></button></div>}

    <section className="learning-status">
      <div><span className="section-kicker">YOUR ACCESS</span><h2>{plan?.name || "Choose a learning plan"}</h2><p>{subscription ? `${subscription.status} · renews ${formatDate(subscription.next_billing_date || subscription.current_period_end)}` : "Your course access will appear here after enrollment."}</p></div>
      <div className="access-stats"><div><strong>{catalogTier}</strong><span>catalog tier</span></div><div><strong>{canIssueCertificate ? "Eligible" : "Locked"}</strong><span>certificates</span></div><div><strong>{mentorSessionsRemaining ?? "—"}</strong><span>mentor sessions</span></div><div><strong>{canDownloadOffline ? "On" : "Off"}</strong><span>offline study</span></div></div>
    </section>

    <section className="learning-section"><div className="section-heading"><div><span className="section-kicker">PLANS FROM BILLSPHERE</span><h2>Choose your pace</h2></div><button className="icon-button" title="Refresh plans" onClick={() => void refresh()}><RefreshCw size={17} /></button></div>
      {loading ? <div className="learning-loading"><Loader2 className="spin" /> Loading live plans...</div> : <div className="learning-plans">{plans.map((candidate) => <article className={`learning-plan ${candidate.id === plan?.id ? "current" : ""}`} key={candidate.id}><div className="plan-top"><span className="plan-icon"><Sparkles size={18} /></span>{candidate.id === plan?.id && <span className="current-badge">CURRENT</span>}</div><h3>{candidate.name}</h3><p className="plan-description">{candidate.description || "Flexible access to the BillSphere learning catalog."}</p><p className="plan-price">{money(candidate)} <small>/ {candidate.billing_cycle}</small></p>{candidate.trial_days > 0 && <p className="trial-note">{candidate.trial_days}-day trial</p>}<ul>{featureList(candidate).slice(0, 6).map((feature) => <li key={feature}><Check size={15} />{feature}</li>)}</ul><button className={candidate.id === plan?.id ? "plan-button muted" : "plan-button"} disabled={candidate.id === plan?.id || checkoutLoading} onClick={() => { setSelectedPlanId(candidate.id); void startCheckout(candidate.id); }}>{selectedPlanId === candidate.id ? <><Loader2 className="spin" size={16} /> Confirming...</> : candidate.id === plan?.id ? "Active plan" : "Enroll now"}</button></article>)}</div>}
    </section>

    <section className="learning-section billing-strip"><div className="section-heading"><div><span className="section-kicker">BILLING HISTORY</span><h2>Receipts for your learning</h2></div><FileText size={20} /></div>{invoices.length === 0 ? <p className="empty-copy">Invoices will appear after your first BillSphere payment.</p> : <div className="invoice-list">{invoices.slice(0, 5).map((invoice) => <div className="invoice-row" key={invoice.id}><div><strong>{invoice.invoice_number || `Invoice #${invoice.id}`}</strong><span>{formatDate(invoice.paid_at || invoice.due_date)} · {invoice.status}</span></div><button className="icon-button" title="Download invoice PDF" onClick={() => void download(invoice.id)}><Download size={16} /></button></div>)}</div>}</section>
    <div className="learning-note"><Users size={17} /><span>Mentor bookings, certificates, and downloads follow the entitlements returned by your active plan.</span></div>
  </div>;
}
