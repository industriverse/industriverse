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
import { __extends } from "tslib";
import { IVWidget } from './base/IVWidget';
var IVProofTicker = /** @class */ (function (_super) {
    __extends(IVProofTicker, _super);
    function IVProofTicker() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this.proofs = [];
        _this.maxItems = 10;
        _this.scrollSpeed = 'normal';
        return _this;
    }
    Object.defineProperty(IVProofTicker, "observedAttributes", {
        get: function () {
            return ['max-items', 'scroll-speed'];
        },
        enumerable: false,
        configurable: true
    });
    IVProofTicker.prototype.handleAttributeChange = function (name, oldValue, newValue) {
        if (name === 'max-items') {
            this.maxItems = parseInt(newValue) || 10;
            this.trimProofs();
        }
        else if (name === 'scroll-speed') {
            this.scrollSpeed = newValue || 'normal';
        }
    };
    IVProofTicker.prototype.shouldRerender = function (attributeName) {
        return attributeName === 'scroll-speed';
    };
    IVProofTicker.prototype.render = function () {
        this.shadow.innerHTML = '';
        this.applyStyles(this.getStyles());
        var container = document.createElement('div');
        container.className = 'proof-ticker-container';
        var header = document.createElement('div');
        header.className = 'ticker-header';
        header.innerHTML = "\n      <span class=\"ticker-title\">Live Proofs</span>\n      <span class=\"ticker-count\" id=\"proof-count\">".concat(this.proofs.length, "</span>\n    ");
        var tickerTrack = document.createElement('div');
        tickerTrack.className = 'ticker-track';
        tickerTrack.id = 'ticker-track';
        this.renderProofs(tickerTrack);
        container.appendChild(header);
        container.appendChild(tickerTrack);
        this.shadow.appendChild(container);
    };
    IVProofTicker.prototype.attachEventListeners = function () {
        // Pause on hover
        var track = this.shadow.getElementById('ticker-track');
        if (track) {
            track.addEventListener('mouseenter', function () {
                track.style.animationPlayState = 'paused';
            });
            track.addEventListener('mouseleave', function () {
                track.style.animationPlayState = 'running';
            });
        }
    };
    IVProofTicker.prototype.onWebSocketMessage = function (event) {
        try {
            var data = JSON.parse(event.data);
            if (data.type === 'proof_generated') {
                this.addProof({
                    id: data.id,
                    type: data.proofType,
                    value: data.value,
                    timestamp: Date.now(),
                    source: data.source || 'Unknown',
                });
            }
        }
        catch (error) {
            console.error('Failed to parse WebSocket message:', error);
        }
    };
    IVProofTicker.prototype.addProof = function (proof) {
        this.proofs.unshift(proof);
        this.trimProofs();
        this.updateDisplay();
        this.emitEvent('proof-added', proof);
    };
    IVProofTicker.prototype.trimProofs = function () {
        if (this.proofs.length > this.maxItems) {
            this.proofs = this.proofs.slice(0, this.maxItems);
        }
    };
    IVProofTicker.prototype.updateDisplay = function () {
        var track = this.shadow.getElementById('ticker-track');
        var count = this.shadow.getElementById('proof-count');
        if (track) {
            this.renderProofs(track);
        }
        if (count) {
            count.textContent = this.proofs.length.toString();
        }
    };
    IVProofTicker.prototype.renderProofs = function (container) {
        var _this = this;
        container.innerHTML = '';
        if (this.proofs.length === 0) {
            var empty = document.createElement('div');
            empty.className = 'empty-state';
            empty.textContent = 'Waiting for proofs...';
            container.appendChild(empty);
            return;
        }
        this.proofs.forEach(function (proof) {
            var item = document.createElement('div');
            item.className = "proof-item proof-type-".concat(proof.type);
            item.innerHTML = "\n        <span class=\"proof-icon\">".concat(_this.getProofIcon(proof.type), "</span>\n        <span class=\"proof-type\">").concat(_this.formatProofType(proof.type), "</span>\n        <span class=\"proof-value\">$").concat(proof.value.toFixed(2), "</span>\n        <span class=\"proof-source\">").concat(proof.source, "</span>\n        <span class=\"proof-time\">").concat(_this.formatTime(proof.timestamp), "</span>\n      ");
            container.appendChild(item);
        });
    };
    IVProofTicker.prototype.getProofIcon = function (type) {
        var icons = {
            execution: '⚡',
            energy: '🔋',
            optimization: '🎯',
            calibration: '🔧',
            thermodynamic: '🌡️',
        };
        return icons[type] || '📋';
    };
    IVProofTicker.prototype.formatProofType = function (type) {
        return type.charAt(0).toUpperCase() + type.slice(1);
    };
    IVProofTicker.prototype.formatTime = function (timestamp) {
        var seconds = Math.floor((Date.now() - timestamp) / 1000);
        if (seconds < 60)
            return "".concat(seconds, "s ago");
        var minutes = Math.floor(seconds / 60);
        if (minutes < 60)
            return "".concat(minutes, "m ago");
        var hours = Math.floor(minutes / 60);
        return "".concat(hours, "h ago");
    };
    IVProofTicker.prototype.getStyles = function () {
        var speedMap = {
            slow: '60s',
            normal: '30s',
            fast: '15s',
        };
        var duration = speedMap[this.scrollSpeed];
        return "\n      :host {\n        display: block;\n        width: 100%;\n      }\n\n      .proof-ticker-container {\n        background: ".concat(this.theme.bgSecondary, ";\n        border: 1px solid ").concat(this.theme.borderDefault, ";\n        border-radius: ").concat(this.theme.radiusMd, ";\n        overflow: hidden;\n        box-shadow: ").concat(this.theme.shadowMd, ";\n      }\n\n      .ticker-header {\n        display: flex;\n        justify-content: space-between;\n        align-items: center;\n        padding: 0.75rem 1rem;\n        background: ").concat(this.theme.bgPrimary, ";\n        border-bottom: 1px solid ").concat(this.theme.borderDefault, ";\n      }\n\n      .ticker-title {\n        font-family: ").concat(this.theme.fontHeading, ";\n        font-size: 0.875rem;\n        font-weight: 600;\n        color: ").concat(this.theme.fgPrimary, ";\n        text-transform: uppercase;\n        letter-spacing: 0.05em;\n      }\n\n      .ticker-count {\n        font-family: ").concat(this.theme.fontMono, ";\n        font-size: 0.875rem;\n        font-weight: 600;\n        color: ").concat(this.theme.brandPrimary, ";\n        background: ").concat(this.theme.amiContextGlow, ";\n        padding: 0.25rem 0.5rem;\n        border-radius: 9999px;\n      }\n\n      .ticker-track {\n        padding: 0.5rem 0;\n        max-height: 300px;\n        overflow-y: auto;\n      }\n\n      .ticker-track::-webkit-scrollbar {\n        width: 6px;\n      }\n\n      .ticker-track::-webkit-scrollbar-track {\n        background: ").concat(this.theme.bgPrimary, ";\n      }\n\n      .ticker-track::-webkit-scrollbar-thumb {\n        background: ").concat(this.theme.borderDefault, ";\n        border-radius: 3px;\n      }\n\n      .proof-item {\n        display: flex;\n        align-items: center;\n        gap: 0.75rem;\n        padding: 0.75rem 1rem;\n        border-left: 3px solid transparent;\n        transition: all ").concat(this.theme.durationNormal, " ").concat(this.theme.easingDefault, ";\n        animation: slideIn ").concat(this.theme.durationNormal, " ").concat(this.theme.easingDefault, ";\n      }\n\n      .proof-item:hover {\n        background: ").concat(this.theme.bgPrimary, ";\n      }\n\n      .proof-item.proof-type-execution {\n        border-left-color: ").concat(this.theme.statusInfo, ";\n      }\n\n      .proof-item.proof-type-energy {\n        border-left-color: ").concat(this.theme.statusSuccess, ";\n      }\n\n      .proof-item.proof-type-optimization {\n        border-left-color: ").concat(this.theme.brandPrimary, ";\n      }\n\n      .proof-item.proof-type-calibration {\n        border-left-color: ").concat(this.theme.statusWarning, ";\n      }\n\n      .proof-item.proof-type-thermodynamic {\n        border-left-color: ").concat(this.theme.brandSecondary, ";\n      }\n\n      .proof-icon {\n        font-size: 1.25rem;\n      }\n\n      .proof-type {\n        font-family: ").concat(this.theme.fontBody, ";\n        font-size: 0.875rem;\n        font-weight: 500;\n        color: ").concat(this.theme.fgPrimary, ";\n        min-width: 100px;\n      }\n\n      .proof-value {\n        font-family: ").concat(this.theme.fontMono, ";\n        font-size: 0.875rem;\n        font-weight: 600;\n        color: ").concat(this.theme.statusSuccess, ";\n        min-width: 60px;\n        text-align: right;\n      }\n\n      .proof-source {\n        font-family: ").concat(this.theme.fontMono, ";\n        font-size: 0.75rem;\n        color: ").concat(this.theme.fgSecondary, ";\n        flex: 1;\n        overflow: hidden;\n        text-overflow: ellipsis;\n        white-space: nowrap;\n      }\n\n      .proof-time {\n        font-family: ").concat(this.theme.fontBody, ";\n        font-size: 0.75rem;\n        color: ").concat(this.theme.fgSecondary, ";\n        min-width: 60px;\n        text-align: right;\n      }\n\n      .empty-state {\n        padding: 2rem;\n        text-align: center;\n        color: ").concat(this.theme.fgSecondary, ";\n        font-family: ").concat(this.theme.fontBody, ";\n        font-size: 0.875rem;\n      }\n\n      @keyframes slideIn {\n        from {\n          opacity: 0;\n          transform: translateX(-20px);\n        }\n        to {\n          opacity: 1;\n          transform: translateX(0);\n        }\n      }\n    ");
    };
    return IVProofTicker;
}(IVWidget));
export { IVProofTicker };
// Register custom element
if (!customElements.get('iv-proof-ticker')) {
    customElements.define('iv-proof-ticker', IVProofTicker);
}
//# sourceMappingURL=iv-proof-ticker.js.map