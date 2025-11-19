# Industriverse White-Label Platform - Frontend Vision

**Version**: 2.0.0
**Last Updated**: November 19, 2024
**Status**: Complete Design System & Architecture

## Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [Domain Architecture](#domain-architecture)
3. [Thermodynamic Aesthetic](#thermodynamic-aesthetic)
4. [Design System](#design-system)
5. [Technology Stack](#technology-stack)
6. [Key User Experiences](#key-user-experiences)
7. [Component Library](#component-library)
8. [Animation & Interactions](#animation--interactions)
9. [Performance & SEO](#performance--seo)
10. [Responsive Design](#responsive-design)

---

## Design Philosophy

### Core Principles

**1. WOW Factor from First Glance**
- Every interface must make an immediate visual impact
- Rich, premium aesthetics that convey technological sophistication
- No generic designs - every element feels intentional and high-end

**2. Thermodynamic Visual Language**
- Energy flows, heat maps, plasma effects throughout
- Physics-based animations (particles, forces, momentum)
- Data visualization inspired by thermodynamics and fluid dynamics

**3. Intuitive Value Communication**
- Visual hierarchy that guides users to key value propositions
- Progressive disclosure - complexity revealed as needed
- Clear tier differentiation through visual treatment

**4. Premium Industrial Aesthetic**
- Dark, sleek interfaces with accent lighting
- Glassmorphism and depth effects
- Precision engineering feel - every pixel matters

### Visual Inspiration

- **Cyberpunk 2077**: Neon accents, holographic interfaces, depth
- **Tesla Dashboard**: Clean data visualization, real-time updates
- **Figma**: Smooth interactions, performant animations
- **Linear**: Premium dark mode, subtle gradients
- **Vercel**: Sharp typography, precise spacing

---

## Domain Architecture

### Primary Domain: industriverse.ai

**Purpose**: Main marketing site and platform hub

**Subdomain Structure**:

```
industriverse.ai/
├── /                          # Marketing homepage
├── /platform                  # Platform overview
├── /partners                  # Partner onboarding
├── /pricing                   # Tier comparison
├── /about                     # Company story
└── /contact                   # Contact form

widgets.industriverse.ai
├── /embed/{widget-type}       # iframe embeds
├── /preview                   # Widget showcase
└── /sdk                       # SDK documentation

partners.industriverse.ai
├── /login                     # Partner authentication
├── /dashboard                 # Analytics & overview
├── /dacs                      # DAC management
├── /billing                   # Revenue & invoices
├── /analytics                 # Detailed metrics
├── /theme                     # Theme customizer
└── /support                   # Help & docs

marketplace.industriverse.ai (Tier 3)
├── /                          # Marketplace home
├── /explore                   # Browse insights
├── /insight/{utid}            # Insight detail
├── /sell                      # List insight
├── /portfolio                 # User's insights
└── /transactions              # Purchase history

docs.industriverse.ai
├── /                          # Documentation hub
├── /api                       # API reference
├── /guides                    # Integration guides
├── /widgets                   # Widget docs
└── /examples                  # Code examples

cdn.industriverse.ai
├── /widget-sdk/v2.js          # Widget SDK
├── /themes/                   # Theme bundles
└── /assets/                   # Static assets
```

### Secondary Domain: thermodynasty.com

**Purpose**: I³ Intelligence Platform & Research Portal

```
thermodynasty.com/
├── /                          # I³ platform overview
├── /research                  # Research explorer
├── /shadow-twin               # 3D visualization
├── /papers                    # Paper database
├── /simulations               # MSEP.one interface
└── /discover                  # Insight discovery

labs.thermodynasty.com
├── /rdr                       # RDR engine interface
├── /obmi                      # OBMI operator playground
├── /embeddings                # 6D embedding visualizer
└── /experiments               # Research experiments
```

---

## Thermodynamic Aesthetic

### Core Visual Elements

**1. Plasma Effects**
- Animated gradient borders
- Glowing edges with energy flow
- Pulsing accents on interactive elements

```css
/* Plasma Border */
.plasma-border {
  position: relative;
  border: 2px solid transparent;
  background: linear-gradient(135deg, #0A4B5C, #1A1F3A) padding-box,
              linear-gradient(135deg, #FF6B35, #9B59B6, #2ECC71) border-box;
  animation: plasma-flow 3s ease-in-out infinite;
}

@keyframes plasma-flow {
  0%, 100% { filter: hue-rotate(0deg) brightness(1); }
  50% { filter: hue-rotate(30deg) brightness(1.2); }
}
```

**2. Energy Flow Animations**
- Particles flowing along paths
- Heat map color transitions
- Thermodynamic topology visualizations

**3. Glow Effects**
- Soft box-shadows with colored glows
- Text shadows for luminosity
- Button hover states with energy buildup

```css
/* Glow Effect */
.glow-accent {
  box-shadow:
    0 0 10px rgba(255, 107, 53, 0.3),
    0 0 20px rgba(255, 107, 53, 0.2),
    0 0 30px rgba(255, 107, 53, 0.1);
  transition: box-shadow 0.3s ease;
}

.glow-accent:hover {
  box-shadow:
    0 0 15px rgba(255, 107, 53, 0.5),
    0 0 30px rgba(255, 107, 53, 0.3),
    0 0 45px rgba(255, 107, 53, 0.2);
}
```

**4. Depth & Layers**
- Glassmorphism for elevated elements
- Multi-layer parallax effects
- Z-index hierarchy for visual depth

### Color System

**Cosmic Theme** (Primary):
```css
:root {
  /* Primary Palette */
  --color-primary: #0A4B5C;           /* Deep Teal */
  --color-primary-light: #1A6D82;     /* Lighter Teal */
  --color-primary-dark: #083A4A;      /* Darker Teal */

  /* Accent Colors */
  --color-accent: #FF6B35;            /* Vibrant Orange */
  --color-entropy: #9B59B6;           /* Purple */
  --color-proof: #2ECC71;             /* Green */
  --color-energy: #F1C40F;            /* Gold */

  /* Background Gradients */
  --bg-cosmic: linear-gradient(135deg, #0A0E27 0%, #1A1F3A 100%);
  --bg-plasma: linear-gradient(135deg,
    rgba(10, 75, 92, 0.3) 0%,
    rgba(155, 89, 182, 0.3) 50%,
    rgba(46, 204, 113, 0.3) 100%
  );

  /* Glassmorphism */
  --glass-bg: rgba(26, 31, 58, 0.7);
  --glass-border: rgba(255, 255, 255, 0.1);
  --glass-blur: blur(20px);

  /* Text */
  --text-primary: #FFFFFF;
  --text-secondary: #B8C5D6;
  --text-muted: #6B7280;

  /* Interactive States */
  --hover-glow: rgba(255, 107, 53, 0.3);
  --active-glow: rgba(255, 107, 53, 0.5);
}
```

**Chrome Theme** (Professional Light):
```css
:root {
  --color-primary: #1E40AF;           /* Professional Blue */
  --color-accent: #F59E0B;            /* Amber */
  --bg-chrome: linear-gradient(135deg, #F9FAFB 0%, #E5E7EB 100%);
  --text-primary: #111827;
  --glass-bg: rgba(255, 255, 255, 0.9);
}
```

### Typography

**Font Stack**:
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  /* Primary Font */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

  /* Monospace (code, data) */
  --font-mono: 'JetBrains Mono', 'Fira Code', Consolas, monospace;

  /* Display (headings) */
  --font-display: 'Inter', sans-serif;

  /* Font Sizes */
  --text-xs: 0.75rem;     /* 12px */
  --text-sm: 0.875rem;    /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg: 1.125rem;    /* 18px */
  --text-xl: 1.25rem;     /* 20px */
  --text-2xl: 1.5rem;     /* 24px */
  --text-3xl: 1.875rem;   /* 30px */
  --text-4xl: 2.25rem;    /* 36px */
  --text-5xl: 3rem;       /* 48px */
  --text-6xl: 3.75rem;    /* 60px */

  /* Line Heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;

  /* Font Weights */
  --font-light: 300;
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  --font-extrabold: 800;
}
```

**Typography Scale**:
```css
/* Hero Heading */
h1, .h1 {
  font-size: var(--text-6xl);
  font-weight: var(--font-extrabold);
  line-height: var(--leading-tight);
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, #FFFFFF 0%, #B8C5D6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Section Heading */
h2, .h2 {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  line-height: var(--leading-tight);
}

/* Subsection Heading */
h3, .h3 {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-normal);
}

/* Body Text */
p, .body {
  font-size: var(--text-base);
  font-weight: var(--font-normal);
  line-height: var(--leading-relaxed);
  color: var(--text-secondary);
}

/* Caption/Small */
.caption {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
```

---

## Design System

### Spacing Scale

```css
:root {
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-20: 5rem;     /* 80px */
  --space-24: 6rem;     /* 96px */
}
```

### Border Radius

```css
:root {
  --radius-sm: 0.375rem;    /* 6px */
  --radius-md: 0.5rem;      /* 8px */
  --radius-lg: 0.75rem;     /* 12px */
  --radius-xl: 1rem;        /* 16px */
  --radius-2xl: 1.5rem;     /* 24px */
  --radius-full: 9999px;    /* Pill */
}
```

### Shadows

```css
:root {
  /* Standard Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);

  /* Glow Shadows (Thermodynamic) */
  --shadow-glow-sm: 0 0 10px rgba(255, 107, 53, 0.2);
  --shadow-glow-md: 0 0 20px rgba(255, 107, 53, 0.3);
  --shadow-glow-lg: 0 0 30px rgba(255, 107, 53, 0.4);

  /* Colored Glows */
  --shadow-glow-accent: 0 0 20px rgba(255, 107, 53, 0.4);
  --shadow-glow-entropy: 0 0 20px rgba(155, 89, 182, 0.4);
  --shadow-glow-proof: 0 0 20px rgba(46, 204, 113, 0.4);
}
```

### Motion & Transitions

```css
:root {
  /* Durations */
  --duration-fast: 150ms;
  --duration-base: 250ms;
  --duration-slow: 350ms;
  --duration-slower: 500ms;

  /* Easing Functions */
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-spring: cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

/* Standard Transition */
.transition {
  transition: all var(--duration-base) var(--ease-in-out);
}

/* Smooth Transform */
.transform {
  transition: transform var(--duration-base) var(--ease-out);
}
```

---

## Technology Stack

### Frontend Framework

**Primary**: **Next.js 14** (App Router)
- Server-side rendering for SEO
- API routes for backend integration
- Image optimization
- Built-in performance optimizations

**Alternative** (Tier 1 partners): **Vite + React 18**
- Faster dev experience
- Simpler deployment
- Better for embedded widgets

### UI Libraries

**Core**:
- **React 18**: Component framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Utility-first styling
- **Framer Motion**: Advanced animations
- **Three.js + React Three Fiber**: 3D visualizations (Shadow Twin)

**Components**:
- **Radix UI**: Accessible primitives
- **Headless UI**: Unstyled components
- **Recharts**: Data visualization charts
- **React Spring**: Physics-based animations

### State Management

- **Zustand**: Lightweight global state
- **TanStack Query**: Server state & caching
- **Jotai**: Atomic state management

### 3D & Visualization

- **Three.js**: 3D rendering (Shadow Twin)
- **D3.js**: Complex data viz
- **Visx**: React visualization primitives
- **Particles.js**: Particle effects

### Real-Time

- **Socket.io**: WebSocket connections
- **SWR**: Real-time data fetching
- **Server-Sent Events**: Live updates

### Build & Deploy

- **Vercel**: Hosting & edge functions
- **Turborepo**: Monorepo management
- **pnpm**: Fast package manager
- **GitHub Actions**: CI/CD

### Testing

- **Vitest**: Unit tests
- **Playwright**: E2E tests
- **Testing Library**: Component tests
- **Chromatic**: Visual regression

---

## Key User Experiences

### 1. Marketing Homepage (industriverse.ai)

**Goal**: WOW visitors and convert to partners

**Hero Section**:
```
[Full-screen animated background with energy particles]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

          THE FUTURE OF AMBIENT INTELLIGENCE
         Deploy Anywhere. Scale Everywhere.

    [Animated 3D visualization of interconnected systems]

        [Get Started →]    [View Demo ↗]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Features**:
- Animated particles flowing in background
- 3D rotating platform visualization
- Smooth scroll-triggered animations
- Interactive demo widget previews
- Real-time stats counter (partners, deployments, uptime)

**Sections**:
1. **Hero**: Full-screen impact, animated CTA
2. **Value Prop**: 3-card layout (Deploy, Customize, Monetize)
3. **Platform Demo**: Interactive widget carousel
4. **Tier Comparison**: Animated pricing cards
5. **Social Proof**: Partner logos with glow effects
6. **I³ Showcase**: 3D Shadow Twin demo
7. **CTA**: Glowing sign-up form

### 2. Partner Portal (partners.industriverse.ai)

**Goal**: Clear analytics, easy configuration, revenue transparency

**Dashboard Layout**:
```
┌─────────────────────────────────────────────────────────┐
│  [Logo]              Dashboard           [Profile] [🔔] │
├─────────────────────────────────────────────────────────┤
│  [Sidebar]  │  [Main Content Area]                      │
│             │                                            │
│  Dashboard  │  ┌─────────┐ ┌─────────┐ ┌─────────┐    │
│  DACs       │  │ Revenue │ │ API     │ │ Active  │    │
│  Analytics  │  │ $28.5K  │ │ Calls   │ │ Deploy  │    │
│  Theme      │  │ ↑ 12%   │ │ 125K    │ │ 3       │    │
│  Billing    │  └─────────┘ └─────────┘ └─────────┘    │
│  Support    │                                            │
│             │  [Revenue Chart - Last 30 Days]           │
│             │  [Interactive line graph with glow]       │
│             │                                            │
│             │  [Recent Activity]                        │
│             │  • Widget impression spike on acme.com    │
│             │  • New DAC deployed to production         │
│             │  • API usage approaching tier limit       │
└─────────────┴────────────────────────────────────────────┘
```

**Key Features**:
- Real-time metrics with smooth transitions
- Interactive charts with hover details
- Glassmorphism cards with depth
- Glow effects on important metrics
- Toast notifications for events
- Inline editing for configurations

### 3. Widget Showcase (widgets.industriverse.ai)

**Goal**: Let partners preview and test widgets before integration

**Layout**:
```
[Interactive Widget Gallery]

┌───────────────────────────────────────┐
│                                       │
│     [Widget Preview - Live Demo]     │
│                                       │
│   ┌─────────────────────────────┐   │
│   │                             │   │
│   │   [AI Shield Dashboard]     │   │
│   │   [Live threat simulation]  │   │
│   │                             │   │
│   └─────────────────────────────┘   │
│                                       │
│   [Theme Selector: Cosmic | Chrome]  │
│                                       │
│   [Get Embed Code]  [View Docs →]   │
│                                       │
└───────────────────────────────────────┘

[Widget Grid Below]
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ Shield │ │Complnce│ │ Threat │ │  Orb   │
└────────┘ └────────┘ └────────┘ └────────┘
```

**Features**:
- Live widget previews with real data simulation
- Theme switcher to test customization
- One-click embed code generation
- Interactive configuration panel
- Performance metrics display

### 4. Marketplace (marketplace.industriverse.ai) - Tier 3

**Goal**: Beautiful insight discovery and transaction UX

**Listing Page**:
```
[Search Bar with Filters]
┌─────────────────────────────────────────────────┐
│  🔍  Search insights...            [Filters ▼] │
└─────────────────────────────────────────────────┘

[Insight Grid]
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ [Glow Border]    │  │ [Glow Border]    │  │ [Glow Border]    │
│                  │  │                  │  │                  │
│ Quantum Error    │  │ Neural Network   │  │ Materials Sci    │
│ Correction       │  │ Optimization     │  │ Discovery        │
│                  │  │                  │  │                  │
│ Proof: 0.95 ⭐   │  │ Proof: 0.92 ⭐   │  │ Proof: 0.97 ⭐   │
│ 42 citations     │  │ 28 citations     │  │ 67 citations     │
│                  │  │                  │  │                  │
│ 100 Credits      │  │ License 50/mo    │  │ 250 Credits      │
│ [Buy Now]        │  │ [Subscribe]      │  │ [Buy Now]        │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

**Features**:
- Masonry grid layout with glowing cards
- Proof score visualized with glow intensity
- Hover effects reveal citation graph preview
- Smooth transitions between list/grid views
- Real-time availability indicators

### 5. Shadow Twin 3D (thermodynasty.com/shadow-twin)

**Goal**: Stunning 3D knowledge graph that invites exploration

**Interface**:
```
[Full-screen 3D Canvas]
┌─────────────────────────────────────────────────────────┐
│  [3D Force-Directed Graph]                       [?][⚙]│
│                                                         │
│        ●                 ●                              │
│         ╲               ╱                               │
│          ●─────●─────●                                  │
│         ╱       ╲   ╱                                   │
│        ●         ● ●                                    │
│                   │                                     │
│                   ●                                     │
│                                                         │
│  [Minimap]    [Search]    [Filters]    [Export]       │
└─────────────────────────────────────────────────────────┘

[Info Panel - Appears on node click]
┌──────────────────────────────┐
│  Paper: "Quantum Computing"  │
│  Proof Score: 0.95           │
│  Citations: 42               │
│  [View Details →]            │
└──────────────────────────────┘
```

**Features**:
- WebGL-powered 3D rendering
- Physics-based node positioning
- Glow effects on nodes based on proof score
- Smooth camera controls (orbit, zoom, pan)
- Particle effects for connections
- VR/AR mode toggle
- Export as video or image

---

## Component Library

### Buttons

**Primary Button**:
```jsx
<button className="btn-primary">
  <span>Get Started</span>
  <ArrowRight className="icon" />
</button>
```

```css
.btn-primary {
  position: relative;
  padding: 1rem 2rem;
  font-size: 1rem;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, var(--color-accent), var(--color-entropy));
  border: none;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-glow-accent);
  cursor: pointer;
  overflow: hidden;
  transition: all var(--duration-base) var(--ease-out);
}

.btn-primary::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  transition: left 0.5s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow-lg);
}

.btn-primary:hover::before {
  left: 100%;
}
```

**Ghost Button**:
```jsx
<button className="btn-ghost">
  Learn More
</button>
```

```css
.btn-ghost {
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  color: var(--text-primary);
  background: transparent;
  border: 2px solid var(--glass-border);
  border-radius: var(--radius-lg);
  backdrop-filter: var(--glass-blur);
  transition: all var(--duration-base) var(--ease-out);
}

.btn-ghost:hover {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-sm);
}
```

### Cards

**Glassmorphism Card**:
```jsx
<div className="card-glass">
  <h3>Security Essentials</h3>
  <p className="price">$5K-$15K/mo</p>
  <ul className="features">
    <li>✓ AI Shield Dashboard</li>
    <li>✓ Compliance Score</li>
    <li>✓ 4 Widgets</li>
  </ul>
  <button className="btn-primary">Get Started</button>
</div>
```

```css
.card-glass {
  padding: var(--space-8);
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-2xl);
  backdrop-filter: var(--glass-blur);
  box-shadow: var(--shadow-xl);
  transition: all var(--duration-base) var(--ease-out);
}

.card-glass:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl), var(--shadow-glow-sm);
  border-color: var(--color-accent);
}
```

**Metric Card** (Dashboard):
```jsx
<div className="metric-card">
  <div className="metric-icon">
    <DollarSign className="glow" />
  </div>
  <div className="metric-content">
    <p className="metric-label">Monthly Revenue</p>
    <h2 className="metric-value">$28,500</h2>
    <p className="metric-change positive">↑ 12% from last month</p>
  </div>
</div>
```

```css
.metric-card {
  display: flex;
  gap: var(--space-4);
  padding: var(--space-6);
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  backdrop-filter: var(--glass-blur);
}

.metric-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, var(--color-accent), var(--color-entropy));
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-glow-accent);
}

.metric-value {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: var(--space-2) 0;
}

.metric-change.positive {
  color: var(--color-proof);
}
```

### Navigation

**Top Navigation**:
```jsx
<nav className="nav-top">
  <div className="nav-logo">
    <Logo />
    <span>Industriverse</span>
  </div>

  <div className="nav-links">
    <a href="/platform">Platform</a>
    <a href="/pricing">Pricing</a>
    <a href="/docs">Docs</a>
  </div>

  <div className="nav-actions">
    <button className="btn-ghost">Sign In</button>
    <button className="btn-primary">Get Started</button>
  </div>
</nav>
```

```css
.nav-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-8);
  background: var(--glass-bg);
  border-bottom: 1px solid var(--glass-border);
  backdrop-filter: var(--glass-blur);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-links a {
  margin: 0 var(--space-4);
  color: var(--text-secondary);
  font-weight: 500;
  text-decoration: none;
  transition: color var(--duration-fast);
}

.nav-links a:hover {
  color: var(--text-primary);
}
```

### Data Visualization

**Chart Container**:
```jsx
<div className="chart-container">
  <div className="chart-header">
    <h3>Revenue Trend</h3>
    <select className="chart-period">
      <option>Last 7 days</option>
      <option>Last 30 days</option>
      <option>Last 90 days</option>
    </select>
  </div>

  <div className="chart-body">
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <defs>
          <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--color-accent)" stopOpacity={0.8} />
            <stop offset="100%" stopColor="var(--color-accent)" stopOpacity={0.1} />
          </linearGradient>
        </defs>
        <Line
          type="monotone"
          dataKey="revenue"
          stroke="var(--color-accent)"
          strokeWidth={3}
          fill="url(#revenueGradient)"
          dot={{ fill: 'var(--color-accent)', r: 4 }}
          activeDot={{ r: 6, boxShadow: 'var(--shadow-glow-accent)' }}
        />
      </LineChart>
    </ResponsiveContainer>
  </div>
</div>
```

### Form Elements

**Input Field**:
```jsx
<div className="input-group">
  <label htmlFor="api-key">API Key</label>
  <input
    type="text"
    id="api-key"
    className="input"
    placeholder="iv_xxxxxxxxxxxxxx"
  />
</div>
```

```css
.input {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-base);
  color: var(--text-primary);
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  transition: all var(--duration-fast);
}

.input:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}
```

---

## Animation & Interactions

### Page Load Animations

**Stagger In Effect**:
```jsx
import { motion } from 'framer-motion';

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
};

<motion.div
  variants={container}
  initial="hidden"
  animate="show"
  className="feature-grid"
>
  {features.map(feature => (
    <motion.div key={feature.id} variants={item}>
      <FeatureCard {...feature} />
    </motion.div>
  ))}
</motion.div>
```

### Hover Interactions

**Magnetic Button**:
```jsx
const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

const handleMouseMove = (e) => {
  const rect = e.currentTarget.getBoundingClientRect();
  const x = e.clientX - rect.left - rect.width / 2;
  const y = e.clientY - rect.top - rect.height / 2;
  setMousePosition({ x: x * 0.3, y: y * 0.3 });
};

const handleMouseLeave = () => {
  setMousePosition({ x: 0, y: 0 });
};

<motion.button
  onMouseMove={handleMouseMove}
  onMouseLeave={handleMouseLeave}
  animate={{ x: mousePosition.x, y: mousePosition.y }}
  transition={{ type: 'spring', stiffness: 150, damping: 15 }}
  className="btn-primary"
>
  Get Started
</motion.button>
```

### Particle Effects

**Background Particles**:
```jsx
import Particles from 'react-tsparticles';

<Particles
  options={{
    particles: {
      number: { value: 80 },
      color: { value: '#FF6B35' },
      opacity: {
        value: 0.3,
        animation: { enable: true, speed: 1 }
      },
      size: {
        value: 3,
        random: true
      },
      links: {
        enable: true,
        distance: 150,
        color: '#FF6B35',
        opacity: 0.2,
        width: 1
      },
      move: {
        enable: true,
        speed: 1,
        direction: 'none',
        random: true,
        out_mode: 'bounce'
      }
    }
  }}
/>
```

### Scroll Animations

**Parallax Sections**:
```jsx
import { useScroll, useTransform, motion } from 'framer-motion';

const { scrollYProgress } = useScroll();
const y = useTransform(scrollYProgress, [0, 1], ['0%', '50%']);
const opacity = useTransform(scrollYProgress, [0, 0.5, 1], [1, 0.5, 0]);

<motion.div
  style={{ y, opacity }}
  className="hero-background"
>
  <ParticleField />
</motion.div>
```

### Loading States

**Skeleton Loader**:
```jsx
<div className="skeleton-card">
  <div className="skeleton skeleton-title"></div>
  <div className="skeleton skeleton-text"></div>
  <div className="skeleton skeleton-text"></div>
  <div className="skeleton skeleton-button"></div>
</div>
```

```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--glass-bg) 0%,
    rgba(255,255,255,0.1) 50%,
    var(--glass-bg) 100%
  );
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s ease-in-out infinite;
  border-radius: var(--radius-md);
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton-title {
  height: 24px;
  width: 60%;
  margin-bottom: var(--space-3);
}

.skeleton-text {
  height: 16px;
  width: 100%;
  margin-bottom: var(--space-2);
}
```

---

## Performance & SEO

### Performance Budget

**Target Metrics**:
- **FCP** (First Contentful Paint): < 1.5s
- **LCP** (Largest Contentful Paint): < 2.5s
- **TBT** (Total Blocking Time): < 300ms
- **CLS** (Cumulative Layout Shift): < 0.1
- **Lighthouse Score**: > 95

**Optimization Strategies**:

1. **Code Splitting**:
```jsx
// Route-based splitting
const Dashboard = lazy(() => import('./Dashboard'));
const Marketplace = lazy(() => import('./Marketplace'));

<Suspense fallback={<Loading />}>
  <Routes>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/marketplace" element={<Marketplace />} />
  </Routes>
</Suspense>
```

2. **Image Optimization**:
```jsx
import Image from 'next/image';

<Image
  src="/hero-background.jpg"
  alt="Platform visualization"
  width={1920}
  height={1080}
  priority
  placeholder="blur"
  quality={85}
/>
```

3. **Font Loading**:
```jsx
// next.config.js
module.exports = {
  optimizeFonts: true,
  // Preload critical fonts
  experimental: {
    fontLoaders: [
      { loader: '@next/font/google', options: { subsets: ['latin'] } }
    ]
  }
};
```

4. **Bundle Size**:
- Target: < 200KB initial JS bundle
- Use tree-shaking
- Lazy load non-critical libraries
- Analyze with `webpack-bundle-analyzer`

### SEO Implementation

**Meta Tags** (Every Page):
```jsx
import Head from 'next/head';

<Head>
  <title>Industriverse - Deploy Anywhere. Scale Everywhere.</title>
  <meta
    name="description"
    content="White-label platform for embedding Ambient Intelligence. AI Shield, I³ intelligence layer, and Deploy Anywhere Capsules for any infrastructure."
  />

  {/* Open Graph */}
  <meta property="og:type" content="website" />
  <meta property="og:title" content="Industriverse Platform" />
  <meta property="og:description" content="..." />
  <meta property="og:image" content="https://industriverse.ai/og-image.jpg" />

  {/* Twitter */}
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Industriverse Platform" />
  <meta name="twitter:description" content="..." />
  <meta name="twitter:image" content="https://industriverse.ai/twitter-image.jpg" />

  {/* Structured Data */}
  <script type="application/ld+json">
    {JSON.stringify({
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      "name": "Industriverse",
      "description": "...",
      "offers": {
        "@type": "AggregateOffer",
        "lowPrice": "5000",
        "highPrice": "500000",
        "priceCurrency": "USD"
      }
    })}
  </script>
</Head>
```

**Sitemap Generation**:
```jsx
// pages/sitemap.xml.js
export async function getServerSideProps({ res }) {
  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <url>
        <loc>https://industriverse.ai</loc>
        <priority>1.0</priority>
      </url>
      <url>
        <loc>https://industriverse.ai/platform</loc>
        <priority>0.8</priority>
      </url>
      <!-- ... more URLs ... -->
    </urlset>`;

  res.setHeader('Content-Type', 'text/xml');
  res.write(sitemap);
  res.end();

  return { props: {} };
}
```

---

## Responsive Design

### Breakpoints

```css
:root {
  --breakpoint-sm: 640px;   /* Mobile landscape */
  --breakpoint-md: 768px;   /* Tablet */
  --breakpoint-lg: 1024px;  /* Laptop */
  --breakpoint-xl: 1280px;  /* Desktop */
  --breakpoint-2xl: 1536px; /* Large desktop */
}
```

### Mobile-First Approach

**Example - Hero Section**:
```css
/* Mobile (default) */
.hero {
  padding: var(--space-8) var(--space-4);
  text-align: center;
}

.hero-title {
  font-size: var(--text-3xl);
  line-height: 1.2;
}

.hero-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* Tablet */
@media (min-width: 768px) {
  .hero {
    padding: var(--space-12) var(--space-8);
  }

  .hero-title {
    font-size: var(--text-5xl);
  }

  .hero-grid {
    flex-direction: row;
    gap: var(--space-6);
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .hero {
    padding: var(--space-20) var(--space-12);
  }

  .hero-title {
    font-size: var(--text-6xl);
  }
}
```

### Touch Targets

```css
/* Minimum 44x44px touch targets for mobile */
.btn, .link, .interactive-element {
  min-height: 44px;
  min-width: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
```

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Set up Next.js monorepo with Turborepo
- [ ] Implement design system (tokens, components)
- [ ] Build core layout components (Nav, Footer, Container)
- [ ] Set up Tailwind + custom theme
- [ ] Create component library in Storybook

### Phase 2: Marketing Site (Weeks 3-4)
- [ ] Homepage with animated hero
- [ ] Platform overview page
- [ ] Pricing tier comparison
- [ ] Partner testimonials
- [ ] Documentation hub

### Phase 3: Partner Portal (Weeks 5-6)
- [ ] Authentication flow
- [ ] Dashboard with real-time metrics
- [ ] DAC configuration UI
- [ ] Theme customizer
- [ ] Billing & analytics pages

### Phase 4: Widget Showcase (Week 7)
- [ ] Widget preview gallery
- [ ] Live demo environment
- [ ] Embed code generator
- [ ] Interactive configuration

### Phase 5: Marketplace (Week 8) - Tier 3
- [ ] Insight listing page
- [ ] Search & filters
- [ ] Detail views
- [ ] Transaction flow
- [ ] Portfolio management

### Phase 6: Shadow Twin 3D (Weeks 9-10)
- [ ] Three.js scene setup
- [ ] Force-directed graph algorithm
- [ ] Node/edge rendering with effects
- [ ] Camera controls
- [ ] Info panels & interactions

### Phase 7: Polish & Launch (Weeks 11-12)
- [ ] Performance optimization
- [ ] Accessibility audit
- [ ] Cross-browser testing
- [ ] SEO implementation
- [ ] Analytics integration
- [ ] Launch!

---

## Success Metrics

### User Engagement
- **Time on Site**: > 3 minutes average
- **Bounce Rate**: < 40%
- **Widget Preview Rate**: > 60% of visitors
- **Partner Sign-up Conversion**: > 5%

### Performance
- **Lighthouse Score**: > 95
- **FCP**: < 1.5s
- **LCP**: < 2.5s
- **Page Load Time**: < 2s (3G)

### Business
- **Partner Onboarding Time**: < 30 minutes (from sign-up to first DAC)
- **Widget Integration Time**: < 15 minutes (React)
- **Theme Customization Time**: < 5 minutes
- **Partner Satisfaction**: > 4.5/5 NPS

---

## Conclusion

This frontend vision creates a **premium, high-performance platform** that:

✅ **WOWs** users with stunning thermodynamic aesthetics
✅ **Communicates value** clearly through intuitive UX
✅ **Scales** across all tiers with consistent quality
✅ **Performs** exceptionally on all devices
✅ **Converts** visitors to partners through compelling design

The combination of cutting-edge technology, thoughtful UX, and breathtaking visuals will make Industriverse the **premier white-label platform for Ambient Intelligence**.

---

**Next Steps**:
1. Review this vision with stakeholders
2. Create high-fidelity mockups in Figma
3. Build component library in Storybook
4. Implement Phase 1 (Foundation)
5. Iterate based on partner feedback

**Questions? Contact**: frontend@industriverse.ai
