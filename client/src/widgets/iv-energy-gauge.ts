/**
 * <iv-energy-gauge> Widget
 * Week 8: White-Label Platform
 * 
 * Real-time energy consumption gauge with threshold indicators
 * Features:
 * - Circular gauge with animated needle
 * - Color-coded zones (green/yellow/red)
 * - Current/peak/average values
 * - WebSocket updates
 * - AmI glow effects
 */

import { IVWidget } from './base/IVWidget';

interface EnergyData {
  current: number;
  peak: number;
  average: number;
  unit: string;
  timestamp: number;
  threshold_warning: number;
  threshold_critical: number;
}

export class IVEnergyGauge extends IVWidget {
  protected attachEventListeners(): void {
    // No DOM event listeners needed for gauge
  }
  protected energyData: EnergyData = {
    current: 0,
    peak: 0,
    average: 0,
    unit: 'kW',
    timestamp: Date.now(),
    threshold_warning: 75,
    threshold_critical: 90,
  };

  protected canvas: HTMLCanvasElement | null = null;
  protected ctx: CanvasRenderingContext2D | null = null;
  protected animationFrame: number | null = null;
  protected targetValue: number = 0;
  protected currentValue: number = 0;

  constructor() {
    super();
    this.setupCanvas();
  }

  protected setupCanvas() {
    this.canvas = document.createElement('canvas');
    this.canvas.width = 300;
    this.canvas.height = 300;
    this.ctx = this.canvas.getContext('2d');
  }

  protected getDefaultStyles(): string {
    return `
      :host {
        display: block;
        width: 300px;
        height: 400px;
        font-family: var(--font-sans, system-ui, sans-serif);
      }

      .gauge-container {
        background: var(--color-background, #1a1a1a);
        border: 1px solid var(--color-border, #333);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
      }

      .gauge-container:hover {
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.4);
      }

      .gauge-title {
        font-size: 14px;
        font-weight: 600;
        color: var(--color-foreground, #e5e5e5);
        margin-bottom: 16px;
        text-align: center;
      }

      .gauge-canvas {
        display: block;
        margin: 0 auto;
      }

      .gauge-stats {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-top: 16px;
      }

      .stat {
        text-align: center;
      }

      .stat-label {
        font-size: 11px;
        color: var(--color-muted-foreground, #888);
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .stat-value {
        font-size: 18px;
        font-weight: 700;
        color: var(--color-foreground, #e5e5e5);
        margin-top: 4px;
      }

      .stat-unit {
        font-size: 12px;
        color: var(--color-muted-foreground, #888);
        margin-left: 2px;
      }

      /* AmI glow effects */
      .gauge-container.warning {
        box-shadow: 0 0 20px rgba(251, 191, 36, 0.3);
      }

      .gauge-container.critical {
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.3);
        animation: pulse-critical 2s ease-in-out infinite;
      }

      @keyframes pulse-critical {
        0%, 100% {
          box-shadow: 0 0 20px rgba(239, 68, 68, 0.3);
        }
        50% {
          box-shadow: 0 0 30px rgba(239, 68, 68, 0.5);
        }
      }
    `;
  }

  protected render(): void {
    if (!this.shadowRoot) return;

    const percentage = (this.energyData.current / this.energyData.peak) * 100;
    let statusClass = '';
    if (percentage >= this.energyData.threshold_critical) {
      statusClass = 'critical';
    } else if (percentage >= this.energyData.threshold_warning) {
      statusClass = 'warning';
    }

    this.shadowRoot.innerHTML = `
      <style>${this.getDefaultStyles()}</style>
      <div class="gauge-container ${statusClass}">
        <div class="gauge-title">Energy Consumption</div>
        <canvas class="gauge-canvas" width="300" height="300"></canvas>
        <div class="gauge-stats">
          <div class="stat">
            <div class="stat-label">Current</div>
            <div class="stat-value">
              ${this.energyData.current.toFixed(1)}
              <span class="stat-unit">${this.energyData.unit}</span>
            </div>
          </div>
          <div class="stat">
            <div class="stat-label">Peak</div>
            <div class="stat-value">
              ${this.energyData.peak.toFixed(1)}
              <span class="stat-unit">${this.energyData.unit}</span>
            </div>
          </div>
          <div class="stat">
            <div class="stat-label">Average</div>
            <div class="stat-value">
              ${this.energyData.average.toFixed(1)}
              <span class="stat-unit">${this.energyData.unit}</span>
            </div>
          </div>
        </div>
      </div>
    `;

    // Get canvas from shadow DOM
    this.canvas = this.shadowRoot.querySelector('.gauge-canvas');
    if (this.canvas) {
      this.ctx = this.canvas.getContext('2d');
      this.drawGauge();
    }
  }

  protected drawGauge(): void {
    if (!this.ctx || !this.canvas) return;

    const width = this.canvas.width;
    const height = this.canvas.height;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 2 - 40;

    // Clear canvas
    this.ctx.clearRect(0, 0, width, height);

    // Animate current value towards target
    const diff = this.targetValue - this.currentValue;
    if (Math.abs(diff) > 0.1) {
      this.currentValue += diff * 0.1;
      this.animationFrame = requestAnimationFrame(() => this.drawGauge());
    } else {
      this.currentValue = this.targetValue;
    }

    // Draw gauge background
    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY, radius, 0.75 * Math.PI, 2.25 * Math.PI);
    this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    this.ctx.lineWidth = 20;
    this.ctx.stroke();

    // Draw colored zones
    const warningAngle = 0.75 * Math.PI + (this.energyData.threshold_warning / 100) * 1.5 * Math.PI;
    const criticalAngle = 0.75 * Math.PI + (this.energyData.threshold_critical / 100) * 1.5 * Math.PI;

    // Green zone (0 - warning)
    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY, radius, 0.75 * Math.PI, warningAngle);
    this.ctx.strokeStyle = 'rgba(34, 197, 94, 0.3)';
    this.ctx.lineWidth = 20;
    this.ctx.stroke();

    // Yellow zone (warning - critical)
    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY, radius, warningAngle, criticalAngle);
    this.ctx.strokeStyle = 'rgba(251, 191, 36, 0.3)';
    this.ctx.lineWidth = 20;
    this.ctx.stroke();

    // Red zone (critical - max)
    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY, radius, criticalAngle, 2.25 * Math.PI);
    this.ctx.strokeStyle = 'rgba(239, 68, 68, 0.3)';
    this.ctx.lineWidth = 20;
    this.ctx.stroke();

    // Draw current value arc
    const percentage = this.currentValue / 100;
    const endAngle = 0.75 * Math.PI + percentage * 1.5 * Math.PI;

    let arcColor = '#22c55e'; // green
    if (percentage >= this.energyData.threshold_critical / 100) {
      arcColor = '#ef4444'; // red
    } else if (percentage >= this.energyData.threshold_warning / 100) {
      arcColor = '#fbbf24'; // yellow
    }

    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY, radius, 0.75 * Math.PI, endAngle);
    this.ctx.strokeStyle = arcColor;
    this.ctx.lineWidth = 20;
    this.ctx.lineCap = 'round';
    this.ctx.stroke();

    // Draw needle
    const needleAngle = 0.75 * Math.PI + percentage * 1.5 * Math.PI;
    const needleLength = radius - 30;

    this.ctx.save();
    this.ctx.translate(centerX, centerY);
    this.ctx.rotate(needleAngle);

    // Needle shadow
    this.ctx.beginPath();
    this.ctx.moveTo(0, 0);
    this.ctx.lineTo(needleLength + 2, 2);
    this.ctx.strokeStyle = 'rgba(0, 0, 0, 0.3)';
    this.ctx.lineWidth = 3;
    this.ctx.stroke();

    // Needle
    this.ctx.beginPath();
    this.ctx.moveTo(0, 0);
    this.ctx.lineTo(needleLength, 0);
    this.ctx.strokeStyle = '#e5e5e5';
    this.ctx.lineWidth = 3;
    this.ctx.stroke();

    this.ctx.restore();

    // Draw center circle
    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY, 8, 0, 2 * Math.PI);
    this.ctx.fillStyle = '#e5e5e5';
    this.ctx.fill();

    // Draw percentage text
    this.ctx.font = 'bold 32px system-ui';
    this.ctx.fillStyle = '#e5e5e5';
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'middle';
    this.ctx.fillText(`${Math.round(percentage * 100)}%`, centerX, centerY + 60);
  }

  protected handleWebSocketMessage(data: any): void {
    if (data.type === 'energy_update') {
      this.updateEnergy(data.data);
    }
  }

  public updateEnergy(data: Partial<EnergyData>): void {
    this.energyData = { ...this.energyData, ...data };
    this.targetValue = (this.energyData.current / this.energyData.peak) * 100;
    this.render();
    this.emitEvent('energy-update', this.energyData);
  }

  protected onConnect(): void {
    this.render();
  }

  protected onDisconnect(): void {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
    }
  }

  // Attribute handling
  static get observedAttributes() {
    return ['current', 'peak', 'average', 'unit', 'threshold-warning', 'threshold-critical', 'ws-url', 'auto-connect'];
  }

  attributeChangedCallback(name: string, oldValue: string, newValue: string) {
    if (oldValue === newValue) return;

    switch (name) {
      case 'current':
        this.energyData.current = parseFloat(newValue) || 0;
        this.targetValue = (this.energyData.current / this.energyData.peak) * 100;
        this.render();
        break;
      case 'peak':
        this.energyData.peak = parseFloat(newValue) || 100;
        this.render();
        break;
      case 'average':
        this.energyData.average = parseFloat(newValue) || 0;
        this.render();
        break;
      case 'unit':
        this.energyData.unit = newValue;
        this.render();
        break;
      case 'threshold-warning':
        this.energyData.threshold_warning = parseFloat(newValue) || 75;
        this.render();
        break;
      case 'threshold-critical':
        this.energyData.threshold_critical = parseFloat(newValue) || 90;
        this.render();
        break;
      case 'ws-url':
        this.config.wsUrl = newValue;
        if (newValue) {
          this.connectWebSocket();
        }
        break;
      case 'auto-connect':
        // Auto-connect handled by ws-url attribute
        break;
    }
  }
}

// Register custom element
if (!customElements.get('iv-energy-gauge')) {
  customElements.define('iv-energy-gauge', IVEnergyGauge);
}
