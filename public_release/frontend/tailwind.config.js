/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx,js,jsx}"],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        // Stellar Obsidian Palette
        void: {
          DEFAULT: "#050505",
          light: "#0A0A0A",
          dark: "#000000",
        },
        plasma: {
          DEFAULT: "#00F0FF",
          glow: "rgba(0, 240, 255, 0.5)",
        },
        solar: {
          DEFAULT: "#FFD700",
          glow: "rgba(255, 215, 0, 0.5)",
        },
        nebula: {
          DEFAULT: "#BC13FE",
          glow: "rgba(188, 19, 254, 0.5)",
        },
        redshift: {
          DEFAULT: "#FF0055",
          glow: "rgba(255, 0, 85, 0.5)",
        },
        glass: {
          DEFAULT: "rgba(255, 255, 255, 0.05)",
          border: "rgba(255, 255, 255, 0.1)",
        },
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))'
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))'
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))'
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))'
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))'
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))'
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))'
        },
        // Dyson Sphere Specific Colors
        dyson: {
          void: '#050505',
          plasma: '#FF3333',
          amber: '#FFB300',
          gold: '#FFD700',
          teal: '#008080',
          glass: 'rgba(10, 10, 10, 0.6)',
        }
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)'
      },
      keyframes: {
        'accordion-down': {
          from: {
            height: '0'
          },
          to: {
            height: 'var(--radix-accordion-content-height)'
          }
        },
        'accordion-up': {
          from: {
            height: 'var(--radix-accordion-content-height)'
          },
          to: {
            height: '0'
          }
        },
        'breathe': {
          '0%, 100%': { opacity: '0.8', transform: 'scale(1)' },
          '50%': { opacity: '0.4', transform: 'scale(1.02)' },
        },
        'plasma-pulse': {
          '0%, 100%': { boxShadow: '0 0 5px var(--dyson-plasma), 0 0 10px var(--dyson-plasma)' },
          '50%': { boxShadow: '0 0 20px var(--dyson-plasma), 0 0 30px var(--dyson-plasma)' },
        },
        'rotate-slow': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        }
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        'breathe': 'breathe 8s ease-in-out infinite',
        'plasma-pulse': 'plasma-pulse 2s infinite',
        'rotate-slow': 'rotate-slow 20s linear infinite',
      }
    }
  },
  plugins: [require("tailwindcss-animate")],
}
