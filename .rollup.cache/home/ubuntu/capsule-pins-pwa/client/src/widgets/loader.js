/**
 * Widget Loader
 * Week 8: White-Label Platform - Widget Build System
 *
 * Main entry point for CDN distribution
 * Loads and registers all Industriverse widgets as custom elements
 *
 * Usage:
 * <script src="https://cdn.industriverse.io/widgets/latest/iv-widgets.js"></script>
 * <iv-wallet-orb balance="1000" theme="cosmic"></iv-wallet-orb>
 */
import { __extends } from "tslib";
// Widget registration system
var WidgetRegistry = /** @class */ (function () {
    function WidgetRegistry() {
        this.widgets = new Map();
        this.loaded = new Set();
    }
    WidgetRegistry.prototype.register = function (name, constructor) {
        this.widgets.set(name, constructor);
        if (!customElements.get(name)) {
            customElements.define(name, constructor);
            this.loaded.add(name);
        }
    };
    WidgetRegistry.prototype.get = function (name) {
        return this.widgets.get(name);
    };
    WidgetRegistry.prototype.isLoaded = function (name) {
        return this.loaded.has(name);
    };
    WidgetRegistry.prototype.getAll = function () {
        return Array.from(this.widgets.keys());
    };
    return WidgetRegistry;
}());
// Base widget class
var IndustriverseWidget = /** @class */ (function (_super) {
    __extends(IndustriverseWidget, _super);
    function IndustriverseWidget() {
        var _this = _super.call(this) || this;
        _this.config = {};
        _this.shadow = _this.attachShadow({ mode: 'open' });
        return _this;
    }
    IndustriverseWidget.prototype.connectedCallback = function () {
        this.parseAttributes();
        this.render();
    };
    IndustriverseWidget.prototype.parseAttributes = function () {
        for (var i = 0; i < this.attributes.length; i++) {
            var attr = this.attributes[i];
            var value = attr.value;
            // Try to parse as JSON, fallback to string
            try {
                this.config[attr.name] = JSON.parse(value);
            }
            catch (_a) {
                this.config[attr.name] = value;
            }
        }
    };
    IndustriverseWidget.prototype.render = function () {
        // Override in subclasses
    };
    IndustriverseWidget.prototype.injectStyles = function (css) {
        var style = document.createElement('style');
        style.textContent = css;
        this.shadow.appendChild(style);
    };
    return IndustriverseWidget;
}(HTMLElement));
// Wallet Orb Widget
var WalletOrbWidget = /** @class */ (function (_super) {
    __extends(WalletOrbWidget, _super);
    function WalletOrbWidget() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    WalletOrbWidget.prototype.render = function () {
        var balance = this.config.balance || 0;
        var theme = this.config.theme || 'cosmic';
        this.injectStyles("\n      :host {\n        display: inline-block;\n      }\n      .wallet-orb {\n        width: 120px;\n        height: 120px;\n        border-radius: 50%;\n        background: linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 100%);\n        display: flex;\n        align-items: center;\n        justify-content: center;\n        box-shadow: 0 0 30px rgba(14, 165, 233, 0.5);\n        animation: pulse 2s ease-in-out infinite;\n      }\n      .balance {\n        color: white;\n        font-size: 18px;\n        font-weight: bold;\n        text-align: center;\n      }\n      @keyframes pulse {\n        0%, 100% { box-shadow: 0 0 30px rgba(14, 165, 233, 0.5); }\n        50% { box-shadow: 0 0 50px rgba(139, 92, 246, 0.8); }\n      }\n    ");
        var container = document.createElement('div');
        container.className = 'wallet-orb';
        container.innerHTML = "<div class=\"balance\">".concat(balance, "</div>");
        this.shadow.appendChild(container);
    };
    return WalletOrbWidget;
}(IndustriverseWidget));
// Proof Ticker Widget
var ProofTickerWidget = /** @class */ (function (_super) {
    __extends(ProofTickerWidget, _super);
    function ProofTickerWidget() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ProofTickerWidget.prototype.render = function () {
        var speed = this.config.speed || 30;
        this.injectStyles("\n      :host {\n        display: block;\n        overflow: hidden;\n      }\n      .ticker {\n        display: flex;\n        gap: 20px;\n        animation: scroll ".concat(speed, "s linear infinite;\n      }\n      .proof-item {\n        padding: 8px 16px;\n        background: rgba(14, 165, 233, 0.1);\n        border: 1px solid rgba(14, 165, 233, 0.3);\n        border-radius: 4px;\n        white-space: nowrap;\n        font-size: 14px;\n      }\n      @keyframes scroll {\n        0% { transform: translateX(0); }\n        100% { transform: translateX(-50%); }\n      }\n    "));
        var container = document.createElement('div');
        container.className = 'ticker';
        container.innerHTML = "\n      <div class=\"proof-item\">Proof #1234 verified</div>\n      <div class=\"proof-item\">Proof #1235 verified</div>\n      <div class=\"proof-item\">Proof #1236 verified</div>\n      <div class=\"proof-item\">Proof #1237 verified</div>\n      <div class=\"proof-item\">Proof #1234 verified</div>\n      <div class=\"proof-item\">Proof #1235 verified</div>\n      <div class=\"proof-item\">Proof #1236 verified</div>\n      <div class=\"proof-item\">Proof #1237 verified</div>\n    ";
        this.shadow.appendChild(container);
    };
    return ProofTickerWidget;
}(IndustriverseWidget));
// Capsule Card Widget
var CapsuleCardWidget = /** @class */ (function (_super) {
    __extends(CapsuleCardWidget, _super);
    function CapsuleCardWidget() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    CapsuleCardWidget.prototype.render = function () {
        var title = this.config.title || 'Capsule';
        var status = this.config.status || 'active';
        this.injectStyles("\n      :host {\n        display: inline-block;\n      }\n      .capsule-card {\n        padding: 16px;\n        background: rgba(15, 23, 42, 0.8);\n        border: 1px solid rgba(14, 165, 233, 0.3);\n        border-radius: 8px;\n        min-width: 200px;\n      }\n      .title {\n        font-size: 16px;\n        font-weight: bold;\n        color: #0ea5e9;\n        margin-bottom: 8px;\n      }\n      .status {\n        font-size: 12px;\n        color: #10b981;\n      }\n    ");
        var container = document.createElement('div');
        container.className = 'capsule-card';
        container.innerHTML = "\n      <div class=\"title\">".concat(title, "</div>\n      <div class=\"status\">").concat(status, "</div>\n    ");
        this.shadow.appendChild(container);
    };
    return CapsuleCardWidget;
}(IndustriverseWidget));
// Energy Gauge Widget
var EnergyGaugeWidget = /** @class */ (function (_super) {
    __extends(EnergyGaugeWidget, _super);
    function EnergyGaugeWidget() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    EnergyGaugeWidget.prototype.render = function () {
        var value = this.config.value || 75;
        this.injectStyles("\n      :host {\n        display: inline-block;\n      }\n      .gauge {\n        width: 100px;\n        height: 100px;\n        border-radius: 50%;\n        background: conic-gradient(\n          #10b981 0deg ".concat(value * 3.6, "deg,\n          rgba(16, 185, 129, 0.2) ").concat(value * 3.6, "deg 360deg\n        );\n        display: flex;\n        align-items: center;\n        justify-content: center;\n      }\n      .gauge-inner {\n        width: 70px;\n        height: 70px;\n        border-radius: 50%;\n        background: #0f172a;\n        display: flex;\n        align-items: center;\n        justify-content: center;\n        color: white;\n        font-weight: bold;\n      }\n    "));
        var container = document.createElement('div');
        container.className = 'gauge';
        container.innerHTML = "<div class=\"gauge-inner\">".concat(value, "%</div>");
        this.shadow.appendChild(container);
    };
    return EnergyGaugeWidget;
}(IndustriverseWidget));
// UTID Badge Widget
var UTIDBadgeWidget = /** @class */ (function (_super) {
    __extends(UTIDBadgeWidget, _super);
    function UTIDBadgeWidget() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    UTIDBadgeWidget.prototype.render = function () {
        var utid = this.config.utid || 'UTID-0000';
        this.injectStyles("\n      :host {\n        display: inline-block;\n      }\n      .badge {\n        padding: 8px 16px;\n        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);\n        border-radius: 20px;\n        color: white;\n        font-weight: bold;\n        font-size: 14px;\n      }\n    ");
        var container = document.createElement('div');
        container.className = 'badge';
        container.textContent = utid;
        this.shadow.appendChild(container);
    };
    return UTIDBadgeWidget;
}(IndustriverseWidget));
// AmI Pulse Widget
var AmIPulseWidget = /** @class */ (function (_super) {
    __extends(AmIPulseWidget, _super);
    function AmIPulseWidget() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    AmIPulseWidget.prototype.render = function () {
        var active = this.config.active !== false;
        this.injectStyles("\n      :host {\n        display: inline-block;\n      }\n      .pulse {\n        width: 60px;\n        height: 60px;\n        border-radius: 50%;\n        background: ".concat(active ? '#10b981' : '#6b7280', ";\n        animation: ").concat(active ? 'pulse 1.5s ease-in-out infinite' : 'none', ";\n      }\n      @keyframes pulse {\n        0%, 100% { opacity: 1; transform: scale(1); }\n        50% { opacity: 0.7; transform: scale(1.1); }\n      }\n    "));
        var container = document.createElement('div');
        container.className = 'pulse';
        this.shadow.appendChild(container);
    };
    return AmIPulseWidget;
}(IndustriverseWidget));
// Shadow Twin Widget
var ShadowTwinWidget = /** @class */ (function (_super) {
    __extends(ShadowTwinWidget, _super);
    function ShadowTwinWidget() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ShadowTwinWidget.prototype.render = function () {
        var synced = this.config.synced !== false;
        this.injectStyles("\n      :host {\n        display: inline-block;\n      }\n      .twin {\n        padding: 12px 20px;\n        background: rgba(139, 92, 246, 0.1);\n        border: 2px solid ".concat(synced ? '#10b981' : '#f59e0b', ";\n        border-radius: 8px;\n        color: ").concat(synced ? '#10b981' : '#f59e0b', ";\n        font-weight: bold;\n      }\n    "));
        var container = document.createElement('div');
        container.className = 'twin';
        container.textContent = synced ? '✓ Synced' : '⟳ Syncing...';
        this.shadow.appendChild(container);
    };
    return ShadowTwinWidget;
}(IndustriverseWidget));
// Initialize registry
var registry = new WidgetRegistry();
// Register all widgets
registry.register('iv-wallet-orb', WalletOrbWidget);
registry.register('iv-proof-ticker', ProofTickerWidget);
registry.register('iv-capsule-card', CapsuleCardWidget);
registry.register('iv-energy-gauge', EnergyGaugeWidget);
registry.register('iv-utid-badge', UTIDBadgeWidget);
registry.register('iv-ami-pulse', AmIPulseWidget);
registry.register('iv-shadow-twin', ShadowTwinWidget);
// Export for module usage
export { registry, IndustriverseWidget };
// Global API
window.IVWidgets = {
    registry: registry,
    version: '1.0.0',
    widgets: registry.getAll(),
};
console.log('Industriverse Widgets loaded:', registry.getAll());
//# sourceMappingURL=loader.js.map