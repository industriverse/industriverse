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
import { __extends } from "tslib";
import { IVWidget } from './base/IVWidget';
var IVWalletOrb = /** @class */ (function (_super) {
    __extends(IVWalletOrb, _super);
    function IVWalletOrb() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this.balance = 0;
        _this.currency = 'USD';
        _this.isAnimating = false;
        return _this;
    }
    Object.defineProperty(IVWalletOrb, "observedAttributes", {
        get: function () {
            return ['balance', 'currency'];
        },
        enumerable: false,
        configurable: true
    });
    IVWalletOrb.prototype.handleAttributeChange = function (name, oldValue, newValue) {
        if (name === 'balance') {
            var newBalance = parseFloat(newValue) || 0;
            if (newBalance !== this.balance) {
                this.animateBalanceChange(this.balance, newBalance);
                this.balance = newBalance;
            }
        }
        else if (name === 'currency') {
            this.currency = newValue || 'USD';
        }
    };
    IVWalletOrb.prototype.shouldRerender = function (attributeName) {
        return attributeName === 'currency';
    };
    IVWalletOrb.prototype.render = function () {
        // Clear shadow DOM
        this.shadow.innerHTML = '';
        // Apply styles
        this.applyStyles(this.getStyles());
        // Create structure
        var container = document.createElement('div');
        container.className = 'wallet-orb-container';
        var orb = document.createElement('div');
        orb.className = 'orb';
        orb.id = 'orb';
        var balanceEl = document.createElement('div');
        balanceEl.className = 'balance';
        balanceEl.id = 'balance';
        balanceEl.textContent = this.formatBalance(this.balance);
        var currencyEl = document.createElement('div');
        currencyEl.className = 'currency';
        currencyEl.textContent = this.currency;
        orb.appendChild(balanceEl);
        orb.appendChild(currencyEl);
        container.appendChild(orb);
        this.shadow.appendChild(container);
    };
    IVWalletOrb.prototype.attachEventListeners = function () {
        var _this = this;
        // Click to pulse animation
        var orb = this.shadow.getElementById('orb');
        if (orb) {
            orb.addEventListener('click', function () {
                _this.pulseAnimation();
            });
        }
    };
    IVWalletOrb.prototype.onWebSocketMessage = function (event) {
        try {
            var data = JSON.parse(event.data);
            if (data.type === 'balance_update' && data.userId === this.config.userId) {
                this.updateBalance(data.balance);
            }
        }
        catch (error) {
            console.error('Failed to parse WebSocket message:', error);
        }
    };
    IVWalletOrb.prototype.updateBalance = function (newBalance) {
        this.setAttribute('balance', newBalance.toString());
    };
    IVWalletOrb.prototype.formatBalance = function (balance) {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }).format(balance);
    };
    IVWalletOrb.prototype.animateBalanceChange = function (oldBalance, newBalance) {
        var _this = this;
        if (this.isAnimating)
            return;
        this.isAnimating = true;
        var balanceEl = this.shadow.getElementById('balance');
        var orb = this.shadow.getElementById('orb');
        if (!balanceEl || !orb)
            return;
        var duration = 1000; // 1 second
        var startTime = Date.now();
        var diff = newBalance - oldBalance;
        var animate = function () {
            var elapsed = Date.now() - startTime;
            var progress = Math.min(elapsed / duration, 1);
            // Ease out cubic
            var eased = 1 - Math.pow(1 - progress, 3);
            var currentBalance = oldBalance + (diff * eased);
            balanceEl.textContent = _this.formatBalance(currentBalance);
            // Add glow effect based on change direction
            if (diff > 0) {
                orb.style.boxShadow = "0 0 ".concat(20 + (progress * 30), "px ").concat(_this.theme.statusSuccess);
            }
            else if (diff < 0) {
                orb.style.boxShadow = "0 0 ".concat(20 + (progress * 30), "px ").concat(_this.theme.statusError);
            }
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
            else {
                _this.isAnimating = false;
                // Reset to default glow
                setTimeout(function () {
                    orb.style.boxShadow = "0 0 30px ".concat(_this.theme.amiContextGlow);
                }, 500);
            }
        };
        requestAnimationFrame(animate);
    };
    IVWalletOrb.prototype.pulseAnimation = function () {
        var orb = this.shadow.getElementById('orb');
        if (!orb)
            return;
        orb.style.animation = 'none';
        setTimeout(function () {
            orb.style.animation = 'pulse 0.5s ease-out';
        }, 10);
    };
    IVWalletOrb.prototype.getStyles = function () {
        return "\n      :host {\n        display: inline-block;\n        --orb-size: 120px;\n      }\n\n      .wallet-orb-container {\n        display: flex;\n        align-items: center;\n        justify-content: center;\n        padding: 1rem;\n      }\n\n      .orb {\n        width: var(--orb-size);\n        height: var(--orb-size);\n        border-radius: 50%;\n        background: linear-gradient(135deg, ".concat(this.theme.brandPrimary, ", ").concat(this.theme.brandSecondary, ");\n        display: flex;\n        flex-direction: column;\n        align-items: center;\n        justify-content: center;\n        cursor: pointer;\n        transition: transform ").concat(this.theme.durationNormal, " ").concat(this.theme.easingDefault, ";\n        box-shadow: 0 0 30px ").concat(this.theme.amiContextGlow, ";\n        position: relative;\n        overflow: hidden;\n      }\n\n      .orb::before {\n        content: '';\n        position: absolute;\n        top: -50%;\n        left: -50%;\n        width: 200%;\n        height: 200%;\n        background: radial-gradient(circle, ").concat(this.theme.amiPredictionPulse, " 0%, transparent 70%);\n        animation: rotate 10s linear infinite;\n      }\n\n      .orb:hover {\n        transform: scale(1.05);\n      }\n\n      .orb:active {\n        transform: scale(0.95);\n      }\n\n      .balance {\n        font-family: ").concat(this.theme.fontMono, ";\n        font-size: 1.25rem;\n        font-weight: 700;\n        color: ").concat(this.theme.fgPrimary, ";\n        z-index: 1;\n        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);\n      }\n\n      .currency {\n        font-family: ").concat(this.theme.fontBody, ";\n        font-size: 0.75rem;\n        font-weight: 500;\n        color: ").concat(this.theme.fgSecondary, ";\n        z-index: 1;\n        text-transform: uppercase;\n        letter-spacing: 0.1em;\n        margin-top: 0.25rem;\n      }\n\n      @keyframes rotate {\n        from {\n          transform: rotate(0deg);\n        }\n        to {\n          transform: rotate(360deg);\n        }\n      }\n\n      @keyframes pulse {\n        0%, 100% {\n          transform: scale(1);\n        }\n        50% {\n          transform: scale(1.1);\n        }\n      }\n    ");
    };
    return IVWalletOrb;
}(IVWidget));
export { IVWalletOrb };
// Register custom element
if (!customElements.get('iv-wallet-orb')) {
    customElements.define('iv-wallet-orb', IVWalletOrb);
}
//# sourceMappingURL=iv-wallet-orb.js.map