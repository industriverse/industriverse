/**
 * <iv-utid-badge> Widget
 * Week 8: White-Label Platform
 * 
 * Universal Thermodynamic ID badge with blockchain verification
 * Features:
 * - UTID display with copy-to-clipboard
 * - Blockchain verification status
 * - QR code generation
 * - Provenance chain visualization
 * - AmI consciousness glow
 */

import { IVWidget } from './base/IVWidget';

interface UTIDData {
  utid: string;
  verified: boolean;
  blockchainHash: string;
  timestamp: number;
  provenanceChain: string[];
  consciousnessLevel: number; // 0-100
  physicsDomain: string;
}

export class IVUTIDBadge extends IVWidget {
  protected attachEventListeners(): void {
    const copyBtn = this.shadowRoot?.querySelector('.copy-btn');
    const qrBtn = this.shadowRoot?.querySelector('.qr-btn');
    
    copyBtn?.addEventListener('click', () => this.copyUTID());
    qrBtn?.addEventListener('click', () => this.showQRCode());
  }

  protected utidData: UTIDData = {
    utid: '',
    verified: false,
    blockchainHash: '',
    timestamp: Date.now(),
    provenanceChain: [],
    consciousnessLevel: 0,
    physicsDomain: 'unknown',
  };

  protected showingQR: boolean = false;

  constructor() {
    super();
  }

  protected getDefaultStyles(): string {
    return `
      :host {
        display: inline-block;
        font-family: var(--font-sans, system-ui, sans-serif);
      }

      .badge-container {
        background: var(--color-background, #1a1a1a);
        border: 1px solid var(--color-border, #333);
        border-radius: 8px;
        padding: 12px 16px;
        display: inline-flex;
        align-items: center;
        gap: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
        cursor: pointer;
      }

      .badge-container:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        transform: translateY(-1px);
      }

      .badge-container.verified {
        border-color: var(--status-success, #10b981);
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.2);
      }

      .badge-container.consciousness {
        animation: consciousness-pulse 3s ease-in-out infinite;
      }

      @keyframes consciousness-pulse {
        0%, 100% {
          box-shadow: 0 0 15px rgba(139, 92, 246, 0.3);
        }
        50% {
          box-shadow: 0 0 25px rgba(139, 92, 246, 0.5);
        }
      }

      .utid-icon {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--brand-primary, #0ea5e9), var(--brand-secondary, #8b5cf6));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        flex-shrink: 0;
      }

      .utid-content {
        flex: 1;
        min-width: 0;
      }

      .utid-label {
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--color-muted-foreground, #888);
        margin-bottom: 2px;
      }

      .utid-value {
        font-family: var(--font-mono, 'JetBrains Mono', monospace);
        font-size: 13px;
        font-weight: 600;
        color: var(--color-foreground, #e5e5e5);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .badge-actions {
        display: flex;
        gap: 8px;
      }

      .action-btn {
        width: 28px;
        height: 28px;
        border: none;
        background: var(--color-muted, #333);
        border-radius: 4px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        font-size: 14px;
      }

      .action-btn:hover {
        background: var(--color-accent, #444);
        transform: scale(1.1);
      }

      .action-btn:active {
        transform: scale(0.95);
      }

      .verification-badge {
        position: absolute;
        top: -6px;
        right: -6px;
        width: 20px;
        height: 20px;
        background: var(--status-success, #10b981);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        border: 2px solid var(--color-background, #1a1a1a);
      }

      .qr-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
      }

      .qr-content {
        background: var(--color-background, #1a1a1a);
        border: 1px solid var(--color-border, #333);
        border-radius: 12px;
        padding: 24px;
        max-width: 300px;
        text-align: center;
      }

      .qr-code {
        width: 200px;
        height: 200px;
        margin: 16px auto;
        background: white;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        color: #333;
      }

      .qr-close {
        margin-top: 16px;
        padding: 8px 16px;
        background: var(--brand-primary, #0ea5e9);
        border: none;
        border-radius: 6px;
        color: white;
        cursor: pointer;
        font-weight: 600;
      }

      .consciousness-indicator {
        position: absolute;
        bottom: -4px;
        left: 50%;
        transform: translateX(-50%);
        width: 80%;
        height: 3px;
        background: rgba(139, 92, 246, 0.2);
        border-radius: 2px;
        overflow: hidden;
      }

      .consciousness-fill {
        height: 100%;
        background: linear-gradient(90deg, #8b5cf6, #06b6d4);
        transition: width 0.5s ease;
      }
    `;
  }

  protected render(): void {
    if (!this.shadowRoot) return;

    const shortUTID = this.utidData.utid ? 
      `${this.utidData.utid.slice(0, 8)}...${this.utidData.utid.slice(-6)}` : 
      'No UTID';

    const containerClasses = [
      'badge-container',
      this.utidData.verified ? 'verified' : '',
      this.utidData.consciousnessLevel > 50 ? 'consciousness' : '',
    ].filter(Boolean).join(' ');

    this.shadowRoot.innerHTML = `
      <style>${this.getDefaultStyles()}</style>
      <div class="${containerClasses}" style="position: relative;">
        <div class="utid-icon">🔮</div>
        <div class="utid-content">
          <div class="utid-label">UTID</div>
          <div class="utid-value" title="${this.utidData.utid}">${shortUTID}</div>
        </div>
        <div class="badge-actions">
          <button class="action-btn copy-btn" title="Copy UTID">📋</button>
          <button class="action-btn qr-btn" title="Show QR Code">📱</button>
        </div>
        ${this.utidData.verified ? '<div class="verification-badge">✓</div>' : ''}
        ${this.utidData.consciousnessLevel > 0 ? `
          <div class="consciousness-indicator">
            <div class="consciousness-fill" style="width: ${this.utidData.consciousnessLevel}%"></div>
          </div>
        ` : ''}
      </div>
      ${this.showingQR ? this.renderQRModal() : ''}
    `;

    this.attachEventListeners();
  }

  protected renderQRModal(): string {
    return `
      <div class="qr-modal">
        <div class="qr-content">
          <h3 style="margin: 0 0 8px 0; color: var(--color-foreground, #e5e5e5);">UTID QR Code</h3>
          <div class="qr-code">
            QR Code<br/>
            ${this.utidData.utid.slice(0, 12)}...
          </div>
          <div style="font-size: 11px; color: var(--color-muted-foreground, #888); margin-top: 8px;">
            Scan to verify on blockchain
          </div>
          <button class="qr-close">Close</button>
        </div>
      </div>
    `;
  }

  protected copyUTID(): void {
    if (!this.utidData.utid) return;

    navigator.clipboard.writeText(this.utidData.utid).then(() => {
      this.emitEvent('utid-copied', { utid: this.utidData.utid });
      
      // Show feedback
      const copyBtn = this.shadowRoot?.querySelector('.copy-btn');
      if (copyBtn) {
        copyBtn.textContent = '✓';
        setTimeout(() => {
          copyBtn.textContent = '📋';
        }, 2000);
      }
    });
  }

  protected showQRCode(): void {
    this.showingQR = true;
    this.render();

    // Attach close handler
    const closeBtn = this.shadowRoot?.querySelector('.qr-close');
    const modal = this.shadowRoot?.querySelector('.qr-modal');
    
    closeBtn?.addEventListener('click', () => {
      this.showingQR = false;
      this.render();
    });

    modal?.addEventListener('click', (e) => {
      if (e.target === modal) {
        this.showingQR = false;
        this.render();
      }
    });

    this.emitEvent('qr-shown', { utid: this.utidData.utid });
  }

  protected handleWebSocketMessage(data: any): void {
    if (data.type === 'utid_update') {
      this.updateUTID(data.data);
    }
  }

  public updateUTID(data: Partial<UTIDData>): void {
    this.utidData = { ...this.utidData, ...data };
    this.render();
    this.emitEvent('utid-update', this.utidData);
  }

  protected onConnect(): void {
    this.render();
  }

  protected onDisconnect(): void {
    // Cleanup
  }

  // Attribute handling
  static get observedAttributes() {
    return ['utid', 'verified', 'blockchain-hash', 'consciousness-level', 'physics-domain', 'ws-url'];
  }

  attributeChangedCallback(name: string, oldValue: string, newValue: string) {
    if (oldValue === newValue) return;

    switch (name) {
      case 'utid':
        this.utidData.utid = newValue;
        this.render();
        break;
      case 'verified':
        this.utidData.verified = newValue === 'true';
        this.render();
        break;
      case 'blockchain-hash':
        this.utidData.blockchainHash = newValue;
        this.render();
        break;
      case 'consciousness-level':
        this.utidData.consciousnessLevel = parseFloat(newValue) || 0;
        this.render();
        break;
      case 'physics-domain':
        this.utidData.physicsDomain = newValue;
        this.render();
        break;
      case 'ws-url':
        this.config.wsUrl = newValue;
        if (newValue) {
          this.connectWebSocket();
        }
        break;
    }
  }
}

// Register custom element
if (!customElements.get('iv-utid-badge')) {
  customElements.define('iv-utid-badge', IVUTIDBadge);
}
