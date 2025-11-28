/**
 * IVWidget Base Class
 * Week 8: White-Label Platform - Widget Architecture
 * 
 * Base class for all <iv-*> custom elements
 * Provides theme integration, WebSocket support, and lifecycle management
 */

export interface IVWidgetConfig {
  apiUrl?: string;
  wsUrl?: string;
  userId?: string;
  themeMode?: string;
  autoConnect?: boolean;
}

export abstract class IVWidget extends HTMLElement {
  protected shadow: ShadowRoot;
  protected theme: Record<string, string> = {};
  protected ws: WebSocket | null = null;
  protected config: IVWidgetConfig = {};
  protected wsConnected: boolean = false;

  constructor() {
    super();
    this.shadow = this.attachShadow({ mode: 'open' });
  }

  /**
   * Lifecycle: Element added to DOM
   */
  connectedCallback() {
    this.loadConfig();
    this.loadTheme();
    this.render();
    this.attachEventListeners();
    
    if (this.config.autoConnect !== false && this.config.wsUrl) {
      this.connectWebSocket();
    }
  }

  /**
   * Lifecycle: Element removed from DOM
   */
  disconnectedCallback() {
    this.disconnectWebSocket();
    this.cleanup();
  }

  /**
   * Lifecycle: Attribute changed
   */
  attributeChangedCallback(name: string, oldValue: string, newValue: string) {
    if (oldValue === newValue) return;
    
    this.handleAttributeChange(name, oldValue, newValue);
    
    // Re-render if significant attribute changed
    if (this.shouldRerender(name)) {
      this.render();
    }
  }

  /**
   * Load configuration from attributes
   */
  protected loadConfig(): void {
    this.config = {
      apiUrl: this.getAttribute('api-url') || undefined,
      wsUrl: this.getAttribute('ws-url') || undefined,
      userId: this.getAttribute('user-id') || undefined,
      themeMode: this.getAttribute('theme-mode') || undefined,
      autoConnect: this.getAttribute('auto-connect') !== 'false',
    };
  }

  /**
   * Load theme from CSS custom properties
   */
  protected loadTheme(): void {
    const computedStyle = getComputedStyle(document.documentElement);
    
    this.theme = {
      // Brand colors
      brandPrimary: computedStyle.getPropertyValue('--brand-primary').trim() || '#0ea5e9',
      brandSecondary: computedStyle.getPropertyValue('--brand-secondary').trim() || '#8b5cf6',
      brandAccent: computedStyle.getPropertyValue('--brand-accent').trim() || '#f59e0b',
      
      // Status colors
      statusSuccess: computedStyle.getPropertyValue('--status-success').trim() || '#10b981',
      statusWarning: computedStyle.getPropertyValue('--status-warning').trim() || '#f59e0b',
      statusError: computedStyle.getPropertyValue('--status-error').trim() || '#ef4444',
      statusInfo: computedStyle.getPropertyValue('--status-info').trim() || '#3b82f6',
      
      // Semantic colors
      bgPrimary: computedStyle.getPropertyValue('--bg-primary').trim() || '#0f172a',
      bgSecondary: computedStyle.getPropertyValue('--bg-secondary').trim() || '#1e293b',
      fgPrimary: computedStyle.getPropertyValue('--fg-primary').trim() || '#f8fafc',
      fgSecondary: computedStyle.getPropertyValue('--fg-secondary').trim() || '#cbd5e1',
      borderDefault: computedStyle.getPropertyValue('--border-default').trim() || '#334155',
      
      // AmI colors
      amiContextGlow: computedStyle.getPropertyValue('--ami-context-glow').trim() || 'rgba(14, 165, 233, 0.3)',
      amiPredictionPulse: computedStyle.getPropertyValue('--ami-prediction-pulse').trim() || 'rgba(139, 92, 246, 0.4)',
      amiAdaptationFade: computedStyle.getPropertyValue('--ami-adaptation-fade').trim() || 'rgba(245, 158, 11, 0.2)',
      
      // Typography
      fontHeading: computedStyle.getPropertyValue('--font-heading').trim() || "'Inter', sans-serif",
      fontBody: computedStyle.getPropertyValue('--font-body').trim() || "'Inter', sans-serif",
      fontMono: computedStyle.getPropertyValue('--font-mono').trim() || "'JetBrains Mono', monospace",
      
      // Effects
      radiusMd: computedStyle.getPropertyValue('--radius-md').trim() || '0.5rem',
      shadowMd: computedStyle.getPropertyValue('--shadow-md').trim() || '0 4px 6px -1px rgb(0 0 0 / 0.1)',
      
      // Animations
      durationNormal: computedStyle.getPropertyValue('--duration-normal').trim() || '300ms',
      easingDefault: computedStyle.getPropertyValue('--easing-default').trim() || 'cubic-bezier(0.4, 0, 0.2, 1)',
    };
  }

  /**
   * Connect to WebSocket
   */
  protected connectWebSocket(): void {
    if (!this.config.wsUrl) return;
    
    try {
      this.ws = new WebSocket(this.config.wsUrl);
      
      this.ws.onopen = () => {
        this.wsConnected = true;
        this.onWebSocketOpen();
      };
      
      this.ws.onmessage = (event) => {
        this.onWebSocketMessage(event);
      };
      
      this.ws.onerror = (error) => {
        this.onWebSocketError(error);
      };
      
      this.ws.onclose = () => {
        this.wsConnected = false;
        this.onWebSocketClose();
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  }

  /**
   * Disconnect from WebSocket
   */
  protected disconnectWebSocket(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.wsConnected = false;
    }
  }

  /**
   * Send message via WebSocket
   */
  protected sendWebSocketMessage(data: any): void {
    if (this.ws && this.wsConnected) {
      this.ws.send(JSON.stringify(data));
    }
  }

  /**
   * Apply styles to shadow DOM
   */
  protected applyStyles(styles: string): void {
    const styleEl = document.createElement('style');
    styleEl.textContent = styles;
    this.shadow.appendChild(styleEl);
  }

  /**
   * Emit custom event
   */
  protected emitEvent(name: string, detail?: any): void {
    this.dispatchEvent(new CustomEvent(name, {
      detail,
      bubbles: true,
      composed: true,
    }));
  }

  // Abstract methods to be implemented by subclasses
  protected abstract render(): void;
  protected abstract attachEventListeners(): void;
  
  // Optional lifecycle hooks
  protected handleAttributeChange(name: string, oldValue: string, newValue: string): void {}
  protected shouldRerender(attributeName: string): boolean { return false; }
  protected onWebSocketOpen(): void {}
  protected onWebSocketMessage(event: MessageEvent): void {}
  protected onWebSocketError(error: Event): void {}
  protected onWebSocketClose(): void {}
  protected cleanup(): void {}
}
