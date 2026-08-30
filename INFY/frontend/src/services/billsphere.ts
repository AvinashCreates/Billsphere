const API_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

export type FeatureEntitlements = string[] | Record<string, unknown> | null;

export interface BillSpherePlan {
  id: number;
  platform: string;
  name: string;
  description?: string | null;
  price: number | string;
  currency: string;
  billing_cycle: string;
  trial_days: number;
  feature_entitlements?: FeatureEntitlements;
  is_active?: boolean;
}

export interface BillSphereSubscription {
  id: number;
  customer_id: number;
  plan_id: number;
  billing_cycle: string;
  status: string;
  start_date: string;
  end_date?: string | null;
  current_period_end?: string | null;
  next_billing_date?: string | null;
  cancel_at_period_end: boolean;
}

export interface BillSphereInvoice {
  id: number;
  invoice_number?: string | null;
  subscription_id?: number | null;
  total_amount?: number | string | null;
  amount?: number | string | null;
  currency?: string | null;
  status: string;
  due_date?: string | null;
  paid_at?: string | null;
}

export interface BillSpherePayment {
  id: number;
  invoice_id: number;
  amount: number | string;
  payment_method: string;
  status: string;
  transaction_id?: string | null;
  failure_reason?: string | null;
  created_at?: string | null;
}

export interface CheckoutResult {
  payment_id: number;
  payment_status: string;
  subscription_id: number;
  subscription_status: string;
  plan_id: number;
  amount: number | string;
  currency: string;
  confirmation_url?: string | null;
  mock_mode: boolean;
  email_delivered?: boolean | null;
}

async function parseResponse(response: Response): Promise<unknown> {
  const contentType = response.headers.get("content-type") || "";
  return contentType.includes("application/json") ? response.json() : response.text();
}

function errorMessage(result: unknown, fallback: string): string {
  if (typeof result === "string") return result;
  if (result && typeof result === "object") {
    const detail = (result as { detail?: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return detail.map((item) => (item as { msg?: string })?.msg || "Validation error").join(", ");
    const message = (result as { message?: unknown }).message;
    if (typeof message === "string") return message;
  }
  return fallback;
}

function headers(): Record<string, string> {
  const token = localStorage.getItem("access_token");
  return {
    Accept: "application/json",
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function refreshAccessToken(): Promise<boolean> {
  const refreshToken = localStorage.getItem("refresh_token");
  if (!refreshToken) return false;

  const response = await fetch(`${API_URL}/refresh`, {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  if (!response.ok) return false;

  const result = (await response.json()) as { access_token?: string; refresh_token?: string };
  if (!result.access_token) return false;
  localStorage.setItem("access_token", result.access_token);
  if (result.refresh_token) localStorage.setItem("refresh_token", result.refresh_token);
  return true;
}

async function request<T>(path: string, init: RequestInit = {}, canRefresh = true): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { ...headers(), ...(init.headers || {}) },
  });

  if (response.status === 401 && canRefresh && await refreshAccessToken()) {
    return request<T>(path, init, false);
  }

  const result = await parseResponse(response);
  if (!response.ok) throw new Error(errorMessage(result, "BillSphere request failed"));
  return result as T;
}

function list<T>(result: unknown, key: string): T[] {
  if (Array.isArray(result)) return result as T[];
  if (result && typeof result === "object") {
    const values = (result as Record<string, unknown>)[key] || (result as Record<string, unknown>).items;
    return Array.isArray(values) ? values as T[] : [];
  }
  return [];
}

export async function getElearningPlans(): Promise<BillSpherePlan[]> {
  const result = await request<unknown>("/plans?platform=elearning&page=1&page_size=100");
  return list<BillSpherePlan>(result, "plans").filter((plan) => plan.is_active !== false && plan.platform?.toLowerCase() === "elearning");
}

export async function getPlan(planId: number): Promise<BillSpherePlan> {
  return request<BillSpherePlan>(`/plans/${planId}`);
}

export async function getMySubscriptions(): Promise<BillSphereSubscription[]> {
  return list<BillSphereSubscription>(await request<unknown>("/subscriptions/me"), "items");
}

export async function createCheckout(planId: number): Promise<CheckoutResult> {
  return request<CheckoutResult>("/payments/checkout", {
    method: "POST",
    body: JSON.stringify({ plan_id: planId, payment_method: "mock_success" }),
  });
}

export async function getPayment(paymentId: number): Promise<BillSpherePayment> {
  return request<BillSpherePayment>(`/payments/${paymentId}`);
}

export async function waitForPayment(paymentId: number, attempts = 6): Promise<BillSpherePayment> {
  let payment = await getPayment(paymentId);
  for (let attempt = 1; attempt < attempts && payment.status === "pending"; attempt += 1) {
    await new Promise((resolve) => window.setTimeout(resolve, 1000));
    payment = await getPayment(paymentId);
  }
  return payment;
}

export async function getMyInvoices(): Promise<BillSphereInvoice[]> {
  return list<BillSphereInvoice>(await request<unknown>("/invoices?page=1&page_size=100"), "items");
}

export async function downloadInvoicePdf(invoiceId: number): Promise<Blob> {
  const response = await fetch(`${API_URL}/invoices/${invoiceId}/pdf`, { headers: headers() });
  if (!response.ok) throw new Error("Invoice PDF could not be downloaded");
  return response.blob();
}
