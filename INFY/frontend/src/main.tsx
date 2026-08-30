import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { ToastProvider } from "./components/ToastProvider";
import { ThemeProvider } from "./contexts/ThemeContext";
import { AuthProvider } from "./contexts/AuthContext";
import { LearnerEntitlementsProvider } from "./contexts/LearnerEntitlementsProvider";
import ErrorBoundary from "./components/ErrorBoundary";
// Import theme tokens FIRST, before any component styles
import "./styles/themes.css";
import "./style.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <ThemeProvider>
        <AuthProvider>
          <LearnerEntitlementsProvider>
            <ToastProvider>
              <App />
            </ToastProvider>
          </LearnerEntitlementsProvider>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  </React.StrictMode>
);