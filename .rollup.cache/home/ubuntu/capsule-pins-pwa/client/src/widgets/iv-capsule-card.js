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
import { __extends } from "tslib";
import { IVWidget } from './base/IVWidget';
var IVCapsuleCard = /** @class */ (function (_super) {
    __extends(IVCapsuleCard, _super);
    function IVCapsuleCard() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this.capsuleId = '';
        _this.capsuleTitle = '';
        _this.capsuleStatus = 'active';
        _this.capsulePriority = 'P1';
        _this.capsuleSource = '';
        _this.capsuleDescription = '';
        return _this;
    }
    Object.defineProperty(IVCapsuleCard, "observedAttributes", {
        get: function () {
            return ['capsule-id', 'title', 'status', 'priority', 'source', 'description'];
        },
        enumerable: false,
        configurable: true
    });
    IVCapsuleCard.prototype.handleAttributeChange = function (name, oldValue, newValue) {
        switch (name) {
            case 'capsule-id':
                this.capsuleId = newValue || '';
                break;
            case 'title':
                this.capsuleTitle = newValue || '';
                break;
            case 'status':
                this.capsuleStatus = newValue || 'active';
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
    };
    IVCapsuleCard.prototype.shouldRerender = function (attributeName) {
        return true; // Re-render on any attribute change
    };
    IVCapsuleCard.prototype.render = function () {
        this.shadow.innerHTML = '';
        this.applyStyles(this.getStyles());
        var card = document.createElement('div');
        card.className = "capsule-card status-".concat(this.capsuleStatus);
        card.id = 'card';
        // Status indicator
        var statusIndicator = document.createElement('div');
        statusIndicator.className = 'status-indicator';
        // Header
        var header = document.createElement('div');
        header.className = 'card-header';
        var titleEl = document.createElement('div');
        titleEl.className = 'card-title';
        titleEl.textContent = this.capsuleTitle || 'Untitled Capsule';
        var priorityBadge = document.createElement('span');
        priorityBadge.className = "priority-badge priority-".concat(this.capsulePriority.toLowerCase());
        priorityBadge.textContent = this.capsulePriority;
        header.appendChild(titleEl);
        header.appendChild(priorityBadge);
        // Body
        var body = document.createElement('div');
        body.className = 'card-body';
        var sourceEl = document.createElement('div');
        sourceEl.className = 'card-source';
        sourceEl.innerHTML = "<span class=\"source-label\">Source:</span> <span class=\"source-value\">".concat(this.capsuleSource || 'Unknown', "</span>");
        if (this.capsuleDescription) {
            var descEl = document.createElement('div');
            descEl.className = 'card-description';
            descEl.textContent = this.capsuleDescription;
            body.appendChild(descEl);
        }
        body.appendChild(sourceEl);
        // Footer
        var footer = document.createElement('div');
        footer.className = 'card-footer';
        var statusBadge = document.createElement('span');
        statusBadge.className = "status-badge status-".concat(this.capsuleStatus);
        statusBadge.textContent = this.formatStatus(this.capsuleStatus);
        var viewButton = document.createElement('button');
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
    };
    IVCapsuleCard.prototype.attachEventListeners = function () {
        var _this = this;
        var viewButton = this.shadow.getElementById('view-button');
        if (viewButton) {
            viewButton.addEventListener('click', function () {
                _this.handleViewClick();
            });
        }
        var card = this.shadow.getElementById('card');
        if (card) {
            card.addEventListener('click', function (e) {
                // Don't trigger if clicking the button
                if (e.target.id !== 'view-button') {
                    _this.handleCardClick();
                }
            });
        }
    };
    IVCapsuleCard.prototype.handleViewClick = function () {
        this.emitEvent('view-capsule', {
            capsuleId: this.capsuleId,
            title: this.capsuleTitle,
            status: this.capsuleStatus,
        });
    };
    IVCapsuleCard.prototype.handleCardClick = function () {
        this.emitEvent('capsule-click', {
            capsuleId: this.capsuleId,
        });
    };
    IVCapsuleCard.prototype.formatStatus = function (status) {
        var map = {
            active: 'Active',
            warning: 'Warning',
            critical: 'Critical',
            resolved: 'Resolved',
        };
        return map[status] || status;
    };
    IVCapsuleCard.prototype.getStyles = function () {
        var statusColors = {
            active: this.theme.statusInfo,
            warning: this.theme.statusWarning,
            critical: this.theme.statusError,
            resolved: this.theme.statusSuccess,
        };
        return "\n      :host {\n        display: block;\n        width: 100%;\n        max-width: 400px;\n      }\n\n      .capsule-card {\n        background: ".concat(this.theme.bgSecondary, ";\n        border: 1px solid ").concat(this.theme.borderDefault, ";\n        border-radius: ").concat(this.theme.radiusMd, ";\n        overflow: hidden;\n        box-shadow: ").concat(this.theme.shadowMd, ";\n        transition: all ").concat(this.theme.durationNormal, " ").concat(this.theme.easingDefault, ";\n        cursor: pointer;\n        position: relative;\n      }\n\n      .capsule-card:hover {\n        transform: translateY(-2px);\n        box-shadow: ").concat(this.theme.shadowLg, ";\n        border-color: ").concat(statusColors[this.capsuleStatus], ";\n      }\n\n      .status-indicator {\n        position: absolute;\n        top: 0;\n        left: 0;\n        width: 4px;\n        height: 100%;\n        background: ").concat(statusColors[this.capsuleStatus], ";\n      }\n\n      .status-indicator::before {\n        content: '';\n        position: absolute;\n        top: 0;\n        left: 0;\n        width: 100%;\n        height: 100%;\n        background: ").concat(statusColors[this.capsuleStatus], ";\n        opacity: 0.5;\n        animation: pulse 2s ease-in-out infinite;\n      }\n\n      .card-header {\n        display: flex;\n        justify-content: space-between;\n        align-items: flex-start;\n        gap: 0.75rem;\n        padding: 1rem 1rem 0.5rem 1.5rem;\n      }\n\n      .card-title {\n        font-family: ").concat(this.theme.fontHeading, ";\n        font-size: 1rem;\n        font-weight: 600;\n        color: ").concat(this.theme.fgPrimary, ";\n        flex: 1;\n        line-height: 1.4;\n      }\n\n      .priority-badge {\n        font-family: ").concat(this.theme.fontMono, ";\n        font-size: 0.75rem;\n        font-weight: 600;\n        padding: 0.25rem 0.5rem;\n        border-radius: 9999px;\n        white-space: nowrap;\n      }\n\n      .priority-badge.priority-p5 {\n        background: ").concat(this.theme.statusError, ";\n        color: white;\n      }\n\n      .priority-badge.priority-p4 {\n        background: ").concat(this.theme.statusWarning, ";\n        color: ").concat(this.theme.bgPrimary, ";\n      }\n\n      .priority-badge.priority-p3 {\n        background: ").concat(this.theme.statusInfo, ";\n        color: white;\n      }\n\n      .priority-badge.priority-p2,\n      .priority-badge.priority-p1 {\n        background: ").concat(this.theme.borderDefault, ";\n        color: ").concat(this.theme.fgPrimary, ";\n      }\n\n      .card-body {\n        padding: 0.5rem 1rem 0.5rem 1.5rem;\n      }\n\n      .card-description {\n        font-family: ").concat(this.theme.fontBody, ";\n        font-size: 0.875rem;\n        color: ").concat(this.theme.fgSecondary, ";\n        line-height: 1.5;\n        margin-bottom: 0.75rem;\n      }\n\n      .card-source {\n        font-family: ").concat(this.theme.fontBody, ";\n        font-size: 0.75rem;\n        color: ").concat(this.theme.fgSecondary, ";\n      }\n\n      .source-label {\n        font-weight: 600;\n        color: ").concat(this.theme.fgPrimary, ";\n      }\n\n      .source-value {\n        font-family: ").concat(this.theme.fontMono, ";\n        color: ").concat(this.theme.brandPrimary, ";\n      }\n\n      .card-footer {\n        display: flex;\n        justify-content: space-between;\n        align-items: center;\n        padding: 0.75rem 1rem 0.75rem 1.5rem;\n        background: ").concat(this.theme.bgPrimary, ";\n        border-top: 1px solid ").concat(this.theme.borderDefault, ";\n      }\n\n      .status-badge {\n        font-family: ").concat(this.theme.fontBody, ";\n        font-size: 0.75rem;\n        font-weight: 600;\n        padding: 0.25rem 0.75rem;\n        border-radius: 9999px;\n        text-transform: uppercase;\n        letter-spacing: 0.05em;\n      }\n\n      .status-badge.status-active {\n        background: ").concat(this.theme.amiContextGlow, ";\n        color: ").concat(this.theme.statusInfo, ";\n      }\n\n      .status-badge.status-warning {\n        background: ").concat(this.theme.amiAdaptationFade, ";\n        color: ").concat(this.theme.statusWarning, ";\n      }\n\n      .status-badge.status-critical {\n        background: rgba(239, 68, 68, 0.2);\n        color: ").concat(this.theme.statusError, ";\n      }\n\n      .status-badge.status-resolved {\n        background: rgba(16, 185, 129, 0.2);\n        color: ").concat(this.theme.statusSuccess, ";\n      }\n\n      .view-button {\n        font-family: ").concat(this.theme.fontBody, ";\n        font-size: 0.75rem;\n        font-weight: 600;\n        padding: 0.375rem 0.75rem;\n        background: ").concat(this.theme.brandPrimary, ";\n        color: white;\n        border: none;\n        border-radius: ").concat(this.theme.radiusMd, ";\n        cursor: pointer;\n        transition: all ").concat(this.theme.durationNormal, " ").concat(this.theme.easingDefault, ";\n      }\n\n      .view-button:hover {\n        background: ").concat(this.theme.brandSecondary, ";\n        transform: translateY(-1px);\n      }\n\n      .view-button:active {\n        transform: translateY(0);\n      }\n\n      @keyframes pulse {\n        0%, 100% {\n          opacity: 0.5;\n        }\n        50% {\n          opacity: 1;\n        }\n      }\n    ");
    };
    return IVCapsuleCard;
}(IVWidget));
export { IVCapsuleCard };
// Register custom element
if (!customElements.get('iv-capsule-card')) {
    customElements.define('iv-capsule-card', IVCapsuleCard);
}
//# sourceMappingURL=iv-capsule-card.js.map