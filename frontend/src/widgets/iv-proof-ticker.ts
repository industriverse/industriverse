/**
 * <iv-proof-ticker> Widget
 * Week 8: White-Label Platform
 * 
 * Real-time proof generation feed with scrolling ticker
 * 
 * Usage:
 * <iv-proof-ticker
 *   ws-url="wss://api.industriverse.io/ws"
 *   max-items="10"
 *   scroll-speed="slow"
 * ></iv-proof-ticker>
 */

import { IVWidget } from './base/IVWidget';

interface Proof {
  id: string;
  type: 'execution' | 'energy' | 'optimization' | 'calibration' | 'thermodynamic';
  value: number;
  timestamp: number;
  source: string;
}

export class IVProofTicker extends IVWidget {
  private proofs: Proof[] = [];
  private maxItems: number = 10;
  private scrollSpeed: 'slow' | 'normal' | 'fast' = 'normal';

  static get observedAttributes() {
    return ['max-items', 'scroll-speed'];
  }

  protected handleAttributeChange(name: string, oldValue: string, newValue: string): void {
    if (name === 'max-items') {
      this.maxItems = parseInt(newValue) || 10;
      this.trimProofs();
    } else if (name === 'scroll-speed') {
      this.scrollSpeed = (newValue as any) || 'normal';
    }
  }

  protected shouldRerender(attributeName: string): boolean {
    return attributeName === 'scroll-speed';
  }

  protected render(): void {
    this.shadow.innerHTML = '';
    this.applyStyles(this.getStyles());

    const container = document.createElement('div');
    container.className = 'proof-ticker-container';

    const header = document.createElement('div');
    header.className = 'ticker-header';
    header.innerHTML = `
      <span class="ticker-title">Live Proofs</span>
      <span class="ticker-count" id="proof-count">${this.proofs.length}</span>
    `;

    const tickerTrack = document.createElement('div');
    tickerTrack.className = 'ticker-track';
    tickerTrack.id = 'ticker-track';

    this.renderProofs(tickerTrack);

    container.appendChild(header);
    container.appendChild(tickerTrack);
    this.shadow.appendChild(container);
  }

  protected attachEventListeners(): void {
    // Pause on hover
    const track = this.shadow.getElementById('ticker-track');
    if (track) {
      track.addEventListener('mouseenter', () => {
        track.style.animationPlayState = 'paused';
      });
      track.addEventListener('mouseleave', () => {
        track.style.animationPlayState = 'running';
      });
    }
  }

  protected onWebSocketMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data);
      
      if (data.type === 'proof_generated') {
        this.addProof({
          id: data.id,
          type: data.proofType,
          value: data.value,
          timestamp: Date.now(),
          source: data.source || 'Unknown',
        });
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }

  private addProof(proof: Proof): void {
    this.proofs.unshift(proof);
    this.trimProofs();
    this.updateDisplay();
    this.emitEvent('proof-added', proof);
  }

  private trimProofs(): void {
    if (this.proofs.length > this.maxItems) {
      this.proofs = this.proofs.slice(0, this.maxItems);
    }
  }

  private updateDisplay(): void {
    const track = this.shadow.getElementById('ticker-track');
    const count = this.shadow.getElementById('proof-count');
    
    if (track) {
      this.renderProofs(track);
    }
    
    if (count) {
      count.textContent = this.proofs.length.toString();
    }
  }

  private renderProofs(container: HTMLElement): void {
    container.innerHTML = '';
    
    if (this.proofs.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'empty-state';
      empty.textContent = 'Waiting for proofs...';
      container.appendChild(empty);
      return;
    }

    this.proofs.forEach(proof => {
      const item = document.createElement('div');
      item.className = `proof-item proof-type-${proof.type}`;
      item.innerHTML = `
        <span class="proof-icon">${this.getProofIcon(proof.type)}</span>
        <span class="proof-type">${this.formatProofType(proof.type)}</span>
        <span class="proof-value">$${proof.value.toFixed(2)}</span>
        <span class="proof-source">${proof.source}</span>
        <span class="proof-time">${this.formatTime(proof.timestamp)}</span>
      `;
      container.appendChild(item);
    });
  }

  private getProofIcon(type: string): string {
    const icons = {
      execution: '⚡',
      energy: '🔋',
      optimization: '🎯',
      calibration: '🔧',
      thermodynamic: '🌡️',
    };
    return icons[type as keyof typeof icons] || '📋';
  }

  private formatProofType(type: string): string {
    return type.charAt(0).toUpperCase() + type.slice(1);
  }

  private formatTime(timestamp: number): string {
    const seconds = Math.floor((Date.now() - timestamp) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ago`;
  }

  private getStyles(): string {
    const speedMap = {
      slow: '60s',
      normal: '30s',
      fast: '15s',
    };
    const duration = speedMap[this.scrollSpeed];

    return `
      :host {
        display: block;
        width: 100%;
      }

      .proof-ticker-container {
        background: ${this.theme.bgSecondary};
        border: 1px solid ${this.theme.borderDefault};
        border-radius: ${this.theme.radiusMd};
        overflow: hidden;
        box-shadow: ${this.theme.shadowMd};
      }

      .ticker-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 1rem;
        background: ${this.theme.bgPrimary};
        border-bottom: 1px solid ${this.theme.borderDefault};
      }

      .ticker-title {
        font-family: ${this.theme.fontHeading};
        font-size: 0.875rem;
        font-weight: 600;
        color: ${this.theme.fgPrimary};
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }

      .ticker-count {
        font-family: ${this.theme.fontMono};
        font-size: 0.875rem;
        font-weight: 600;
        color: ${this.theme.brandPrimary};
        background: ${this.theme.amiContextGlow};
        padding: 0.25rem 0.5rem;
        border-radius: 9999px;
      }

      .ticker-track {
        padding: 0.5rem 0;
        max-height: 300px;
        overflow-y: auto;
      }

      .ticker-track::-webkit-scrollbar {
        width: 6px;
      }

      .ticker-track::-webkit-scrollbar-track {
        background: ${this.theme.bgPrimary};
      }

      .ticker-track::-webkit-scrollbar-thumb {
        background: ${this.theme.borderDefault};
        border-radius: 3px;
      }

      .proof-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 1rem;
        border-left: 3px solid transparent;
        transition: all ${this.theme.durationNormal} ${this.theme.easingDefault};
        animation: slideIn ${this.theme.durationNormal} ${this.theme.easingDefault};
      }

      .proof-item:hover {
        background: ${this.theme.bgPrimary};
      }

      .proof-item.proof-type-execution {
        border-left-color: ${this.theme.statusInfo};
      }

      .proof-item.proof-type-energy {
        border-left-color: ${this.theme.statusSuccess};
      }

      .proof-item.proof-type-optimization {
        border-left-color: ${this.theme.brandPrimary};
      }

      .proof-item.proof-type-calibration {
        border-left-color: ${this.theme.statusWarning};
      }

      .proof-item.proof-type-thermodynamic {
        border-left-color: ${this.theme.brandSecondary};
      }

      .proof-icon {
        font-size: 1.25rem;
      }

      .proof-type {
        font-family: ${this.theme.fontBody};
        font-size: 0.875rem;
        font-weight: 500;
        color: ${this.theme.fgPrimary};
        min-width: 100px;
      }

      .proof-value {
        font-family: ${this.theme.fontMono};
        font-size: 0.875rem;
        font-weight: 600;
        color: ${this.theme.statusSuccess};
        min-width: 60px;
        text-align: right;
      }

      .proof-source {
        font-family: ${this.theme.fontMono};
        font-size: 0.75rem;
        color: ${this.theme.fgSecondary};
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .proof-time {
        font-family: ${this.theme.fontBody};
        font-size: 0.75rem;
        color: ${this.theme.fgSecondary};
        min-width: 60px;
        text-align: right;
      }

      .empty-state {
        padding: 2rem;
        text-align: center;
        color: ${this.theme.fgSecondary};
        font-family: ${this.theme.fontBody};
        font-size: 0.875rem;
      }

      @keyframes slideIn {
        from {
          opacity: 0;
          transform: translateX(-20px);
        }
        to {
          opacity: 1;
          transform: translateX(0);
        }
      }
    `;
  }
}

// Register custom element
if (!customElements.get('iv-proof-ticker')) {
  customElements.define('iv-proof-ticker', IVProofTicker);
}
