const plansGrid = document.getElementById('plansGrid');
const planTemplate = document.getElementById('planTemplate');
const trialBtn = document.getElementById('trialBtn');

const billsphereBase = 'http://localhost:5173';
const billsphereApiBase = 'http://127.0.0.1:8000/api/v1';

let plans = [];

function formatCurrency(value) {
  const numeric = Number(value ?? 0);
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(numeric);
}

function normalizePlanName(plan) {
  return plan?.name || 'Spotify Plan';
}

function normalizePlanDescription(plan) {
  return plan?.description || 'Flexible Spotify subscription access via BillSphere.';
}

function normalizeBillingCycle(plan) {
  const value = String(plan?.billing_cycle || 'monthly').toLowerCase();
  return value.includes('year') ? 'year' : 'month';
}

function getPlanFeatures(plan) {
  if (Array.isArray(plan?.feature_entitlements)) {
    return plan.feature_entitlements.filter(Boolean);
  }

  if (plan?.feature_entitlements && typeof plan.feature_entitlements === 'object') {
    return Object.entries(plan.feature_entitlements)
      .filter(([, value]) => Boolean(value))
      .map(([key]) => key.replace(/_/g, ' '));
  }

  return ['Premium access', 'High quality streaming', 'Multi-device support'];
}

function openBillspherePayment(plan) {
  const planId = plan?.id ?? 1;
  const planName = encodeURIComponent(normalizePlanName(plan));
  const targetUrl = `${billsphereBase}/customer/plans/${planId}/confirm?source=external-app&planName=${planName}`;
  window.location.href = targetUrl;
}

function renderPlans() {
  plansGrid.innerHTML = '';

  plans.forEach((plan) => {
    const fragment = planTemplate.content.cloneNode(true);
    const card = fragment.querySelector('.plan-card');
    const planName = fragment.querySelector('.plan-name');
    const planDesc = fragment.querySelector('.plan-desc');
    const planPrice = fragment.querySelector('.plan-price');
    const planCycle = fragment.querySelector('.plan-cycle');
    const planPopular = fragment.querySelector('.plan-popular');
    const featureList = fragment.querySelector('.plan-features');
    const selectButton = fragment.querySelector('.plan-btn');

    const isFeatured = /premium|standard/i.test(normalizePlanName(plan));
    if (isFeatured) {
      card.classList.add('featured');
      planPopular.classList.remove('hidden');
    }

    planName.textContent = normalizePlanName(plan);
    planDesc.textContent = normalizePlanDescription(plan);
    planPrice.textContent = formatCurrency(plan.price ?? 0);
    planCycle.textContent = `/${normalizeBillingCycle(plan)}`;

    getPlanFeatures(plan).forEach((feature) => {
      const item = document.createElement('li');
      item.textContent = feature;
      featureList.appendChild(item);
    });

    selectButton.addEventListener('click', () => openBillspherePayment(plan));
    plansGrid.appendChild(fragment);
  });
}

async function loadPlans() {
  try {
    const response = await fetch(`${billsphereApiBase}/plans?platform=Spotify&page=1&page_size=100`, {
      headers: { Accept: 'application/json' }
    });

    if (!response.ok) {
      throw new Error(`Unable to load plans from BillSphere (${response.status})`);
    }

    const data = await response.json();
    const items = Array.isArray(data) ? data : (Array.isArray(data.plans) ? data.plans : (Array.isArray(data.items) ? data.items : []));
    const spotifyPlans = items.filter((plan) => plan && String(plan.platform || '').toLowerCase() === 'spotify' && plan.is_active !== false);

    if (!spotifyPlans.length) {
      throw new Error('No Spotify plans are available from BillSphere yet.');
    }

    plans = spotifyPlans.sort((a, b) => Number(a.price ?? 0) - Number(b.price ?? 0));
    renderPlans();
  } catch (error) {
    console.error('External app plan sync failed:', error);
    plansGrid.innerHTML = '<p style="padding: 1rem; color: #fca5a5;">Unable to sync with BillSphere plans right now. Please try again later.</p>';
  }
}

trialBtn.addEventListener('click', () => {
  const fallbackPlan = plans.find((plan) => /premium|standard/i.test(normalizePlanName(plan))) || plans[0];
  if (fallbackPlan) {
    openBillspherePayment(fallbackPlan);
  }
});

loadPlans();
