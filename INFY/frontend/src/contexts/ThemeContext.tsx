import React, { createContext, useContext, useEffect, useState } from 'react';

type ColorTheme = 'ledger' | 'gold' | 'slate';
type Mode = 'light' | 'dark';

type ThemeContextType = {
  theme: ColorTheme;
  mode: Mode;
  setTheme: (t: ColorTheme) => void;
  setMode: (m: Mode) => void;
  toggleMode: () => void;
  // Backward compatibility
  toggle: () => void;
};

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider = ({ children }: { children: React.ReactNode }) => {
  const [colorTheme, setColorThemeState] = useState<ColorTheme>('ledger');
  const [mode, setModeState] = useState<Mode>('light');

  useEffect(() => {
    // Read saved theme and mode from localStorage
    const savedTheme = (localStorage.getItem('billsphere-theme') as ColorTheme | null) || 'ledger';
    const savedMode = (localStorage.getItem('billsphere-mode') as Mode | null);
    
    // Determine mode: use saved, or fall back to OS preference, or default to light
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialMode = savedMode || (prefersDark ? 'dark' : 'light');

    setColorThemeState(savedTheme);
    setModeState(initialMode);

    // Apply to DOM before render to prevent flash
    document.documentElement.setAttribute('data-theme', savedTheme);
    document.documentElement.setAttribute('data-mode', initialMode);
    // Keep backward compatibility with dark class
    document.documentElement.classList.toggle('dark', initialMode === 'dark');
  }, []);

  function setTheme(t: ColorTheme) {
    setColorThemeState(t);
    document.documentElement.setAttribute('data-theme', t);
    localStorage.setItem('billsphere-theme', t);
  }

  function setMode(m: Mode) {
    setModeState(m);
    document.documentElement.setAttribute('data-mode', m);
    document.documentElement.classList.toggle('dark', m === 'dark');
    localStorage.setItem('billsphere-mode', m);
  }

  function toggleMode() {
    setMode(mode === 'dark' ? 'light' : 'dark');
  }

  return (
    <ThemeContext.Provider value={{ theme: colorTheme, mode, setTheme, setMode, toggleMode, toggle: toggleMode }}>
      {children}
    </ThemeContext.Provider>
  );
};

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
  return ctx;
}
