import { __assign, __extends } from "tslib";
import { IVWidget } from './base/IVWidget';
var IVShadowTwin = /** @class */ (function (_super) {
    __extends(IVShadowTwin, _super);
    function IVShadowTwin() {
        var _this = _super.call(this) || this;
        _this.twinData = {
            twinId: '',
            syncStatus: 'offline',
            lastSync: 0,
            driftPercentage: 0,
            energyConsumption: 0,
            calibrationNeeded: false,
        };
        return _this;
    }
    IVShadowTwin.prototype.attachEventListeners = function () {
        var _this = this;
        var _a;
        var syncBtn = (_a = this.shadowRoot) === null || _a === void 0 ? void 0 : _a.querySelector('.sync-btn');
        syncBtn === null || syncBtn === void 0 ? void 0 : syncBtn.addEventListener('click', function () { return _this.forceSync(); });
    };
    IVShadowTwin.prototype.getDefaultStyles = function () {
        return ':host { display: block; font-family: system-ui, sans-serif; }';
    };
    IVShadowTwin.prototype.render = function () {
        if (!this.shadowRoot)
            return;
        var styles = this.getDefaultStyles();
        var twinId = this.twinData.twinId || 'Unknown';
        this.shadowRoot.innerHTML = '<style>' + styles + '</style><div>Shadow Twin: ' + twinId + '</div><button class="sync-btn">Sync</button>';
        this.attachEventListeners();
    };
    IVShadowTwin.prototype.forceSync = function () {
        this.emitEvent('sync-requested', { twinId: this.twinData.twinId });
    };
    IVShadowTwin.prototype.handleWebSocketMessage = function (data) {
        if (data.type === 'twin_update') {
            this.twinData = __assign(__assign({}, this.twinData), data.data);
            this.render();
        }
    };
    IVShadowTwin.prototype.onConnect = function () {
        this.render();
    };
    IVShadowTwin.prototype.onDisconnect = function () { };
    Object.defineProperty(IVShadowTwin, "observedAttributes", {
        get: function () {
            return ['twin-id', 'sync-status', 'ws-url'];
        },
        enumerable: false,
        configurable: true
    });
    IVShadowTwin.prototype.attributeChangedCallback = function (name, oldValue, newValue) {
        if (oldValue === newValue)
            return;
        if (name === 'twin-id') {
            this.twinData.twinId = newValue;
            this.render();
        }
    };
    return IVShadowTwin;
}(IVWidget));
export { IVShadowTwin };
if (!customElements.get('iv-shadow-twin')) {
    customElements.define('iv-shadow-twin', IVShadowTwin);
}
//# sourceMappingURL=iv-shadow-twin.js.map