/**
 * <iv-energy-gauge> Widget
 * Week 8: White-Label Platform
 *
 * Real-time energy consumption gauge with threshold indicators
 * Features:
 * - Circular gauge with animated needle
 * - Color-coded zones (green/yellow/red)
 * - Current/peak/average values
 * - WebSocket updates
 * - AmI glow effects
 */
import { __assign, __extends } from "tslib";
import { IVWidget } from './base/IVWidget';
var IVEnergyGauge = /** @class */ (function (_super) {
    __extends(IVEnergyGauge, _super);
    function IVEnergyGauge() {
        var _this = _super.call(this) || this;
        _this.energyData = {
            current: 0,
            peak: 0,
            average: 0,
            unit: 'kW',
            timestamp: Date.now(),
            threshold_warning: 75,
            threshold_critical: 90,
        };
        _this.canvas = null;
        _this.ctx = null;
        _this.animationFrame = null;
        _this.targetValue = 0;
        _this.currentValue = 0;
        _this.setupCanvas();
        return _this;
    }
    IVEnergyGauge.prototype.attachEventListeners = function () {
        // No DOM event listeners needed for gauge
    };
    IVEnergyGauge.prototype.setupCanvas = function () {
        this.canvas = document.createElement('canvas');
        this.canvas.width = 300;
        this.canvas.height = 300;
        this.ctx = this.canvas.getContext('2d');
    };
    IVEnergyGauge.prototype.getDefaultStyles = function () {
        return "\n      :host {\n        display: block;\n        width: 300px;\n        height: 400px;\n        font-family: var(--font-sans, system-ui, sans-serif);\n      }\n\n      .gauge-container {\n        background: var(--color-background, #1a1a1a);\n        border: 1px solid var(--color-border, #333);\n        border-radius: 12px;\n        padding: 20px;\n        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);\n        transition: all 0.3s ease;\n      }\n\n      .gauge-container:hover {\n        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.4);\n      }\n\n      .gauge-title {\n        font-size: 14px;\n        font-weight: 600;\n        color: var(--color-foreground, #e5e5e5);\n        margin-bottom: 16px;\n        text-align: center;\n      }\n\n      .gauge-canvas {\n        display: block;\n        margin: 0 auto;\n      }\n\n      .gauge-stats {\n        display: grid;\n        grid-template-columns: repeat(3, 1fr);\n        gap: 12px;\n        margin-top: 16px;\n      }\n\n      .stat {\n        text-align: center;\n      }\n\n      .stat-label {\n        font-size: 11px;\n        color: var(--color-muted-foreground, #888);\n        text-transform: uppercase;\n        letter-spacing: 0.5px;\n      }\n\n      .stat-value {\n        font-size: 18px;\n        font-weight: 700;\n        color: var(--color-foreground, #e5e5e5);\n        margin-top: 4px;\n      }\n\n      .stat-unit {\n        font-size: 12px;\n        color: var(--color-muted-foreground, #888);\n        margin-left: 2px;\n      }\n\n      /* AmI glow effects */\n      .gauge-container.warning {\n        box-shadow: 0 0 20px rgba(251, 191, 36, 0.3);\n      }\n\n      .gauge-container.critical {\n        box-shadow: 0 0 20px rgba(239, 68, 68, 0.3);\n        animation: pulse-critical 2s ease-in-out infinite;\n      }\n\n      @keyframes pulse-critical {\n        0%, 100% {\n          box-shadow: 0 0 20px rgba(239, 68, 68, 0.3);\n        }\n        50% {\n          box-shadow: 0 0 30px rgba(239, 68, 68, 0.5);\n        }\n      }\n    ";
    };
    IVEnergyGauge.prototype.render = function () {
        if (!this.shadowRoot)
            return;
        var percentage = (this.energyData.current / this.energyData.peak) * 100;
        var statusClass = '';
        if (percentage >= this.energyData.threshold_critical) {
            statusClass = 'critical';
        }
        else if (percentage >= this.energyData.threshold_warning) {
            statusClass = 'warning';
        }
        this.shadowRoot.innerHTML = "\n      <style>".concat(this.getDefaultStyles(), "</style>\n      <div class=\"gauge-container ").concat(statusClass, "\">\n        <div class=\"gauge-title\">Energy Consumption</div>\n        <canvas class=\"gauge-canvas\" width=\"300\" height=\"300\"></canvas>\n        <div class=\"gauge-stats\">\n          <div class=\"stat\">\n            <div class=\"stat-label\">Current</div>\n            <div class=\"stat-value\">\n              ").concat(this.energyData.current.toFixed(1), "\n              <span class=\"stat-unit\">").concat(this.energyData.unit, "</span>\n            </div>\n          </div>\n          <div class=\"stat\">\n            <div class=\"stat-label\">Peak</div>\n            <div class=\"stat-value\">\n              ").concat(this.energyData.peak.toFixed(1), "\n              <span class=\"stat-unit\">").concat(this.energyData.unit, "</span>\n            </div>\n          </div>\n          <div class=\"stat\">\n            <div class=\"stat-label\">Average</div>\n            <div class=\"stat-value\">\n              ").concat(this.energyData.average.toFixed(1), "\n              <span class=\"stat-unit\">").concat(this.energyData.unit, "</span>\n            </div>\n          </div>\n        </div>\n      </div>\n    ");
        // Get canvas from shadow DOM
        this.canvas = this.shadowRoot.querySelector('.gauge-canvas');
        if (this.canvas) {
            this.ctx = this.canvas.getContext('2d');
            this.drawGauge();
        }
    };
    IVEnergyGauge.prototype.drawGauge = function () {
        var _this = this;
        if (!this.ctx || !this.canvas)
            return;
        var width = this.canvas.width;
        var height = this.canvas.height;
        var centerX = width / 2;
        var centerY = height / 2;
        var radius = Math.min(width, height) / 2 - 40;
        // Clear canvas
        this.ctx.clearRect(0, 0, width, height);
        // Animate current value towards target
        var diff = this.targetValue - this.currentValue;
        if (Math.abs(diff) > 0.1) {
            this.currentValue += diff * 0.1;
            this.animationFrame = requestAnimationFrame(function () { return _this.drawGauge(); });
        }
        else {
            this.currentValue = this.targetValue;
        }
        // Draw gauge background
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, radius, 0.75 * Math.PI, 2.25 * Math.PI);
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        this.ctx.lineWidth = 20;
        this.ctx.stroke();
        // Draw colored zones
        var warningAngle = 0.75 * Math.PI + (this.energyData.threshold_warning / 100) * 1.5 * Math.PI;
        var criticalAngle = 0.75 * Math.PI + (this.energyData.threshold_critical / 100) * 1.5 * Math.PI;
        // Green zone (0 - warning)
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, radius, 0.75 * Math.PI, warningAngle);
        this.ctx.strokeStyle = 'rgba(34, 197, 94, 0.3)';
        this.ctx.lineWidth = 20;
        this.ctx.stroke();
        // Yellow zone (warning - critical)
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, radius, warningAngle, criticalAngle);
        this.ctx.strokeStyle = 'rgba(251, 191, 36, 0.3)';
        this.ctx.lineWidth = 20;
        this.ctx.stroke();
        // Red zone (critical - max)
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, radius, criticalAngle, 2.25 * Math.PI);
        this.ctx.strokeStyle = 'rgba(239, 68, 68, 0.3)';
        this.ctx.lineWidth = 20;
        this.ctx.stroke();
        // Draw current value arc
        var percentage = this.currentValue / 100;
        var endAngle = 0.75 * Math.PI + percentage * 1.5 * Math.PI;
        var arcColor = '#22c55e'; // green
        if (percentage >= this.energyData.threshold_critical / 100) {
            arcColor = '#ef4444'; // red
        }
        else if (percentage >= this.energyData.threshold_warning / 100) {
            arcColor = '#fbbf24'; // yellow
        }
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, radius, 0.75 * Math.PI, endAngle);
        this.ctx.strokeStyle = arcColor;
        this.ctx.lineWidth = 20;
        this.ctx.lineCap = 'round';
        this.ctx.stroke();
        // Draw needle
        var needleAngle = 0.75 * Math.PI + percentage * 1.5 * Math.PI;
        var needleLength = radius - 30;
        this.ctx.save();
        this.ctx.translate(centerX, centerY);
        this.ctx.rotate(needleAngle);
        // Needle shadow
        this.ctx.beginPath();
        this.ctx.moveTo(0, 0);
        this.ctx.lineTo(needleLength + 2, 2);
        this.ctx.strokeStyle = 'rgba(0, 0, 0, 0.3)';
        this.ctx.lineWidth = 3;
        this.ctx.stroke();
        // Needle
        this.ctx.beginPath();
        this.ctx.moveTo(0, 0);
        this.ctx.lineTo(needleLength, 0);
        this.ctx.strokeStyle = '#e5e5e5';
        this.ctx.lineWidth = 3;
        this.ctx.stroke();
        this.ctx.restore();
        // Draw center circle
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, 8, 0, 2 * Math.PI);
        this.ctx.fillStyle = '#e5e5e5';
        this.ctx.fill();
        // Draw percentage text
        this.ctx.font = 'bold 32px system-ui';
        this.ctx.fillStyle = '#e5e5e5';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText("".concat(Math.round(percentage * 100), "%"), centerX, centerY + 60);
    };
    IVEnergyGauge.prototype.handleWebSocketMessage = function (data) {
        if (data.type === 'energy_update') {
            this.updateEnergy(data.data);
        }
    };
    IVEnergyGauge.prototype.updateEnergy = function (data) {
        this.energyData = __assign(__assign({}, this.energyData), data);
        this.targetValue = (this.energyData.current / this.energyData.peak) * 100;
        this.render();
        this.emitEvent('energy-update', this.energyData);
    };
    IVEnergyGauge.prototype.onConnect = function () {
        this.render();
    };
    IVEnergyGauge.prototype.onDisconnect = function () {
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
    };
    Object.defineProperty(IVEnergyGauge, "observedAttributes", {
        // Attribute handling
        get: function () {
            return ['current', 'peak', 'average', 'unit', 'threshold-warning', 'threshold-critical', 'ws-url', 'auto-connect'];
        },
        enumerable: false,
        configurable: true
    });
    IVEnergyGauge.prototype.attributeChangedCallback = function (name, oldValue, newValue) {
        if (oldValue === newValue)
            return;
        switch (name) {
            case 'current':
                this.energyData.current = parseFloat(newValue) || 0;
                this.targetValue = (this.energyData.current / this.energyData.peak) * 100;
                this.render();
                break;
            case 'peak':
                this.energyData.peak = parseFloat(newValue) || 100;
                this.render();
                break;
            case 'average':
                this.energyData.average = parseFloat(newValue) || 0;
                this.render();
                break;
            case 'unit':
                this.energyData.unit = newValue;
                this.render();
                break;
            case 'threshold-warning':
                this.energyData.threshold_warning = parseFloat(newValue) || 75;
                this.render();
                break;
            case 'threshold-critical':
                this.energyData.threshold_critical = parseFloat(newValue) || 90;
                this.render();
                break;
            case 'ws-url':
                this.config.wsUrl = newValue;
                if (newValue) {
                    this.connectWebSocket();
                }
                break;
            case 'auto-connect':
                // Auto-connect handled by ws-url attribute
                break;
        }
    };
    return IVEnergyGauge;
}(IVWidget));
export { IVEnergyGauge };
// Register custom element
if (!customElements.get('iv-energy-gauge')) {
    customElements.define('iv-energy-gauge', IVEnergyGauge);
}
//# sourceMappingURL=iv-energy-gauge.js.map