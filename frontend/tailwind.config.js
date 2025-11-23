/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'void-blue': 'var(--color-void-blue)',
        'deep-space': 'var(--color-deep-space)',
        'quantum-teal': 'var(--color-quantum-teal)',
        'plasma-pink': 'var(--color-plasma-pink)',
        'entropy-orange': 'var(--color-entropy-orange)',
        'supernova-white': 'var(--color-supernova-white)',
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px var(--color-quantum-teal)' },
          '100%': { boxShadow: '0 0 20px var(--color-quantum-teal), 0 0 10px var(--color-quantum-teal)' },
        }
      }
    },
  },
  plugins: [],
}

