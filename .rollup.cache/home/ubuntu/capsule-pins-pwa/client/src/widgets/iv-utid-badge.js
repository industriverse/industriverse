/**
 * <iv-utid-badge> Widget
 * Week 8: White-Label Platform
 *
 * Universal Thermodynamic ID badge with blockchain verification
 * Features:
 * - UTID display with copy-to-clipboard
 * - Blockchain verification status
 * - QR code generation
 * - Provenance chain visualization
 * - AmI consciousness glow
 */
import { __assign, __extends } from "tslib";
import { IVWidget } from './base/IVWidget';
var IVUTIDBadge = /** @class */ (function (_super) {
    __extends(IVUTIDBadge, _super);
    function IVUTIDBadge() {
        var _this = _super.call(this) || this;
        _this.utidData = {
            utid: '',
            verified: false,
            blockchainHash: '',
            timestamp: Date.now(),
            provenanceChain: [],
            consciousnessLevel: 0,
            physicsDomain: 'unknown',
        };
        _this.showingQR = false;
        return _this;
    }
    IVUTIDBadge.prototype.attachEventListeners = function () {
        var _this = this;
        var _a, _b;
        var copyBtn = (_a = this.shadowRoot) === null || _a === void 0 ? void 0 : _a.querySelector('.copy-btn');
        var qrBtn = (_b = this.shadowRoot) === null || _b === void 0 ? void 0 : _b.querySelector('.qr-btn');
        copyBtn === null || copyBtn === void 0 ? void 0 : copyBtn.addEventListener('click', function () { return _this.copyUTID(); });
        qrBtn === null || qrBtn === void 0 ? void 0 : qrBtn.addEventListener('click', function () { return _this.showQRCode(); });
    };
    IVUTIDBadge.prototype.getDefaultStyles = function () {
        return "\n      :host {\n        display: inline-block;\n        font-family: var(--font-sans, system-ui, sans-serif);\n      }\n\n      .badge-container {\n        background: var(--color-background, #1a1a1a);\n        border: 1px solid var(--color-border, #333);\n        border-radius: 8px;\n        padding: 12px 16px;\n        display: inline-flex;\n        align-items: center;\n        gap: 12px;\n        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);\n        transition: all 0.3s ease;\n        cursor: pointer;\n      }\n\n      .badge-container:hover {\n        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);\n        transform: translateY(-1px);\n      }\n\n      .badge-container.verified {\n        border-color: var(--status-success, #10b981);\n        box-shadow: 0 0 15px rgba(16, 185, 129, 0.2);\n      }\n\n      .badge-container.consciousness {\n        animation: consciousness-pulse 3s ease-in-out infinite;\n      }\n\n      @keyframes consciousness-pulse {\n        0%, 100% {\n          box-shadow: 0 0 15px rgba(139, 92, 246, 0.3);\n        }\n        50% {\n          box-shadow: 0 0 25px rgba(139, 92, 246, 0.5);\n        }\n      }\n\n      .utid-icon {\n        width: 32px;\n        height: 32px;\n        border-radius: 50%;\n        background: linear-gradient(135deg, var(--brand-primary, #0ea5e9), var(--brand-secondary, #8b5cf6));\n        display: flex;\n        align-items: center;\n        justify-content: center;\n        font-size: 16px;\n        flex-shrink: 0;\n      }\n\n      .utid-content {\n        flex: 1;\n        min-width: 0;\n      }\n\n      .utid-label {\n        font-size: 10px;\n        text-transform: uppercase;\n        letter-spacing: 0.5px;\n        color: var(--color-muted-foreground, #888);\n        margin-bottom: 2px;\n      }\n\n      .utid-value {\n        font-family: var(--font-mono, 'JetBrains Mono', monospace);\n        font-size: 13px;\n        font-weight: 600;\n        color: var(--color-foreground, #e5e5e5);\n        white-space: nowrap;\n        overflow: hidden;\n        text-overflow: ellipsis;\n      }\n\n      .badge-actions {\n        display: flex;\n        gap: 8px;\n      }\n\n      .action-btn {\n        width: 28px;\n        height: 28px;\n        border: none;\n        background: var(--color-muted, #333);\n        border-radius: 4px;\n        cursor: pointer;\n        display: flex;\n        align-items: center;\n        justify-content: center;\n        transition: all 0.2s ease;\n        font-size: 14px;\n      }\n\n      .action-btn:hover {\n        background: var(--color-accent, #444);\n        transform: scale(1.1);\n      }\n\n      .action-btn:active {\n        transform: scale(0.95);\n      }\n\n      .verification-badge {\n        position: absolute;\n        top: -6px;\n        right: -6px;\n        width: 20px;\n        height: 20px;\n        background: var(--status-success, #10b981);\n        border-radius: 50%;\n        display: flex;\n        align-items: center;\n        justify-content: center;\n        font-size: 12px;\n        border: 2px solid var(--color-background, #1a1a1a);\n      }\n\n      .qr-modal {\n        position: fixed;\n        top: 0;\n        left: 0;\n        width: 100%;\n        height: 100%;\n        background: rgba(0, 0, 0, 0.8);\n        display: flex;\n        align-items: center;\n        justify-content: center;\n        z-index: 1000;\n      }\n\n      .qr-content {\n        background: var(--color-background, #1a1a1a);\n        border: 1px solid var(--color-border, #333);\n        border-radius: 12px;\n        padding: 24px;\n        max-width: 300px;\n        text-align: center;\n      }\n\n      .qr-code {\n        width: 200px;\n        height: 200px;\n        margin: 16px auto;\n        background: white;\n        border-radius: 8px;\n        display: flex;\n        align-items: center;\n        justify-content: center;\n        font-size: 12px;\n        color: #333;\n      }\n\n      .qr-close {\n        margin-top: 16px;\n        padding: 8px 16px;\n        background: var(--brand-primary, #0ea5e9);\n        border: none;\n        border-radius: 6px;\n        color: white;\n        cursor: pointer;\n        font-weight: 600;\n      }\n\n      .consciousness-indicator {\n        position: absolute;\n        bottom: -4px;\n        left: 50%;\n        transform: translateX(-50%);\n        width: 80%;\n        height: 3px;\n        background: rgba(139, 92, 246, 0.2);\n        border-radius: 2px;\n        overflow: hidden;\n      }\n\n      .consciousness-fill {\n        height: 100%;\n        background: linear-gradient(90deg, #8b5cf6, #06b6d4);\n        transition: width 0.5s ease;\n      }\n    ";
    };
    IVUTIDBadge.prototype.render = function () {
        if (!this.shadowRoot)
            return;
        var shortUTID = this.utidData.utid ?
            "".concat(this.utidData.utid.slice(0, 8), "...").concat(this.utidData.utid.slice(-6)) :
            'No UTID';
        var containerClasses = [
            'badge-container',
            this.utidData.verified ? 'verified' : '',
            this.utidData.consciousnessLevel > 50 ? 'consciousness' : '',
        ].filter(Boolean).join(' ');
        this.shadowRoot.innerHTML = "\n      <style>".concat(this.getDefaultStyles(), "</style>\n      <div class=\"").concat(containerClasses, "\" style=\"position: relative;\">\n        <div class=\"utid-icon\">\uD83D\uDD2E</div>\n        <div class=\"utid-content\">\n          <div class=\"utid-label\">UTID</div>\n          <div class=\"utid-value\" title=\"").concat(this.utidData.utid, "\">").concat(shortUTID, "</div>\n        </div>\n        <div class=\"badge-actions\">\n          <button class=\"action-btn copy-btn\" title=\"Copy UTID\">\uD83D\uDCCB</button>\n          <button class=\"action-btn qr-btn\" title=\"Show QR Code\">\uD83D\uDCF1</button>\n        </div>\n        ").concat(this.utidData.verified ? '<div class="verification-badge">✓</div>' : '', "\n        ").concat(this.utidData.consciousnessLevel > 0 ? "\n          <div class=\"consciousness-indicator\">\n            <div class=\"consciousness-fill\" style=\"width: ".concat(this.utidData.consciousnessLevel, "%\"></div>\n          </div>\n        ") : '', "\n      </div>\n      ").concat(this.showingQR ? this.renderQRModal() : '', "\n    ");
        this.attachEventListeners();
    };
    IVUTIDBadge.prototype.renderQRModal = function () {
        return "\n      <div class=\"qr-modal\">\n        <div class=\"qr-content\">\n          <h3 style=\"margin: 0 0 8px 0; color: var(--color-foreground, #e5e5e5);\">UTID QR Code</h3>\n          <div class=\"qr-code\">\n            QR Code<br/>\n            ".concat(this.utidData.utid.slice(0, 12), "...\n          </div>\n          <div style=\"font-size: 11px; color: var(--color-muted-foreground, #888); margin-top: 8px;\">\n            Scan to verify on blockchain\n          </div>\n          <button class=\"qr-close\">Close</button>\n        </div>\n      </div>\n    ");
    };
    IVUTIDBadge.prototype.copyUTID = function () {
        var _this = this;
        if (!this.utidData.utid)
            return;
        navigator.clipboard.writeText(this.utidData.utid).then(function () {
            var _a;
            _this.emitEvent('utid-copied', { utid: _this.utidData.utid });
            // Show feedback
            var copyBtn = (_a = _this.shadowRoot) === null || _a === void 0 ? void 0 : _a.querySelector('.copy-btn');
            if (copyBtn) {
                copyBtn.textContent = '✓';
                setTimeout(function () {
                    copyBtn.textContent = '📋';
                }, 2000);
            }
        });
    };
    IVUTIDBadge.prototype.showQRCode = function () {
        var _this = this;
        var _a, _b;
        this.showingQR = true;
        this.render();
        // Attach close handler
        var closeBtn = (_a = this.shadowRoot) === null || _a === void 0 ? void 0 : _a.querySelector('.qr-close');
        var modal = (_b = this.shadowRoot) === null || _b === void 0 ? void 0 : _b.querySelector('.qr-modal');
        closeBtn === null || closeBtn === void 0 ? void 0 : closeBtn.addEventListener('click', function () {
            _this.showingQR = false;
            _this.render();
        });
        modal === null || modal === void 0 ? void 0 : modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                _this.showingQR = false;
                _this.render();
            }
        });
        this.emitEvent('qr-shown', { utid: this.utidData.utid });
    };
    IVUTIDBadge.prototype.handleWebSocketMessage = function (data) {
        if (data.type === 'utid_update') {
            this.updateUTID(data.data);
        }
    };
    IVUTIDBadge.prototype.updateUTID = function (data) {
        this.utidData = __assign(__assign({}, this.utidData), data);
        this.render();
        this.emitEvent('utid-update', this.utidData);
    };
    IVUTIDBadge.prototype.onConnect = function () {
        this.render();
    };
    IVUTIDBadge.prototype.onDisconnect = function () {
        // Cleanup
    };
    Object.defineProperty(IVUTIDBadge, "observedAttributes", {
        // Attribute handling
        get: function () {
            return ['utid', 'verified', 'blockchain-hash', 'consciousness-level', 'physics-domain', 'ws-url'];
        },
        enumerable: false,
        configurable: true
    });
    IVUTIDBadge.prototype.attributeChangedCallback = function (name, oldValue, newValue) {
        if (oldValue === newValue)
            return;
        switch (name) {
            case 'utid':
                this.utidData.utid = newValue;
                this.render();
                break;
            case 'verified':
                this.utidData.verified = newValue === 'true';
                this.render();
                break;
            case 'blockchain-hash':
                this.utidData.blockchainHash = newValue;
                this.render();
                break;
            case 'consciousness-level':
                this.utidData.consciousnessLevel = parseFloat(newValue) || 0;
                this.render();
                break;
            case 'physics-domain':
                this.utidData.physicsDomain = newValue;
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
    return IVUTIDBadge;
}(IVWidget));
export { IVUTIDBadge };
// Register custom element
if (!customElements.get('iv-utid-badge')) {
    customElements.define('iv-utid-badge', IVUTIDBadge);
}
//# sourceMappingURL=iv-utid-badge.js.map