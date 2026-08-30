# BillSphere Token System Documentation

## Overview

BillSphere uses a **token-based, swappable theming system** powered by CSS custom properties. This allows the entire UI to switch between three named color themes (Ledger, Gold, Slate) and between light/dark modes without touching component code.

All tokens are defined in `themes.css` and automatically applied based on the current theme and mode selected by the user.

---

## Token Reference

### Surface Colors

Used for page and card backgrounds.

- **`--surface-0`** - Page background (outermost layer)
- **`--surface-1`** - Card/panel background (card layer)

**Usage:**
```css
body {
  background: var(--surface-0);
}

.card {
  background: var(--surface-1);
}
```

---

### Text Colors

Semantic text color hierarchy.

- **`--text-primary`** - Main body text, headings, high contrast content
- **`--text-secondary`** - Secondary text, labels, subheadings (slightly muted)
- **`--text-muted`** - Helper text, captions, low-emphasis content (even more muted)

**Usage:**
```css
h1, h2, h3 {
  color: var(--text-primary);
}

p {
  color: var(--text-primary);
}

.helper-text {
  color: var(--text-muted);
}

.label {
  color: var(--text-secondary);
}
```

**Best Practice:** Avoid jumping more than one level. Don't use `--text-muted` on `--surface-0` if you can use `--text-secondary` instead (contrast may fail WCAG AA).

---

### Border & Divider

Used for subtle lines, dividers, and borders.

- **`--border`** - Default border color for all components (inputs, cards, dividers)

**Usage:**
```css
input {
  border: 1px solid var(--border);
}

.divider {
  border-top: 1px solid var(--border);
}

.card {
  border: 1px solid var(--border);
}
```

---

### Accent / Interactive

Primary interactive elements — buttons, links, active states, and focus rings.

- **`--accent`** - Default accent color (primary buttons, links, active states)
- **`--accent-hover`** - Accent hover/pressed state
- **`--on-accent`** - Text/content color when placed ON an accent-filled background

**Usage:**
```css
.btn-primary {
  background: var(--accent);
  color: var(--on-accent);  /* For proper contrast */
}

.btn-primary:hover {
  background: var(--accent-hover);
}

a {
  color: var(--accent);
}

a:focus {
  outline: 2px solid var(--accent);
}
```

**Important for Gold Theme:** 
- In the Gold theme, `--on-accent` is **always dark** (near-black) in both light AND dark mode.
- This is intentional: gold is a light-to-mid tone, so text on a gold button must stay dark for proper contrast.
- Do NOT "fix" this to match light/dark patterns in Ledger or Slate themes.

---

### Status Colors

Semantic colors for success, warning, and error states.

- **`--success`** - Positive/paid/active state (green-based)
- **`--warning`** - Neutral/pending/caution state (orange/amber-based)
- **`--danger`** - Error/failed/past-due state (red-based)

**Usage:**
```css
.badge-success {
  background: var(--success);
  color: white;
}

.badge-warning {
  background: var(--warning);
  color: var(--on-accent); /* Usually dark for gold, depends on theme */
}

.badge-danger {
  background: var(--danger);
  color: white;
}

/* In subscription/billing context */
.status-paid,
.status-active {
  color: var(--success);
}

.status-past-due,
.status-failed {
  color: var(--danger);
}

.status-trialing,
.status-pending {
  color: var(--warning);
}
```

---

### Typography Tokens

Font stack and sizing.

- **`--font-sans`** - Default UI font (Inter, system-ui, sans-serif)
- **`--font-voice`** - Premium/serif font for special accents (Fraunces, Georgia, serif)
- **`--radius`** - Default border radius (10px) — use everywhere for consistency

**Usage:**
```css
body {
  font-family: var(--font-sans);
}

.badge {
  border-radius: var(--radius);
}

.card {
  border-radius: var(--radius);
}

/* ONLY on special highlights: plan price, invoice total, dashboard headlines */
.price {
  font-family: var(--font-voice);
  color: var(--accent);
}

.invoice-total {
  font-family: var(--font-voice);
  font-size: 2rem;
  font-weight: 500;
  color: var(--accent);
}
```

**Typography Rules:**
1. Use only **400 (regular)** and **500 (medium)** weights — no bold-for-emphasis.
2. Apply `--font-voice` to **ONE element per screen max**: plan price, invoice total, dashboard headline balance/usage.
3. Never use `--font-voice` for body copy, buttons, navigation, or labels.
4. Keep all copy in **sentence case** — no Title Case, no ALL CAPS, no exclamation marks in system messages.

---

## Three Themes Explained

### 1. Ledger (Default)

**Palette:** Calm fintech navy + green  
**Accent (Light):** `#3D6E5C` (teal/forest green)  
**Accent (Dark):** `#4E8E77` (brighter green)  
**Best for:** General-purpose, professional, financial applications  
**Vibe:** Trustworthy, stable, corporate

### 2. Gold (Premium)

**Palette:** Luxury black/white + gold  
**Accent (Light):** `#B8892B` (deep gold)  
**Accent (Dark):** `#D4AF37` (bright champagne gold)  
**Best for:** Premium tier customers, exclusive features, high-end product marketing  
**Vibe:** Luxury, premium, exclusive  

**⚠️ Special rule for Gold:**
- `--on-accent` is always dark (`#1A1400` light mode, `#17130A` dark mode).
- Do NOT flip it to white for "better tradition." Gold is inherently light; dark text reads better.

### 3. Slate (Neutral)

**Palette:** Neutral admin/dashboard-dense screens  
**Accent (Light):** `#3B5DE0` (royal blue)  
**Accent (Dark):** `#6B8AF0` (sky blue)  
**Best for:** Admin dashboards, data-dense interfaces, neutral contexts  
**Vibe:** Calm, professional, analytical

---

## Applying Tokens to New Components

### Step 1: Replace Hardcoded Colors

**Before:**
```css
.card {
  background: #ffffff;
  border: 1px solid #e2e4e0;
  color: #0f1a2b;
}
```

**After:**
```css
.card {
  background: var(--surface-1);
  border: 1px solid var(--border);
  color: var(--text-primary);
}
```

### Step 2: Use Semantic Token Names

Map your intent to the right token:
- Background? → `var(--surface-0)` or `var(--surface-1)`
- Text? → `var(--text-primary)` / `var(--text-secondary)` / `var(--text-muted)`
- Interactive? → `var(--accent)` / `var(--accent-hover)`
- Status? → `var(--success)` / `var(--warning)` / `var(--danger)`
- Dividers? → `var(--border)`

### Step 3: Test Across Themes

Always test your component in all three themes × both modes (6 combinations):
1. Ledger + Light
2. Ledger + Dark
3. Gold + Light
4. Gold + Dark
5. Slate + Light
6. Slate + Dark

Pay special attention to **contrast**, especially:
- `--text-muted` on `--surface-0`
- `--on-accent` on `--accent` (especially in Gold theme)
- `--text-secondary` on lighter surfaces

---

## Tailwind Integration

BillSphere uses Tailwind CSS. When styling with Tailwind classes, avoid hardcoding colors:

**❌ Don't:**
```jsx
<div className="bg-[#0B0B0C] text-[#F5F1E6]">
  <button className="bg-[#D4AF37] hover:bg-[#E0BE55]">
    Click me
  </button>
</div>
```

**✅ Do:**
```jsx
<div className="surface-0 text-primary">
  <button className="accent-bg hover:accent-hover">
    Click me
  </button>
</div>
```

And define the utility classes in `style.css`:
```css
.surface-0 {
  background-color: var(--surface-0);
}

.text-primary {
  color: var(--text-primary);
}

.accent-bg {
  background-color: var(--accent);
  color: var(--on-accent);
}

.accent-bg:hover {
  background-color: var(--accent-hover);
}
```

---

## Common Patterns

### Status Badge

```tsx
function StatusBadge({ status }: { status: 'active' | 'pending' | 'failed' }) {
  const colorMap = {
    active: 'var(--success)',
    pending: 'var(--warning)',
    failed: 'var(--danger)',
  };

  return (
    <span style={{
      display: 'inline-block',
      padding: '0.25rem 0.75rem',
      borderRadius: 'var(--radius)',
      backgroundColor: colorMap[status],
      color: 'white',
      fontSize: '0.875rem',
      fontWeight: 500,
    }}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}
```

### Interactive Button

```tsx
function Button({ children, variant = 'primary' }: any) {
  const styles = {
    primary: {
      background: 'var(--accent)',
      color: 'var(--on-accent)',
    },
    secondary: {
      background: 'transparent',
      color: 'var(--text-primary)',
      border: '1px solid var(--border)',
    },
  };

  return (
    <button style={{
      padding: '0.75rem 1.5rem',
      borderRadius: 'var(--radius)',
      border: 'none',
      cursor: 'pointer',
      transition: 'all 0.2s ease',
      ...styles[variant],
    }}>
      {children}
    </button>
  );
}
```

### Form Input

```tsx
<input
  type="text"
  style={{
    background: 'var(--surface-1)',
    color: 'var(--text-primary)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: '0.5rem 0.75rem',
  }}
  onFocus={(e) => {
    e.currentTarget.style.borderColor = 'var(--accent)';
  }}
  onBlur={(e) => {
    e.currentTarget.style.borderColor = 'var(--border)';
  }}
/>
```

---

## Accessing Tokens in React

Use the `useTheme()` hook to detect the current theme and mode:

```tsx
import { useTheme } from '../contexts/ThemeContext';

export function MyComponent() {
  const { theme, mode } = useTheme();

  return (
    <div>
      <p>Current theme: {theme}</p>
      <p>Current mode: {mode}</p>
    </div>
  );
}
```

To change theme or mode:

```tsx
const { setTheme, setMode } = useTheme();

<button onClick={() => setTheme('gold')}>
  Switch to Gold Theme
</button>

<button onClick={() => setMode('dark')}>
  Switch to Dark Mode
</button>
```

---

## Accessibility Notes

### Contrast

All token combinations have been tested for WCAG AA compliance. However:

1. **Don't combine tokens arbitrarily.** Stick to the recommended pairs:
   - Text: `--text-primary` / `--text-secondary` / `--text-muted` on `--surface-0` / `--surface-1`
   - Status: `--success` / `--warning` / `--danger` typically on white/light text
   - Gold theme: `--on-accent` is always dark—never override to white

2. **Test muted text carefully.** `--text-muted` on `--surface-0` is intentionally low contrast for "hints." Don't use it for critical information.

3. **Focus rings.** Always use `var(--accent)` for focus rings:
   ```css
   :focus-visible {
     outline: 2px solid var(--accent);
     outline-offset: 2px;
   }
   ```

### Reduced Motion

Respect `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Future Extensions

**If you need a 4th theme:**
1. Add new `:root[data-theme="newtheme"][data-mode="light/dark"]` blocks to `themes.css`
2. Update the `ColorTheme` type in `ThemeContext.tsx`
3. Add it to the theme options in Settings.tsx
4. Test all 6 light/dark combinations

**If you need new tokens:**
1. Add them to `themes.css` in all three themes × both modes
2. Document them here
3. Use semantic names (`--something-primary` not `--gold-500`)

**Don't:**
- Hardcode hex values anywhere else in the codebase
- Create a 4th or 5th theme without coordination
- Override `--on-accent` for any theme except as directed
