# BillSphere E-learning Frontend

This React application includes a learner-facing BillSphere integration at
`/customer/learning`. BillSphere remains the source of truth for e-learning
plans, subscriptions, payments, invoices, and feature entitlements.

## Run Locally

Start the BillSphere backend first at `http://127.0.0.1:8000`. Then run the
frontend:

```powershell
npm install
npm run dev
```

Open the URL printed by Vite, sign in, and visit:

```text
/customer/learning
```

The integration uses `http://127.0.0.1:8000/api/v1` by default. To point the
frontend at another BillSphere instance, create `frontend/.env.local`:

```text
VITE_API_BASE_URL=https://your-billsphere-host/api/v1
```

## Learner Flow

- Plans are fetched live with the `elearning` platform filter.
- The active learner subscription is matched to its BillSphere plan.
- Feature access is derived centrally by `useLearnerEntitlements()`.
- Enrollment uses BillSphere checkout and waits for payment confirmation.
- Failed or declined payments show BillSphere's failure reason.
- Invoice PDFs can be downloaded from the learner billing history.
- A single expired access check retries token refresh once through `/refresh`.

Plan entitlements are read from BillSphere's `feature_entitlements` field. The
backend should seed e-learning plans with keys such as `catalog_tier`,
`can_issue_certificate`, `mentor_sessions`, and `can_download_offline` when
those capabilities are intended for a plan.

## Useful Commands

```powershell
npm run dev
npm run build
npm run lint
```

The repository currently has unrelated pre-existing type and lint errors in
other screens. The learner integration files can be checked independently with
the targeted ESLint command used during development.

---

## React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])

```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])

```
