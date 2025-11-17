/**
 * Widget Loader
 * Week 8: White-Label Platform - Widget Build System
 * 
 * Main entry point for CDN distribution
 * Loads and registers all Industriverse widgets as custom elements
 * 
 * Usage:
 * <script src="https://cdn.industriverse.io/widgets/latest/iv-widgets.js"></script>
 * <iv-wallet-orb balance="1000" theme="cosmic"></iv-wallet-orb>
 */

// Widget registration system
class WidgetRegistry {
  private widgets: Map<string, CustomElementConstructor> = new Map();
  private loaded: Set<string> = new Set();

  register(name: string, constructor: CustomElementConstructor) {
    this.widgets.set(name, constructor);
    if (!customElements.get(name)) {
      customElements.define(name, constructor);
      this.loaded.add(name);
    }
  }

  get(name: string): CustomElementConstructor | undefined {
    return this.widgets.get(name);
  }

  isLoaded(name: string): boolean {
    return this.loaded.has(name);
  }

  getAll(): string[] {
    return Array.from(this.widgets.keys());
  }
}

// Base widget class
class IndustriverseWidget extends HTMLElement {
  protected shadow: ShadowRoot;
  protected config: Record<string, any> = {};

  constructor() {
    super();
    this.shadow = this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    this.parseAttributes();
    this.render();
  }

  protected parseAttributes() {
    for (let i = 0; i < this.attributes.length; i++) {
      const attr = this.attributes[i];
      const value = attr.value;
      // Try to parse as JSON, fallback to string
      try {
        this.config[attr.name] = JSON.parse(value);
      } catch {
        this.config[attr.name] = value;
      }
    }
  }

  protected render() {
    // Override in subclasses
  }

  protected injectStyles(css: string) {
    const style = document.createElement('style');
    style.textContent = css;
    this.shadow.appendChild(style);
  }
}

// Wallet Orb Widget
class WalletOrbWidget extends IndustriverseWidget {
  protected render() {
    const balance = this.config.balance || 0;
    const theme = this.config.theme || 'cosmic';

    this.injectStyles(`
      :host {
        display: inline-block;
      }
      .wallet-orb {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 30px rgba(14, 165, 233, 0.5);
        animation: pulse 2s ease-in-out infinite;
      }
      .balance {
        color: white;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
      }
      @keyframes pulse {
        0%, 100% { box-shadow: 0 0 30px rgba(14, 165, 233, 0.5); }
        50% { box-shadow: 0 0 50px rgba(139, 92, 246, 0.8); }
      }
    `);

    const container = document.createElement('div');
    container.className = 'wallet-orb';
    container.innerHTML = `<div class="balance">${balance}</div>`;
    this.shadow.appendChild(container);
  }
}

// Proof Ticker Widget
class ProofTickerWidget extends IndustriverseWidget {
  protected render() {
    const speed = this.config.speed || 30;

    this.injectStyles(`
      :host {
        display: block;
        overflow: hidden;
      }
      .ticker {
        display: flex;
        gap: 20px;
        animation: scroll ${speed}s linear infinite;
      }
      .proof-item {
        padding: 8px 16px;
        background: rgba(14, 165, 233, 0.1);
        border: 1px solid rgba(14, 165, 233, 0.3);
        border-radius: 4px;
        white-space: nowrap;
        font-size: 14px;
      }
      @keyframes scroll {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
      }
    `);

    const container = document.createElement('div');
    container.className = 'ticker';
    container.innerHTML = `
      <div class="proof-item">Proof #1234 verified</div>
      <div class="proof-item">Proof #1235 verified</div>
      <div class="proof-item">Proof #1236 verified</div>
      <div class="proof-item">Proof #1237 verified</div>
      <div class="proof-item">Proof #1234 verified</div>
      <div class="proof-item">Proof #1235 verified</div>
      <div class="proof-item">Proof #1236 verified</div>
      <div class="proof-item">Proof #1237 verified</div>
    `;
    this.shadow.appendChild(container);
  }
}

// Capsule Card Widget
class CapsuleCardWidget extends IndustriverseWidget {
  protected render() {
    const title = this.config.title || 'Capsule';
    const status = this.config.status || 'active';

    this.injectStyles(`
      :host {
        display: inline-block;
      }
      .capsule-card {
        padding: 16px;
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(14, 165, 233, 0.3);
        border-radius: 8px;
        min-width: 200px;
      }
      .title {
        font-size: 16px;
        font-weight: bold;
        color: #0ea5e9;
        margin-bottom: 8px;
      }
      .status {
        font-size: 12px;
        color: #10b981;
      }
    `);

    const container = document.createElement('div');
    container.className = 'capsule-card';
    container.innerHTML = `
      <div class="title">${title}</div>
      <div class="status">${status}</div>
    `;
    this.shadow.appendChild(container);
  }
}

// Energy Gauge Widget
class EnergyGaugeWidget extends IndustriverseWidget {
  protected render() {
    const value = this.config.value || 75;

    this.injectStyles(`
      :host {
        display: inline-block;
      }
      .gauge {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: conic-gradient(
          #10b981 0deg ${value * 3.6}deg,
          rgba(16, 185, 129, 0.2) ${value * 3.6}deg 360deg
        );
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .gauge-inner {
        width: 70px;
        height: 70px;
        border-radius: 50%;
        background: #0f172a;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
      }
    `);

    const container = document.createElement('div');
    container.className = 'gauge';
    container.innerHTML = `<div class="gauge-inner">${value}%</div>`;
    this.shadow.appendChild(container);
  }
}

// UTID Badge Widget
class UTIDBadgeWidget extends IndustriverseWidget {
  protected render() {
    const utid = this.config.utid || 'UTID-0000';

    this.injectStyles(`
      :host {
        display: inline-block;
      }
      .badge {
        padding: 8px 16px;
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        border-radius: 20px;
        color: white;
        font-weight: bold;
        font-size: 14px;
      }
    `);

    const container = document.createElement('div');
    container.className = 'badge';
    container.textContent = utid;
    this.shadow.appendChild(container);
  }
}

// AmI Pulse Widget
class AmIPulseWidget extends IndustriverseWidget {
  protected render() {
    const active = this.config.active !== false;

    this.injectStyles(`
      :host {
        display: inline-block;
      }
      .pulse {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: ${active ? '#10b981' : '#6b7280'};
        animation: ${active ? 'pulse 1.5s ease-in-out infinite' : 'none'};
      }
      @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.1); }
      }
    `);

    const container = document.createElement('div');
    container.className = 'pulse';
    this.shadow.appendChild(container);
  }
}

// Shadow Twin Widget
class ShadowTwinWidget extends IndustriverseWidget {
  protected render() {
    const synced = this.config.synced !== false;

    this.injectStyles(`
      :host {
        display: inline-block;
      }
      .twin {
        padding: 12px 20px;
        background: rgba(139, 92, 246, 0.1);
        border: 2px solid ${synced ? '#10b981' : '#f59e0b'};
        border-radius: 8px;
        color: ${synced ? '#10b981' : '#f59e0b'};
        font-weight: bold;
      }
    `);

    const container = document.createElement('div');
    container.className = 'twin';
    container.textContent = synced ? '✓ Synced' : '⟳ Syncing...';
    this.shadow.appendChild(container);
  }
}

// Initialize registry
const registry = new WidgetRegistry();

// Register all widgets
registry.register('iv-wallet-orb', WalletOrbWidget);
registry.register('iv-proof-ticker', ProofTickerWidget);
registry.register('iv-capsule-card', CapsuleCardWidget);
registry.register('iv-energy-gauge', EnergyGaugeWidget);
registry.register('iv-utid-badge', UTIDBadgeWidget);
registry.register('iv-ami-pulse', AmIPulseWidget);
registry.register('iv-shadow-twin', ShadowTwinWidget);

// Export for module usage
export { registry, IndustriverseWidget };

// Global API
(window as any).IVWidgets = {
  registry,
  version: '1.0.0',
  widgets: registry.getAll(),
};

console.log('Industriverse Widgets loaded:', registry.getAll());
