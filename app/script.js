const plans = [
  {
    id: 1,
    name: 'Mini',
    description: 'Perfect for casual listening and quick daily playlists.',
    price: 199,
    cycle: 'month',
    popular: false,
    features: ['Offline mode', 'Ad-free listening', 'Shuffle play', '2 device sync']
  },
  {
    id: 2,
    name: 'Premium',
    description: 'The best value for serious music lovers and daily streamers.',
    price: 499,
    cycle: 'month',
    popular: true,
    features: ['Unlimited skips', 'High quality audio', 'Family plan support', 'No ads']
  },
  {
    id: 3,
    name: 'Family',
    description: 'Share one premium subscription across multiple members.',
    price: 799,
    cycle: 'month',
    popular: false,
    features: ['Up to 6 users', 'Parental controls', 'Premium audio', 'Shared playlists']
  }
];

const plansGrid = document.getElementById('plansGrid');
const planTemplate = document.getElementById('planTemplate');
const trialBtn = document.getElementById('trialBtn');

const billsphereBase = 'http://localhost:5173';

function formatCurrency(value) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(value);
}

function openBillspherePayment(plan) {
  const targetUrl = `${billsphereBase}/customer/plans/${plan.id}/confirm?source=external-app&planName=${encodeURIComponent(plan.name)}`;
  window.location.href = targetUrl;
}

function renderPlans() {
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

    if (plan.popular) {
      card.classList.add('featured');
      planPopular.classList.remove('hidden');
    }

    planName.textContent = plan.name;
    planDesc.textContent = plan.description;
    planPrice.textContent = formatCurrency(plan.price);
    planCycle.textContent = `/${plan.cycle}`;

    plan.features.forEach((feature) => {
      const item = document.createElement('li');
      item.textContent = feature;
      featureList.appendChild(item);
    });

    selectButton.addEventListener('click', () => openBillspherePayment(plan));

    plansGrid.appendChild(fragment);
  });
}

trialBtn.addEventListener('click', () => {
  openBillspherePayment(plans[1]);
});

renderPlans();
