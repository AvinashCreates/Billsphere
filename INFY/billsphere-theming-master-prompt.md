# BillSphere Theming — Master Prompt for GitHub Copilot

A single prompt to paste into the `frontend/` repo in Copilot Chat/Agent mode. It sets up a
**token-based, swappable theme system** (not hardcoded colors anywhere) with three ready-made
themes, including the gold "premium" look you asked for.

---

## The three themes (exact values — don't let Copilot invent its own)

Each theme has a light and dark mode. Same structure every time: a page background, a card
surface, three text tones, a border, and one accent color that all buttons/links/active-states
route through.

### 1. Ledger (default — calm fintech navy + green)

| Token | Light | Dark |
|---|---|---|
| `--surface-0` (page bg) | `#F4F5F2` | `#0F1A2B` |
| `--surface-1` (card bg) | `#FFFFFF` | `#16202F` |
| `--text-primary` | `#0F1A2B` | `#EDEFF3` |
| `--text-secondary` | `#4A5568` | `#A9B1BE` |
| `--text-muted` | `#8A93A3` | `#6E7889` |
| `--border` | `#E2E4E0` | `#26344A` |
| `--accent` | `#3D6E5C` | `#4E8E77` |
| `--accent-hover` | `#335C4E` | `#5EA189` |
| `--on-accent` (text on accent fill) | `#EAF3EE` | `#0B120E` |
| `--danger` | `#B3413A` | `#D8695F` |
| `--warning` | `#B98A2E` | `#D9A94A` |

### 2. Gold (premium — black/white + gold accent)

| Token | Light | Dark |
|---|---|---|
| `--surface-0` | `#FAFAF8` | `#0B0B0C` |
| `--surface-1` | `#FFFFFF` | `#17171A` |
| `--text-primary` | `#0B0B0C` | `#F5F1E6` |
| `--text-secondary` | `#55534C` | `#B8B2A0` |
| `--text-muted` | `#918E82` | `#79766A` |
| `--border` | `#E7E3D8` | `#2C2A24` |
| `--accent` | `#B8892B` | `#D4AF37` |
| `--accent-hover` | `#A67A22` | `#E0BE55` |
| `--on-accent` | `#1A1400` | `#17130A` |
| `--danger` | `#A3372F` | `#D8695F` |
| `--warning` | `#B8892B` | `#D4AF37` |

Note: gold is a light-to-mid tone, so `--on-accent` is near-black in BOTH modes — text on a gold
button/badge is always dark, never white. This is the one exception to the usual light/dark
text-flip; hardcode it that way.

### 3. Slate (neutral — for admin/dashboard-dense screens)

| Token | Light | Dark |
|---|---|---|
| `--surface-0` | `#F1F2F4` | `#111418` |
| `--surface-1` | `#FFFFFF` | `#1A1E24` |
| `--text-primary` | `#161A20` | `#E7E9EC` |
| `--text-secondary` | `#565C66` | `#9AA0AB` |
| `--text-muted` | `#8D9199` | `#6B7178` |
| `--border` | `#DEE1E5` | `#2A2F37` |
| `--accent` | `#3B5DE0` | `#6B8AF0` |
| `--accent-hover` | `#2E49B8` | `#8AA3F3` |
| `--on-accent` | `#F3F5FF` | `#0B1230` |
| `--danger` | `#C33F3F` | `#E17575` |
| `--warning` | `#B07B22` | `#D9A94A` |

Shared across all three themes, every mode:
- `--success` → `#2F7D5A` light / `#5BAE8B` dark
- `--radius`: `10px`
- `--font-sans`: `'Inter', system-ui, sans-serif`
- `--font-voice` (serif, used sparingly): `'Fraunces', Georgia, serif`

---

## Master Prompt

```
ROLE: You are building a token-based, swappable theming system for the BillSphere React +
TypeScript + Vite frontend. Right now colors are likely hardcoded per component — we're
replacing that entirely with CSS custom properties so the whole UI can switch between named
themes and between light/dark mode without touching component code.

GOAL
Three selectable color themes — "Ledger", "Gold", and "Slate" — each with a light and dark
mode, switchable at runtime from Settings, persisted across sessions, applied instantly with
no page reload.

TOKEN VALUES
Create these CSS custom properties. Use exactly the hex values below — do not invent or
adjust any of them.

/* frontend/src/styles/themes.css */

:root[data-theme="ledger"][data-mode="light"] {
  --surface-0: #F4F5F2; --surface-1: #FFFFFF;
  --text-primary: #0F1A2B; --text-secondary: #4A5568; --text-muted: #8A93A3;
  --border: #E2E4E0;
  --accent: #3D6E5C; --accent-hover: #335C4E; --on-accent: #EAF3EE;
  --danger: #B3413A; --warning: #B98A2E; --success: #2F7D5A;
}
:root[data-theme="ledger"][data-mode="dark"] {
  --surface-0: #0F1A2B; --surface-1: #16202F;
  --text-primary: #EDEFF3; --text-secondary: #A9B1BE; --text-muted: #6E7889;
  --border: #26344A;
  --accent: #4E8E77; --accent-hover: #5EA189; --on-accent: #0B120E;
  --danger: #D8695F; --warning: #D9A94A; --success: #5BAE8B;
}

:root[data-theme="gold"][data-mode="light"] {
  --surface-0: #FAFAF8; --surface-1: #FFFFFF;
  --text-primary: #0B0B0C; --text-secondary: #55534C; --text-muted: #918E82;
  --border: #E7E3D8;
  --accent: #B8892B; --accent-hover: #A67A22; --on-accent: #1A1400;
  --danger: #A3372F; --warning: #B8892B; --success: #2F7D5A;
}
:root[data-theme="gold"][data-mode="dark"] {
  --surface-0: #0B0B0C; --surface-1: #17171A;
  --text-primary: #F5F1E6; --text-secondary: #B8B2A0; --text-muted: #79766A;
  --border: #2C2A24;
  --accent: #D4AF37; --accent-hover: #E0BE55; --on-accent: #17130A;
  --danger: #D8695F; --warning: #D4AF37; --success: #5BAE8B;
}

:root[data-theme="slate"][data-mode="light"] {
  --surface-0: #F1F2F4; --surface-1: #FFFFFF;
  --text-primary: #161A20; --text-secondary: #565C66; --text-muted: #8D9199;
  --border: #DEE1E5;
  --accent: #3B5DE0; --accent-hover: #2E49B8; --on-accent: #F3F5FF;
  --danger: #C33F3F; --warning: #B07B22; --success: #2F7D5A;
}
:root[data-theme="slate"][data-mode="dark"] {
  --surface-0: #111418; --surface-1: #1A1E24;
  --text-primary: #E7E9EC; --text-secondary: #9AA0AB; --text-muted: #6B7178;
  --border: #2A2F37;
  --accent: #6B8AF0; --accent-hover: #8AA3F3; --on-accent: #0B1230;
  --danger: #E17575; --warning: #D9A94A; --success: #5BAE8B;
}

:root {
  --radius: 10px;
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-voice: 'Fraunces', Georgia, serif;
}

IMPORTANT: --on-accent for the "gold" theme is a dark color in BOTH light and dark mode
(gold is a light-to-mid tone, so text on a gold-filled button/badge must stay dark for
contrast). Do not "fix" this to match the light/dark pattern of the other two themes.

WHAT TO BUILD

1. Token stylesheet
   - Create frontend/src/styles/themes.css with the exact block above.
   - Import it once in main.tsx / App.tsx, before any component styles.

2. Refactor existing styles to consume tokens, not hardcoded colors
   - Audit style.css and any component-level styles/inline colors across
     Landing, Login, Register, Plans, CustomerDashboard, AdminDashboard, Billing,
     Payment, PaymentConfirmation, PaymentHistory, Notifications, Usage, Settings,
     HelpSupport, AdminSupport.
   - Replace every hardcoded hex/rgb color with the matching var(--token):
     backgrounds → var(--surface-0) / var(--surface-1)
     body text → var(--text-primary) / var(--text-secondary) / var(--text-muted)
     borders/dividers → var(--border)
     primary buttons, active nav items, links, focus rings → var(--accent) /
       var(--accent-hover), with text color var(--on-accent) when filled
     status badges: paid/active → var(--success), past_due/failed → var(--danger),
       trialing/pending → var(--warning)
   - Buttons/cards/badges should look identical in structure across all three themes —
     only the token values change. Don't fork component markup per theme.

3. ThemeProvider (React context)
   - Create frontend/src/context/ThemeContext.tsx exposing:
     { theme: 'ledger' | 'gold' | 'slate', mode: 'light' | 'dark',
       setTheme, setMode, toggleMode }
   - On mount, read saved theme/mode from localStorage (keys: "billsphere-theme",
     "billsphere-mode"); if none saved, default mode to the user's OS preference via
     `window.matchMedia('(prefers-color-scheme: dark)')` and default theme to "ledger".
   - On every change, write both `data-theme` and `data-mode` attributes onto
     `document.documentElement` and persist the new values to localStorage.
   - Wrap the app root in <ThemeProvider> in main.tsx.

4. Theme switcher UI (Settings page)
   - Add a "Appearance" section to Settings.tsx with:
     a) three theme swatches (Ledger / Gold / Slate) shown as small circular or
        rounded preview chips using each theme's accent + surface colors, selectable,
        with a checkmark or ring on the active one
     b) a light/dark mode toggle (segmented control or switch)
   - Changing either applies instantly across the whole app (no reload) via the
     context, and persists.
   - Also add a lightweight version of this same switcher as a small icon/menu in the
     main app header, so it's reachable from anywhere, not just Settings.

5. Accessibility
   - Verify text/background contrast meets WCAG AA for every theme × mode combination,
     especially gold's --on-accent on --accent, and --text-muted on --surface-0.
   - Keep visible keyboard focus rings using var(--accent) as the ring color in every
     theme.
   - Respect prefers-reduced-motion for the theme-switch transition (a simple opacity
     crossfade under 150ms is fine; skip it entirely if reduced motion is set).

6. Typography rules (apply the same way in every theme — don't restyle type per theme)
   - Two weights only: 400 regular, 500 medium. No bold-for-emphasis.
   - var(--font-sans) for all UI chrome, labels, buttons, nav, table data.
   - var(--font-voice) reserved for ONE element per screen: the plan price on the
     Plans page, the invoice total on Billing/PaymentConfirmation, and the dashboard's
     headline balance/usage number. Never for body copy, buttons, or nav.
   - Sentence case everywhere in copy (buttons, headings, labels) — no Title Case, no
     ALL CAPS, no exclamation marks in system messages.

CONSTRAINTS
- No component should import or reference a raw hex value. If a one-off color is truly
  needed, add a new named token to themes.css instead of inlining it.
- Don't add a 4th theme or alter the given hex values — extend the pattern later if asked.
- Keep the theme switch synchronous and instant; no flash of unstyled/wrong-theme content
  on page load (read localStorage before first paint, e.g. in an inline script in index.html
  or via a blocking effect before render).

DELIVERABLES
- frontend/src/styles/themes.css with all three themes × two modes.
- frontend/src/context/ThemeContext.tsx.
- Refactored components with zero hardcoded colors.
- Appearance section in Settings.tsx + header quick-switcher.
- A short frontend/src/styles/README.md documenting the token names and when to use each
  (surface vs text vs border vs accent vs status colors), so future pages stay consistent.

Ask me to see the current style.css or any component's existing color usage if you need it
before starting the refactor — don't guess at what's already hardcoded.
```

---

## Notes

- **Gold's contrast rule matters more than it looks.** Gold accents are notorious for failing
  contrast when white text is dropped on them by habit (that's the "Title Case gold button on
  a landing page" tell of a cheap premium look). The prompt hardcodes dark `--on-accent` for
  gold in both modes specifically to avoid that.
- If you want the theme to also reflect **who's using the app** — e.g. Gold reserved for
  Premium-tier customers only, Ledger/Slate for everyone else — that's a small addition:
  default `theme` based on the customer's current plan from BillSphere's subscription data,
  while still letting them override it manually in Settings. Say the word and I'll fold that
  into the prompt.
- Same file works for both the Spotify-style app and the e-learning app from before, if you
  want a consistent visual identity across all three surfaces — just point Copilot at that
  repo's own `styles` folder instead.
