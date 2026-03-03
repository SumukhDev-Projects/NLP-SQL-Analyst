/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#080a0f',
          900: '#0f1319',
          850: '#131820',
          800: '#171e28',
          700: '#1e2836',
          600: '#263244',
        },
        amber: {
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
        },
        slate: {
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
        }
      },
      fontFamily: {
        mono: ['"IBM Plex Mono"', '"Fira Code"', 'monospace'],
        display: ['"Libre Baskerville"', 'Georgia', 'serif'],
        sans: ['"DM Sans"', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease forwards',
        'slide-up': 'slideUp 0.35s ease forwards',
        'blink': 'blink 1.2s step-end infinite',
      },
      keyframes: {
        fadeIn: { from: { opacity: '0' }, to: { opacity: '1' } },
        slideUp: {
          from: { opacity: '0', transform: 'translateY(12px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        blink: { '0%, 100%': { opacity: '1' }, '50%': { opacity: '0' } },
      }
    }
  },
  plugins: []
}
