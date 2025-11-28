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
import { __assign, __extends } from "tslib";
import { IVWidget } from './base/IVWidget';
var IVAMIPulse = /** @class */ (function (_super) {
    __extends(IVAMIPulse, _super);
    function IVAMIPulse() {
        var _this = _super.call(this) || this;
        _this.pulseData = {
            activityLevel: 0,
            contextAwareness: 0,
            proactivity: 0,
            seamlessness: 0,
            adaptivity: 0,
            intelligenceType: 'idle',
            lastActivity: Date.now(),
        };
        _this.showingDetails = false;
        return _this;
    }
    IVAMIPulse.prototype.attachEventListeners = function () {
        var _this = this;
        var _a;
        var container = (_a = this.shadowRoot) === null || _a === void 0 ? void 0 : _a.querySelector('.pulse-container');
        container === null || container === void 0 ? void 0 : container.addEventListener('click', function () { return _this.toggleDetails(); });
    };
    IVAMIPulse.prototype.getDefaultStyles = function () {
        return "\n      :host {\n        display: inline-block;\n        font-family: var(--font-sans, system-ui, sans-serif);\n      }\n\n      .pulse-container {\n        position: relative;\n        width: 60px;\n        height: 60px;\n        cursor: pointer;\n        transition: transform 0.2s ease;\n      }\n\n      .pulse-container:hover {\n        transform: scale(1.1);\n      }\n\n      .pulse-core {\n        position: absolute;\n        top: 50%;\n        left: 50%;\n        transform: translate(-50%, -50%);\n        width: 20px;\n        height: 20px;\n        border-radius: 50%;\n        background: var(--ami-context-glow, rgba(14, 165, 233, 0.8));\n        box-shadow: 0 0 10px var(--ami-context-glow, rgba(14, 165, 233, 0.5));\n        transition: all 0.3s ease;\n      }\n\n      .pulse-core.learning {\n        background: var(--brand-primary, #0ea5e9);\n        box-shadow: 0 0 15px var(--brand-primary, #0ea5e9);\n      }\n\n      .pulse-core.predicting {\n        background: var(--brand-secondary, #8b5cf6);\n        box-shadow: 0 0 15px var(--brand-secondary, #8b5cf6);\n      }\n\n      .pulse-core.adapting {\n        background: var(--brand-accent, #f59e0b);\n        box-shadow: 0 0 15px var(--brand-accent, #f59e0b);\n      }\n\n      .pulse-core.idle {\n        background: var(--color-muted, #64748b);\n        box-shadow: 0 0 5px var(--color-muted, #64748b);\n      }\n\n      .pulse-ring {\n        position: absolute;\n        top: 50%;\n        left: 50%;\n        transform: translate(-50%, -50%);\n        border-radius: 50%;\n        border: 2px solid var(--ami-context-glow, rgba(14, 165, 233, 0.5));\n        animation: pulse-expand 2s ease-out infinite;\n      }\n\n      .pulse-ring:nth-child(2) {\n        animation-delay: 0.5s;\n      }\n\n      .pulse-ring:nth-child(3) {\n        animation-delay: 1s;\n      }\n\n      @keyframes pulse-expand {\n        0% {\n          width: 20px;\n          height: 20px;\n          opacity: 1;\n        }\n        100% {\n          width: 60px;\n          height: 60px;\n          opacity: 0;\n        }\n      }\n\n      .pulse-details {\n        position: absolute;\n        top: 70px;\n        left: 50%;\n        transform: translateX(-50%);\n        background: var(--color-background, #1a1a1a);\n        border: 1px solid var(--color-border, #333);\n        border-radius: 8px;\n        padding: 12px;\n        min-width: 200px;\n        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);\n        z-index: 100;\n        opacity: 0;\n        pointer-events: none;\n        transition: opacity 0.2s ease;\n      }\n\n      .pulse-details.visible {\n        opacity: 1;\n        pointer-events: auto;\n      }\n\n      .details-title {\n        font-size: 12px;\n        font-weight: 600;\n        color: var(--color-foreground, #e5e5e5);\n        margin-bottom: 8px;\n        text-align: center;\n      }\n\n      .ami-metric {\n        display: flex;\n        justify-content: space-between;\n        align-items: center;\n        margin-bottom: 6px;\n        font-size: 11px;\n      }\n\n      .metric-label {\n        color: var(--color-muted-foreground, #888);\n      }\n\n      .metric-value {\n        color: var(--color-foreground, #e5e5e5);\n        font-weight: 600;\n      }\n\n      .metric-bar {\n        width: 100%;\n        height: 3px;\n        background: rgba(255, 255, 255, 0.1);\n        border-radius: 2px;\n        overflow: hidden;\n        margin-top: 2px;\n      }\n\n      .metric-fill {\n        height: 100%;\n        background: linear-gradient(90deg, var(--brand-primary, #0ea5e9), var(--brand-secondary, #8b5cf6));\n        transition: width 0.5s ease;\n      }\n\n      .activity-indicator {\n        position: absolute;\n        top: 0;\n        right: 0;\n        width: 8px;\n        height: 8px;\n        border-radius: 50%;\n        background: var(--status-success, #10b981);\n        border: 2px solid var(--color-background, #1a1a1a);\n      }\n\n      .activity-indicator.active {\n        animation: blink 1s ease-in-out infinite;\n      }\n\n      @keyframes blink {\n        0%, 100% {\n          opacity: 1;\n        }\n        50% {\n          opacity: 0.3;\n        }\n      }\n    ";
    };
    IVAMIPulse.prototype.render = function () {
        if (!this.shadowRoot)
            return;
        var isActive = this.pulseData.activityLevel > 10;
        var detailsClass = this.showingDetails ? 'visible' : '';
        this.shadowRoot.innerHTML = "\n      <style>".concat(this.getDefaultStyles(), "</style>\n      <div class=\"pulse-container\">\n        <div class=\"pulse-core ").concat(this.pulseData.intelligenceType, "\"></div>\n        ").concat(isActive ? "\n          <div class=\"pulse-ring\"></div>\n          <div class=\"pulse-ring\"></div>\n          <div class=\"pulse-ring\"></div>\n        " : '', "\n        ").concat(isActive ? '<div class="activity-indicator active"></div>' : '', "\n        <div class=\"pulse-details ").concat(detailsClass, "\">\n          <div class=\"details-title\">AmI Principles</div>\n          ").concat(this.renderMetric('Context Awareness', this.pulseData.contextAwareness), "\n          ").concat(this.renderMetric('Proactivity', this.pulseData.proactivity), "\n          ").concat(this.renderMetric('Seamlessness', this.pulseData.seamlessness), "\n          ").concat(this.renderMetric('Adaptivity', this.pulseData.adaptivity), "\n          <div style=\"margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--color-border, #333); text-align: center;\">\n            <div style=\"font-size: 10px; color: var(--color-muted-foreground, #888);\">\n              ").concat(this.getStatusText(), "\n            </div>\n          </div>\n        </div>\n      </div>\n    ");
        this.attachEventListeners();
    };
    IVAMIPulse.prototype.renderMetric = function (label, value) {
        return "\n      <div class=\"ami-metric\">\n        <span class=\"metric-label\">".concat(label, "</span>\n        <span class=\"metric-value\">").concat(value, "%</span>\n      </div>\n      <div class=\"metric-bar\">\n        <div class=\"metric-fill\" style=\"width: ").concat(value, "%\"></div>\n      </div>\n    ");
    };
    IVAMIPulse.prototype.getStatusText = function () {
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
    };
    IVAMIPulse.prototype.toggleDetails = function () {
        this.showingDetails = !this.showingDetails;
        this.render();
        this.emitEvent('details-toggled', { showing: this.showingDetails });
    };
    IVAMIPulse.prototype.handleWebSocketMessage = function (data) {
        if (data.type === 'ami_update') {
            this.updatePulse(data.data);
        }
    };
    IVAMIPulse.prototype.updatePulse = function (data) {
        this.pulseData = __assign(__assign(__assign({}, this.pulseData), data), { lastActivity: Date.now() });
        this.render();
        this.emitEvent('ami-update', this.pulseData);
    };
    IVAMIPulse.prototype.onConnect = function () {
        this.render();
    };
    IVAMIPulse.prototype.onDisconnect = function () {
        // Cleanup
    };
    Object.defineProperty(IVAMIPulse, "observedAttributes", {
        // Attribute handling
        get: function () {
            return [
                'activity-level',
                'context-awareness',
                'proactivity',
                'seamlessness',
                'adaptivity',
                'intelligence-type',
                'ws-url',
            ];
        },
        enumerable: false,
        configurable: true
    });
    IVAMIPulse.prototype.attributeChangedCallback = function (name, oldValue, newValue) {
        if (oldValue === newValue)
            return;
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
                this.pulseData.intelligenceType = newValue;
                this.render();
                break;
            case 'ws-url':
                this.config.wsUrl = newValue;
                if (newValue) {
                    this.connectWebSocket();
                }
                break;
        }
    };
    return IVAMIPulse;
}(IVWidget));
export { IVAMIPulse };
// Register custom element
if (!customElements.get('iv-ami-pulse')) {
    customElements.define('iv-ami-pulse', IVAMIPulse);
}
//# sourceMappingURL=iv-ami-pulse.js.map