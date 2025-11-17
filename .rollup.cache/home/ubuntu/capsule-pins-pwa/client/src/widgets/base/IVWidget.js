/**
 * IVWidget Base Class
 * Week 8: White-Label Platform - Widget Architecture
 *
 * Base class for all <iv-*> custom elements
 * Provides theme integration, WebSocket support, and lifecycle management
 */
import { __extends } from "tslib";
var IVWidget = /** @class */ (function (_super) {
    __extends(IVWidget, _super);
    function IVWidget() {
        var _this = _super.call(this) || this;
        _this.theme = {};
        _this.ws = null;
        _this.config = {};
        _this.wsConnected = false;
        _this.shadow = _this.attachShadow({ mode: 'open' });
        return _this;
    }
    /**
     * Lifecycle: Element added to DOM
     */
    IVWidget.prototype.connectedCallback = function () {
        this.loadConfig();
        this.loadTheme();
        this.render();
        this.attachEventListeners();
        if (this.config.autoConnect !== false && this.config.wsUrl) {
            this.connectWebSocket();
        }
    };
    /**
     * Lifecycle: Element removed from DOM
     */
    IVWidget.prototype.disconnectedCallback = function () {
        this.disconnectWebSocket();
        this.cleanup();
    };
    /**
     * Lifecycle: Attribute changed
     */
    IVWidget.prototype.attributeChangedCallback = function (name, oldValue, newValue) {
        if (oldValue === newValue)
            return;
        this.handleAttributeChange(name, oldValue, newValue);
        // Re-render if significant attribute changed
        if (this.shouldRerender(name)) {
            this.render();
        }
    };
    /**
     * Load configuration from attributes
     */
    IVWidget.prototype.loadConfig = function () {
        this.config = {
            apiUrl: this.getAttribute('api-url') || undefined,
            wsUrl: this.getAttribute('ws-url') || undefined,
            userId: this.getAttribute('user-id') || undefined,
            themeMode: this.getAttribute('theme-mode') || undefined,
            autoConnect: this.getAttribute('auto-connect') !== 'false',
        };
    };
    /**
     * Load theme from CSS custom properties
     */
    IVWidget.prototype.loadTheme = function () {
        var computedStyle = getComputedStyle(document.documentElement);
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
    };
    /**
     * Connect to WebSocket
     */
    IVWidget.prototype.connectWebSocket = function () {
        var _this = this;
        if (!this.config.wsUrl)
            return;
        try {
            this.ws = new WebSocket(this.config.wsUrl);
            this.ws.onopen = function () {
                _this.wsConnected = true;
                _this.onWebSocketOpen();
            };
            this.ws.onmessage = function (event) {
                _this.onWebSocketMessage(event);
            };
            this.ws.onerror = function (error) {
                _this.onWebSocketError(error);
            };
            this.ws.onclose = function () {
                _this.wsConnected = false;
                _this.onWebSocketClose();
            };
        }
        catch (error) {
            console.error('Failed to connect WebSocket:', error);
        }
    };
    /**
     * Disconnect from WebSocket
     */
    IVWidget.prototype.disconnectWebSocket = function () {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
            this.wsConnected = false;
        }
    };
    /**
     * Send message via WebSocket
     */
    IVWidget.prototype.sendWebSocketMessage = function (data) {
        if (this.ws && this.wsConnected) {
            this.ws.send(JSON.stringify(data));
        }
    };
    /**
     * Apply styles to shadow DOM
     */
    IVWidget.prototype.applyStyles = function (styles) {
        var styleEl = document.createElement('style');
        styleEl.textContent = styles;
        this.shadow.appendChild(styleEl);
    };
    /**
     * Emit custom event
     */
    IVWidget.prototype.emitEvent = function (name, detail) {
        this.dispatchEvent(new CustomEvent(name, {
            detail: detail,
            bubbles: true,
            composed: true,
        }));
    };
    // Optional lifecycle hooks
    IVWidget.prototype.handleAttributeChange = function (name, oldValue, newValue) { };
    IVWidget.prototype.shouldRerender = function (attributeName) { return false; };
    IVWidget.prototype.onWebSocketOpen = function () { };
    IVWidget.prototype.onWebSocketMessage = function (event) { };
    IVWidget.prototype.onWebSocketError = function (error) { };
    IVWidget.prototype.onWebSocketClose = function () { };
    IVWidget.prototype.cleanup = function () { };
    return IVWidget;
}(HTMLElement));
export { IVWidget };
//# sourceMappingURL=IVWidget.js.map