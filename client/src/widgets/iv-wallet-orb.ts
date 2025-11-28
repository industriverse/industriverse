/**
 * <iv-wallet-orb> Widget
 * Week 8: White-Label Platform
 * 
 * Visual representation of wallet balance with AmI glow effects
 * 
 * Usage:
 * <iv-wallet-orb
 *   balance="1250.50"
 *   currency="USD"
 *   ws-url="wss://api.industriverse.io/ws"
 *   user-id="user123"
 * ></iv-wallet-orb>
 */

import { IVWidget } from './base/IVWidget';

export class IVWalletOrb extends IVWidget {
  private balance: number = 0;
  private currency: string = 'USD';
  private isAnimating: boolean = false;

  static get observedAttributes() {
    return ['balance', 'currency'];
  }

  protected handleAttributeChange(name: string, oldValue: string, newValue: string): void {
    if (name === 'balance') {
      const newBalance = parseFloat(newValue) || 0;
      if (newBalance !== this.balance) {
        this.animateBalanceChange(this.balance, newBalance);
        this.balance = newBalance;
      }
    } else if (name === 'currency') {
      this.currency = newValue || 'USD';
    }
  }

  protected shouldRerender(attributeName: string): boolean {
    return attributeName === 'currency';
  }

  protected render(): void {
    // Clear shadow DOM
    this.shadow.innerHTML = '';

    // Apply styles
    this.applyStyles(this.getStyles());

    // Create structure
    const container = document.createElement('div');
    container.className = 'wallet-orb-container';

    const orb = document.createElement('div');
    orb.className = 'orb';
    orb.id = 'orb';

    const balanceEl = document.createElement('div');
    balanceEl.className = 'balance';
    balanceEl.id = 'balance';
    balanceEl.textContent = this.formatBalance(this.balance);

    const currencyEl = document.createElement('div');
    currencyEl.className = 'currency';
    currencyEl.textContent = this.currency;

    orb.appendChild(balanceEl);
    orb.appendChild(currencyEl);
    container.appendChild(orb);

    this.shadow.appendChild(container);
  }

  protected attachEventListeners(): void {
    // Click to pulse animation
    const orb = this.shadow.getElementById('orb');
    if (orb) {
      orb.addEventListener('click', () => {
        this.pulseAnimation();
      });
    }
  }

  protected onWebSocketMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data);
      
      if (data.type === 'balance_update' && data.userId === this.config.userId) {
        this.updateBalance(data.balance);
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }

  private updateBalance(newBalance: number): void {
    this.setAttribute('balance', newBalance.toString());
  }

  private formatBalance(balance: number): string {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(balance);
  }

  private animateBalanceChange(oldBalance: number, newBalance: number): void {
    if (this.isAnimating) return;
    
    this.isAnimating = true;
    const balanceEl = this.shadow.getElementById('balance');
    const orb = this.shadow.getElementById('orb');
    
    if (!balanceEl || !orb) return;

    const duration = 1000; // 1 second
    const startTime = Date.now();
    const diff = newBalance - oldBalance;

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const currentBalance = oldBalance + (diff * eased);
      
      balanceEl.textContent = this.formatBalance(currentBalance);

      // Add glow effect based on change direction
      if (diff > 0) {
        orb.style.boxShadow = `0 0 ${20 + (progress * 30)}px ${this.theme.statusSuccess}`;
      } else if (diff < 0) {
        orb.style.boxShadow = `0 0 ${20 + (progress * 30)}px ${this.theme.statusError}`;
      }

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        this.isAnimating = false;
        // Reset to default glow
        setTimeout(() => {
          orb.style.boxShadow = `0 0 30px ${this.theme.amiContextGlow}`;
        }, 500);
      }
    };

    requestAnimationFrame(animate);
  }

  private pulseAnimation(): void {
    const orb = this.shadow.getElementById('orb');
    if (!orb) return;

    orb.style.animation = 'none';
    setTimeout(() => {
      orb.style.animation = 'pulse 0.5s ease-out';
    }, 10);
  }

  private getStyles(): string {
    return `
      :host {
        display: inline-block;
        --orb-size: 120px;
      }

      .wallet-orb-container {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
      }

      .orb {
        width: var(--orb-size);
        height: var(--orb-size);
        border-radius: 50%;
        background: linear-gradient(135deg, ${this.theme.brandPrimary}, ${this.theme.brandSecondary});
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: transform ${this.theme.durationNormal} ${this.theme.easingDefault};
        box-shadow: 0 0 30px ${this.theme.amiContextGlow};
        position: relative;
        overflow: hidden;
      }

      .orb::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, ${this.theme.amiPredictionPulse} 0%, transparent 70%);
        animation: rotate 10s linear infinite;
      }

      .orb:hover {
        transform: scale(1.05);
      }

      .orb:active {
        transform: scale(0.95);
      }

      .balance {
        font-family: ${this.theme.fontMono};
        font-size: 1.25rem;
        font-weight: 700;
        color: ${this.theme.fgPrimary};
        z-index: 1;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
      }

      .currency {
        font-family: ${this.theme.fontBody};
        font-size: 0.75rem;
        font-weight: 500;
        color: ${this.theme.fgSecondary};
        z-index: 1;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.25rem;
      }

      @keyframes rotate {
        from {
          transform: rotate(0deg);
        }
        to {
          transform: rotate(360deg);
        }
      }

      @keyframes pulse {
        0%, 100% {
          transform: scale(1);
        }
        50% {
          transform: scale(1.1);
        }
      }
    `;
  }
}

// Register custom element
if (!customElements.get('iv-wallet-orb')) {
  customElements.define('iv-wallet-orb', IVWalletOrb);
}
