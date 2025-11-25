/**
 * <iv-capsule-card> Widget
 * Week 8: White-Label Platform
 * 
 * Compact capsule display for embedding in dashboards
 * 
 * Usage:
 * <iv-capsule-card
 *   capsule-id="cap_123"
 *   title="Thermal Anomaly Detected"
 *   status="critical"
 *   priority="P5"
 *   source="thermal_sampler"
 *   api-url="https://api.industriverse.io"
 * ></iv-capsule-card>
 */

import { IVWidget } from './base/IVWidget';

type CapsuleStatus = 'active' | 'warning' | 'critical' | 'resolved';

export class IVCapsuleCard extends IVWidget {
  protected capsuleId: string = '';
  protected capsuleTitle: string = '';
  protected capsuleStatus: CapsuleStatus = 'active';
  protected capsulePriority: string = 'P1';
  protected capsuleSource: string = '';
  protected capsuleDescription: string = '';

  static get observedAttributes() {
    return ['capsule-id', 'title', 'status', 'priority', 'source', 'description'];
  }

  protected handleAttributeChange(name: string, oldValue: string, newValue: string): void {
    switch (name) {
      case 'capsule-id':
        this.capsuleId = newValue || '';
        break;
      case 'title':
        this.capsuleTitle = newValue || '';
        break;
      case 'status':
        this.capsuleStatus = (newValue as CapsuleStatus) || 'active';
        break;
      case 'priority':
        this.capsulePriority = newValue || 'P1';
        break;
      case 'source':
        this.capsuleSource = newValue || '';
        break;
      case 'description':
        this.capsuleDescription = newValue || '';
        break;
    }
  }

  protected shouldRerender(attributeName: string): boolean {
    return true; // Re-render on any attribute change
  }

  protected render(): void {
    this.shadow.innerHTML = '';
    this.applyStyles(this.getStyles());

    const card = document.createElement('div');
    card.className = `capsule-card status-${this.capsuleStatus}`;
    card.id = 'card';

    // Status indicator
    const statusIndicator = document.createElement('div');
    statusIndicator.className = 'status-indicator';

    // Header
    const header = document.createElement('div');
    header.className = 'card-header';
    
    const titleEl = document.createElement('div');
    titleEl.className = 'card-title';
    titleEl.textContent = this.capsuleTitle || 'Untitled Capsule';

    const priorityBadge = document.createElement('span');
    priorityBadge.className = `priority-badge priority-${this.capsulePriority.toLowerCase()}`;
    priorityBadge.textContent = this.capsulePriority;

    header.appendChild(titleEl);
    header.appendChild(priorityBadge);

    // Body
    const body = document.createElement('div');
    body.className = 'card-body';

    const sourceEl = document.createElement('div');
    sourceEl.className = 'card-source';
    sourceEl.innerHTML = `<span class="source-label">Source:</span> <span class="source-value">${this.capsuleSource || 'Unknown'}</span>`;

    if (this.capsuleDescription) {
      const descEl = document.createElement('div');
      descEl.className = 'card-description';
      descEl.textContent = this.capsuleDescription;
      body.appendChild(descEl);
    }

    body.appendChild(sourceEl);

    // Footer
    const footer = document.createElement('div');
    footer.className = 'card-footer';

    const statusBadge = document.createElement('span');
    statusBadge.className = `status-badge status-${this.capsuleStatus}`;
    statusBadge.textContent = this.formatStatus(this.capsuleStatus);

    const viewButton = document.createElement('button');
    viewButton.className = 'view-button';
    viewButton.textContent = 'View Details';
    viewButton.id = 'view-button';

    footer.appendChild(statusBadge);
    footer.appendChild(viewButton);

    // Assemble card
    card.appendChild(statusIndicator);
    card.appendChild(header);
    card.appendChild(body);
    card.appendChild(footer);

    this.shadow.appendChild(card);
  }

  protected attachEventListeners(): void {
    const viewButton = this.shadow.getElementById('view-button');
    if (viewButton) {
      viewButton.addEventListener('click', () => {
        this.handleViewClick();
      });
    }

    const card = this.shadow.getElementById('card');
    if (card) {
      card.addEventListener('click', (e) => {
        // Don't trigger if clicking the button
        if ((e.target as HTMLElement).id !== 'view-button') {
          this.handleCardClick();
        }
      });
    }
  }

  private handleViewClick(): void {
    this.emitEvent('view-capsule', {
      capsuleId: this.capsuleId,
      title: this.capsuleTitle,
      status: this.capsuleStatus,
    });
  }

  private handleCardClick(): void {
    this.emitEvent('capsule-click', {
      capsuleId: this.capsuleId,
    });
  }

  private formatStatus(status: CapsuleStatus): string {
    const map: Record<CapsuleStatus, string> = {
      active: 'Active',
      warning: 'Warning',
      critical: 'Critical',
      resolved: 'Resolved',
    };
    return map[status] || status;
  }

  private getStyles(): string {
    const statusColors: Record<CapsuleStatus, string> = {
      active: this.theme.statusInfo,
      warning: this.theme.statusWarning,
      critical: this.theme.statusError,
      resolved: this.theme.statusSuccess,
    };

    return `
      :host {
        display: block;
        width: 100%;
        max-width: 400px;
      }

      .capsule-card {
        background: ${this.theme.bgSecondary};
        border: 1px solid ${this.theme.borderDefault};
        border-radius: ${this.theme.radiusMd};
        overflow: hidden;
        box-shadow: ${this.theme.shadowMd};
        transition: all ${this.theme.durationNormal} ${this.theme.easingDefault};
        cursor: pointer;
        position: relative;
      }

      .capsule-card:hover {
        transform: translateY(-2px);
        box-shadow: ${this.theme.shadowLg};
        border-color: ${statusColors[this.capsuleStatus]};
      }

      .status-indicator {
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: ${statusColors[this.capsuleStatus]};
      }

      .status-indicator::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: ${statusColors[this.capsuleStatus]};
        opacity: 0.5;
        animation: pulse 2s ease-in-out infinite;
      }

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 0.75rem;
        padding: 1rem 1rem 0.5rem 1.5rem;
      }

      .card-title {
        font-family: ${this.theme.fontHeading};
        font-size: 1rem;
        font-weight: 600;
        color: ${this.theme.fgPrimary};
        flex: 1;
        line-height: 1.4;
      }

      .priority-badge {
        font-family: ${this.theme.fontMono};
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.5rem;
        border-radius: 9999px;
        white-space: nowrap;
      }

      .priority-badge.priority-p5 {
        background: ${this.theme.statusError};
        color: white;
      }

      .priority-badge.priority-p4 {
        background: ${this.theme.statusWarning};
        color: ${this.theme.bgPrimary};
      }

      .priority-badge.priority-p3 {
        background: ${this.theme.statusInfo};
        color: white;
      }

      .priority-badge.priority-p2,
      .priority-badge.priority-p1 {
        background: ${this.theme.borderDefault};
        color: ${this.theme.fgPrimary};
      }

      .card-body {
        padding: 0.5rem 1rem 0.5rem 1.5rem;
      }

      .card-description {
        font-family: ${this.theme.fontBody};
        font-size: 0.875rem;
        color: ${this.theme.fgSecondary};
        line-height: 1.5;
        margin-bottom: 0.75rem;
      }

      .card-source {
        font-family: ${this.theme.fontBody};
        font-size: 0.75rem;
        color: ${this.theme.fgSecondary};
      }

      .source-label {
        font-weight: 600;
        color: ${this.theme.fgPrimary};
      }

      .source-value {
        font-family: ${this.theme.fontMono};
        color: ${this.theme.brandPrimary};
      }

      .card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 1rem 0.75rem 1.5rem;
        background: ${this.theme.bgPrimary};
        border-top: 1px solid ${this.theme.borderDefault};
      }

      .status-badge {
        font-family: ${this.theme.fontBody};
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }

      .status-badge.status-active {
        background: ${this.theme.amiContextGlow};
        color: ${this.theme.statusInfo};
      }

      .status-badge.status-warning {
        background: ${this.theme.amiAdaptationFade};
        color: ${this.theme.statusWarning};
      }

      .status-badge.status-critical {
        background: rgba(239, 68, 68, 0.2);
        color: ${this.theme.statusError};
      }

      .status-badge.status-resolved {
        background: rgba(16, 185, 129, 0.2);
        color: ${this.theme.statusSuccess};
      }

      .view-button {
        font-family: ${this.theme.fontBody};
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.375rem 0.75rem;
        background: ${this.theme.brandPrimary};
        color: white;
        border: none;
        border-radius: ${this.theme.radiusMd};
        cursor: pointer;
        transition: all ${this.theme.durationNormal} ${this.theme.easingDefault};
      }

      .view-button:hover {
        background: ${this.theme.brandSecondary};
        transform: translateY(-1px);
      }

      .view-button:active {
        transform: translateY(0);
      }

      @keyframes pulse {
        0%, 100% {
          opacity: 0.5;
        }
        50% {
          opacity: 1;
        }
      }
    `;
  }
}

// Register custom element
if (!customElements.get('iv-capsule-card')) {
  customElements.define('iv-capsule-card', IVCapsuleCard);
}
