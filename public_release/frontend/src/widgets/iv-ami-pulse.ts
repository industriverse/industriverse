/**
 * <iv-ami-pulse> Widget
 * Week 8: White-Label Platform
 * 
 * Ambient Intelligence pulse visualization
 * Features:
 * - Real-time AmI activity indicator
 * - 4 AmI principles visualization (context, proactive, seamless, adaptive)
 * - Pulsing animation based on activity level
 * - Color-coded by intelligence type
 * - Subtle, non-intrusive design
 */

import { IVWidget } from './base/IVWidget';

interface AmIPulseData {
  activityLevel: number; // 0-100
  contextAwareness: number; // 0-100
  proactivity: number; // 0-100
  seamlessness: number; // 0-100
  adaptivity: number; // 0-100
  intelligenceType: 'learning' | 'predicting' | 'adapting' | 'idle';
  lastActivity: number;
}

export class IVAMIPulse extends IVWidget {
  protected attachEventListeners(): void {
    const container = this.shadowRoot?.querySelector('.pulse-container');
    container?.addEventListener('click', () => this.toggleDetails());
  }

  protected pulseData: AmIPulseData = {
    activityLevel: 0,
    contextAwareness: 0,
    proactivity: 0,
    seamlessness: 0,
    adaptivity: 0,
    intelligenceType: 'idle',
    lastActivity: Date.now(),
  };

  protected showingDetails: boolean = false;

  constructor() {
    super();
  }

  protected getDefaultStyles(): string {
    return `
      :host {
        display: inline-block;
        font-family: var(--font-sans, system-ui, sans-serif);
      }

      .pulse-container {
        position: relative;
        width: 60px;
        height: 60px;
        cursor: pointer;
        transition: transform 0.2s ease;
      }

      .pulse-container:hover {
        transform: scale(1.1);
      }

      .pulse-core {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: var(--ami-context-glow, rgba(14, 165, 233, 0.8));
        box-shadow: 0 0 10px var(--ami-context-glow, rgba(14, 165, 233, 0.5));
        transition: all 0.3s ease;
      }

      .pulse-core.learning {
        background: var(--brand-primary, #0ea5e9);
        box-shadow: 0 0 15px var(--brand-primary, #0ea5e9);
      }

      .pulse-core.predicting {
        background: var(--brand-secondary, #8b5cf6);
        box-shadow: 0 0 15px var(--brand-secondary, #8b5cf6);
      }

      .pulse-core.adapting {
        background: var(--brand-accent, #f59e0b);
        box-shadow: 0 0 15px var(--brand-accent, #f59e0b);
      }

      .pulse-core.idle {
        background: var(--color-muted, #64748b);
        box-shadow: 0 0 5px var(--color-muted, #64748b);
      }

      .pulse-ring {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        border-radius: 50%;
        border: 2px solid var(--ami-context-glow, rgba(14, 165, 233, 0.5));
        animation: pulse-expand 2s ease-out infinite;
      }

      .pulse-ring:nth-child(2) {
        animation-delay: 0.5s;
      }

      .pulse-ring:nth-child(3) {
        animation-delay: 1s;
      }

      @keyframes pulse-expand {
        0% {
          width: 20px;
          height: 20px;
          opacity: 1;
        }
        100% {
          width: 60px;
          height: 60px;
          opacity: 0;
        }
      }

      .pulse-details {
        position: absolute;
        top: 70px;
        left: 50%;
        transform: translateX(-50%);
        background: var(--color-background, #1a1a1a);
        border: 1px solid var(--color-border, #333);
        border-radius: 8px;
        padding: 12px;
        min-width: 200px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        z-index: 100;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.2s ease;
      }

      .pulse-details.visible {
        opacity: 1;
        pointer-events: auto;
      }

      .details-title {
        font-size: 12px;
        font-weight: 600;
        color: var(--color-foreground, #e5e5e5);
        margin-bottom: 8px;
        text-align: center;
      }

      .ami-metric {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
        font-size: 11px;
      }

      .metric-label {
        color: var(--color-muted-foreground, #888);
      }

      .metric-value {
        color: var(--color-foreground, #e5e5e5);
        font-weight: 600;
      }

      .metric-bar {
        width: 100%;
        height: 3px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 2px;
        overflow: hidden;
        margin-top: 2px;
      }

      .metric-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--brand-primary, #0ea5e9), var(--brand-secondary, #8b5cf6));
        transition: width 0.5s ease;
      }

      .activity-indicator {
        position: absolute;
        top: 0;
        right: 0;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--status-success, #10b981);
        border: 2px solid var(--color-background, #1a1a1a);
      }

      .activity-indicator.active {
        animation: blink 1s ease-in-out infinite;
      }

      @keyframes blink {
        0%, 100% {
          opacity: 1;
        }
        50% {
          opacity: 0.3;
        }
      }
    `;
  }

  protected render(): void {
    if (!this.shadowRoot) return;

    const isActive = this.pulseData.activityLevel > 10;
    const detailsClass = this.showingDetails ? 'visible' : '';

    this.shadowRoot.innerHTML = `
      <style>${this.getDefaultStyles()}</style>
      <div class="pulse-container">
        <div class="pulse-core ${this.pulseData.intelligenceType}"></div>
        ${isActive ? `
          <div class="pulse-ring"></div>
          <div class="pulse-ring"></div>
          <div class="pulse-ring"></div>
        ` : ''}
        ${isActive ? '<div class="activity-indicator active"></div>' : ''}
        <div class="pulse-details ${detailsClass}">
          <div class="details-title">AmI Principles</div>
          ${this.renderMetric('Context Awareness', this.pulseData.contextAwareness)}
          ${this.renderMetric('Proactivity', this.pulseData.proactivity)}
          ${this.renderMetric('Seamlessness', this.pulseData.seamlessness)}
          ${this.renderMetric('Adaptivity', this.pulseData.adaptivity)}
          <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--color-border, #333); text-align: center;">
            <div style="font-size: 10px; color: var(--color-muted-foreground, #888);">
              ${this.getStatusText()}
            </div>
          </div>
        </div>
      </div>
    `;

    this.attachEventListeners();
  }

  protected renderMetric(label: string, value: number): string {
    return `
      <div class="ami-metric">
        <span class="metric-label">${label}</span>
        <span class="metric-value">${value}%</span>
      </div>
      <div class="metric-bar">
        <div class="metric-fill" style="width: ${value}%"></div>
      </div>
    `;
  }

  protected getStatusText(): string {
    switch (this.pulseData.intelligenceType) {
      case 'learning':
        return 'Learning from context...';
      case 'predicting':
        return 'Predicting user needs...';
      case 'adapting':
        return 'Adapting to changes...';
      default:
        return 'Ambient intelligence idle';
    }
  }

  protected toggleDetails(): void {
    this.showingDetails = !this.showingDetails;
    this.render();
    this.emitEvent('details-toggled', { showing: this.showingDetails });
  }

  protected handleWebSocketMessage(data: any): void {
    if (data.type === 'ami_update') {
      this.updatePulse(data.data);
    }
  }

  public updatePulse(data: Partial<AmIPulseData>): void {
    this.pulseData = { ...this.pulseData, ...data, lastActivity: Date.now() };
    this.render();
    this.emitEvent('ami-update', this.pulseData);
  }

  protected onConnect(): void {
    this.render();
  }

  protected onDisconnect(): void {
    // Cleanup
  }

  // Attribute handling
  static get observedAttributes() {
    return [
      'activity-level',
      'context-awareness',
      'proactivity',
      'seamlessness',
      'adaptivity',
      'intelligence-type',
      'ws-url',
    ];
  }

  attributeChangedCallback(name: string, oldValue: string, newValue: string) {
    if (oldValue === newValue) return;

    switch (name) {
      case 'activity-level':
        this.pulseData.activityLevel = parseFloat(newValue) || 0;
        this.render();
        break;
      case 'context-awareness':
        this.pulseData.contextAwareness = parseFloat(newValue) || 0;
        this.render();
        break;
      case 'proactivity':
        this.pulseData.proactivity = parseFloat(newValue) || 0;
        this.render();
        break;
      case 'seamlessness':
        this.pulseData.seamlessness = parseFloat(newValue) || 0;
        this.render();
        break;
      case 'adaptivity':
        this.pulseData.adaptivity = parseFloat(newValue) || 0;
        this.render();
        break;
      case 'intelligence-type':
        this.pulseData.intelligenceType = newValue as any;
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
if (!customElements.get('iv-ami-pulse')) {
  customElements.define('iv-ami-pulse', IVAMIPulse);
}
