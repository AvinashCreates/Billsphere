import React from 'react';
import { Palette } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

interface ThemeSwitcherProps {
  compact?: boolean;
  showLabel?: boolean;
}

export function ThemeSwitcher({ compact = true, showLabel = false }: ThemeSwitcherProps) {
  const { theme, mode, setTheme, setMode } = useTheme();
  const [isOpen, setIsOpen] = React.useState(false);

  const themeOptions = [
    { id: 'ledger' as const, name: 'Ledger', emoji: '🌿' },
    { id: 'gold' as const, name: 'Gold', emoji: '✨' },
    { id: 'slate' as const, name: 'Slate', emoji: '🔷' },
  ];

  if (compact) {
    return (
      <div style={{ position: 'relative' }}>
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          title="Theme switcher"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '40px',
            height: '40px',
            borderRadius: '8px',
            border: 'none',
            background: 'var(--surface-1)',
            color: 'var(--text-primary)',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            fontSize: '0.875rem',
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLElement).style.background = 'var(--accent)';
            (e.currentTarget as HTMLElement).style.color = 'var(--on-accent)';
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLElement).style.background = 'var(--surface-1)';
            (e.currentTarget as HTMLElement).style.color = 'var(--text-primary)';
          }}
        >
          <Palette size={18} />
        </button>

        {isOpen && (
          <div
            style={{
              position: 'absolute',
              top: '100%',
              right: 0,
              marginTop: '0.5rem',
              background: 'var(--surface-1)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              zIndex: 1000,
              minWidth: '200px',
              boxShadow: '0 10px 25px rgba(0, 0, 0, 0.2)',
            }}
          >
            {/* Color Themes */}
            <div style={{ padding: '0.5rem' }}>
              <div style={{
                fontSize: '0.75rem',
                fontWeight: 500,
                textTransform: 'uppercase',
                color: 'var(--text-muted)',
                padding: '0.5rem 0.75rem',
                marginBottom: '0.25rem',
              }}>
                Theme
              </div>
              {themeOptions.map((option) => (
                <button
                  key={option.id}
                  type="button"
                  onClick={() => {
                    setTheme(option.id);
                    setIsOpen(false);
                  }}
                  style={{
                    width: '100%',
                    padding: '0.5rem 0.75rem',
                    textAlign: 'left',
                    border: 'none',
                    background: theme === option.id ? 'var(--accent)' : 'transparent',
                    color: theme === option.id ? 'var(--on-accent)' : 'var(--text-primary)',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    transition: 'all 0.2s ease',
                    borderRadius: '4px',
                  }}
                  onMouseEnter={(e) => {
                    if (theme !== option.id) {
                      (e.currentTarget as HTMLElement).style.background = 'var(--surface-0)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (theme !== option.id) {
                      (e.currentTarget as HTMLElement).style.background = 'transparent';
                    }
                  }}
                >
                  <span style={{ marginRight: '0.5rem' }}>{option.emoji}</span>
                  {option.name}
                  {theme === option.id && ' ✓'}
                </button>
              ))}
            </div>

            <div style={{
              height: '1px',
              background: 'var(--border)',
              margin: '0.5rem 0',
            }} />

            {/* Light/Dark Mode */}
            <div style={{ padding: '0.5rem' }}>
              <div style={{
                fontSize: '0.75rem',
                fontWeight: 500,
                textTransform: 'uppercase',
                color: 'var(--text-muted)',
                padding: '0.5rem 0.75rem',
                marginBottom: '0.25rem',
              }}>
                Mode
              </div>
              <button
                type="button"
                onClick={() => {
                  setMode('light');
                  setIsOpen(false);
                }}
                style={{
                  width: '100%',
                  padding: '0.5rem 0.75rem',
                  textAlign: 'left',
                  border: 'none',
                  background: mode === 'light' ? 'var(--accent)' : 'transparent',
                  color: mode === 'light' ? 'var(--on-accent)' : 'var(--text-primary)',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  transition: 'all 0.2s ease',
                  borderRadius: '4px',
                }}
                onMouseEnter={(e) => {
                  if (mode !== 'light') {
                    (e.currentTarget as HTMLElement).style.background = 'var(--surface-0)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (mode !== 'light') {
                    (e.currentTarget as HTMLElement).style.background = 'transparent';
                  }
                }}
              >
                ☀️ Light
                {mode === 'light' && ' ✓'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setMode('dark');
                  setIsOpen(false);
                }}
                style={{
                  width: '100%',
                  padding: '0.5rem 0.75rem',
                  textAlign: 'left',
                  border: 'none',
                  background: mode === 'dark' ? 'var(--accent)' : 'transparent',
                  color: mode === 'dark' ? 'var(--on-accent)' : 'var(--text-primary)',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  transition: 'all 0.2s ease',
                  borderRadius: '4px',
                }}
                onMouseEnter={(e) => {
                  if (mode !== 'dark') {
                    (e.currentTarget as HTMLElement).style.background = 'var(--surface-0)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (mode !== 'dark') {
                    (e.currentTarget as HTMLElement).style.background = 'transparent';
                  }
                }}
              >
                🌙 Dark
                {mode === 'dark' && ' ✓'}
              </button>
            </div>
          </div>
        )}

        {/* Close menu when clicking outside */}
        {isOpen && (
          <div
            style={{
              position: 'fixed',
              inset: 0,
              zIndex: 999,
            }}
            onClick={() => setIsOpen(false)}
          />
        )}
      </div>
    );
  }

  // Full version for Settings
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {showLabel && (
        <div>
          <h3 style={{ marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
            Theme Switcher
          </h3>
        </div>
      )}
      {/* Content would go here for expanded version */}
    </div>
  );
}
