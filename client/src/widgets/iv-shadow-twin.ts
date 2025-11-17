import { IVWidget } from './base/IVWidget';

interface ShadowTwinData {
  twinId: string;
  syncStatus: 'synced' | 'syncing' | 'drift' | 'offline';
  lastSync: number;
  driftPercentage: number;
  energyConsumption: number;
  calibrationNeeded: boolean;
}

export class IVShadowTwin extends IVWidget {
  protected attachEventListeners(): void {
    const syncBtn = this.shadowRoot?.querySelector('.sync-btn');
    syncBtn?.addEventListener('click', () => this.forceSync());
  }

  protected twinData: ShadowTwinData = {
    twinId: '',
    syncStatus: 'offline',
    lastSync: 0,
    driftPercentage: 0,
    energyConsumption: 0,
    calibrationNeeded: false,
  };

  constructor() {
    super();
  }

  protected getDefaultStyles(): string {
    return ':host { display: block; font-family: system-ui, sans-serif; }';
  }

  protected render(): void {
    if (!this.shadowRoot) return;
    const styles = this.getDefaultStyles();
    const twinId = this.twinData.twinId || 'Unknown';
    this.shadowRoot.innerHTML = '<style>' + styles + '</style><div>Shadow Twin: ' + twinId + '</div><button class="sync-btn">Sync</button>';
    this.attachEventListeners();
  }

  protected forceSync(): void {
    this.emitEvent('sync-requested', { twinId: this.twinData.twinId });
  }

  protected handleWebSocketMessage(data: any): void {
    if (data.type === 'twin_update') {
      this.twinData = { ...this.twinData, ...data.data };
      this.render();
    }
  }

  protected onConnect(): void {
    this.render();
  }

  protected onDisconnect(): void {}

  static get observedAttributes() {
    return ['twin-id', 'sync-status', 'ws-url'];
  }

  attributeChangedCallback(name: string, oldValue: string, newValue: string) {
    if (oldValue === newValue) return;
    if (name === 'twin-id') {
      this.twinData.twinId = newValue;
      this.render();
    }
  }
}

if (!customElements.get('iv-shadow-twin')) {
  customElements.define('iv-shadow-twin', IVShadowTwin);
}
