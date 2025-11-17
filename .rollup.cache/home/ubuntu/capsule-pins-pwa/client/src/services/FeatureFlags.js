/**
 * Feature Flags Service
 * Week 8: White-Label Platform - Phase 4
 *
 * Per-tenant feature flag management for white-label deployments.
 * Enables/disables features at runtime without code changes.
 */
import { __assign } from "tslib";
/**
 * Default feature flags available across all deployments
 */
export var DEFAULT_FEATURE_FLAGS = [
    // Core Features
    {
        key: 'websocket_realtime',
        name: 'WebSocket Real-Time Updates',
        description: 'Enable real-time capsule updates via WebSocket',
        enabled: true,
        category: 'core',
    },
    {
        key: 'offline_mode',
        name: 'Offline Mode',
        description: 'Enable offline-first PWA capabilities',
        enabled: true,
        category: 'core',
    },
    {
        key: 'push_notifications',
        name: 'Push Notifications',
        description: 'Enable browser push notifications',
        enabled: true,
        category: 'core',
    },
    // Widget Features
    {
        key: 'widget_wallet_orb',
        name: 'Wallet Orb Widget',
        description: 'Enable wallet balance visualization widget',
        enabled: true,
        category: 'widget',
    },
    {
        key: 'widget_proof_ticker',
        name: 'Proof Ticker Widget',
        description: 'Enable proof generation feed widget',
        enabled: true,
        category: 'widget',
    },
    {
        key: 'widget_capsule_card',
        name: 'Capsule Card Widget',
        description: 'Enable capsule display widget',
        enabled: true,
        category: 'widget',
    },
    {
        key: 'widget_energy_gauge',
        name: 'Energy Gauge Widget',
        description: 'Enable energy visualization widget',
        enabled: true,
        category: 'widget',
    },
    {
        key: 'widget_utid_badge',
        name: 'UTID Badge Widget',
        description: 'Enable UTID display widget',
        enabled: true,
        category: 'widget',
    },
    {
        key: 'widget_ami_pulse',
        name: 'AmI Pulse Widget',
        description: 'Enable ambient intelligence activity widget',
        enabled: true,
        category: 'widget',
    },
    {
        key: 'widget_shadow_twin',
        name: 'Shadow Twin Widget',
        description: 'Enable digital twin sync widget',
        enabled: true,
        category: 'widget',
    },
    // AmI Features
    {
        key: 'ami_context_awareness',
        name: 'Context Awareness',
        description: 'Enable AmI context-aware intelligence',
        enabled: true,
        category: 'ami',
    },
    {
        key: 'ami_proactive',
        name: 'Proactive Intelligence',
        description: 'Enable AmI proactive predictions',
        enabled: true,
        category: 'ami',
    },
    {
        key: 'ami_seamless',
        name: 'Seamless Integration',
        description: 'Enable AmI seamless user experience',
        enabled: true,
        category: 'ami',
    },
    {
        key: 'ami_adaptive',
        name: 'Adaptive Learning',
        description: 'Enable AmI adaptive behavior',
        enabled: true,
        category: 'ami',
    },
    {
        key: 'cosmic_fabric',
        name: 'Cosmic Intelligence Fabric',
        description: 'Enable federated learning across deployments',
        enabled: true,
        category: 'ami',
    },
    // Integration Features
    {
        key: 'mcp_protocol',
        name: 'MCP Protocol',
        description: 'Enable Model Context Protocol integration',
        enabled: true,
        category: 'integration',
    },
    {
        key: 'a2a_protocol',
        name: 'A2A Protocol',
        description: 'Enable Agent-to-Agent communication',
        enabled: true,
        category: 'integration',
    },
    {
        key: 'thermal_computing',
        name: 'Thermal Computing',
        description: 'Enable JAX/Jasmin thermodynamic computing',
        enabled: true,
        category: 'integration',
    },
    {
        key: 'microadapt_edge',
        name: 'MicroAdaptEdge',
        description: 'Enable edge device optimization',
        enabled: true,
        category: 'integration',
    },
    // Experimental Features
    {
        key: 'experimental_voice_control',
        name: 'Voice Control',
        description: 'Enable voice commands for capsule management',
        enabled: false,
        category: 'experimental',
    },
    {
        key: 'experimental_ar_view',
        name: 'AR Visualization',
        description: 'Enable augmented reality capsule visualization',
        enabled: false,
        category: 'experimental',
    },
    {
        key: 'experimental_quantum_sim',
        name: 'Quantum Simulation',
        description: 'Enable quantum computing simulation for optimization',
        enabled: false,
        category: 'experimental',
    },
];
/**
 * Feature Flags Manager
 */
var FeatureFlagsManager = /** @class */ (function () {
    function FeatureFlagsManager() {
        this.flags = new Map();
        this.tenantId = null;
        this.listeners = new Set();
        this.loadFlags();
    }
    /**
     * Initialize feature flags for a specific tenant
     */
    FeatureFlagsManager.prototype.initialize = function (tenantId, config) {
        var _this = this;
        this.tenantId = tenantId;
        if (config) {
            // Load tenant-specific configuration
            Object.entries(config.flags).forEach(function (_a) {
                var key = _a[0], enabled = _a[1];
                _this.flags.set(key, enabled);
            });
        }
        else {
            // Load default flags
            DEFAULT_FEATURE_FLAGS.forEach(function (flag) {
                _this.flags.set(flag.key, flag.enabled);
            });
        }
        this.saveFlags();
        this.notifyListeners();
    };
    /**
     * Check if a feature is enabled
     */
    FeatureFlagsManager.prototype.isEnabled = function (flagKey) {
        var _a;
        return (_a = this.flags.get(flagKey)) !== null && _a !== void 0 ? _a : false;
    };
    /**
     * Enable a feature flag
     */
    FeatureFlagsManager.prototype.enable = function (flagKey) {
        this.flags.set(flagKey, true);
        this.saveFlags();
        this.notifyListeners();
    };
    /**
     * Disable a feature flag
     */
    FeatureFlagsManager.prototype.disable = function (flagKey) {
        this.flags.set(flagKey, false);
        this.saveFlags();
        this.notifyListeners();
    };
    /**
     * Toggle a feature flag
     */
    FeatureFlagsManager.prototype.toggle = function (flagKey) {
        var current = this.isEnabled(flagKey);
        this.flags.set(flagKey, !current);
        this.saveFlags();
        this.notifyListeners();
    };
    /**
     * Get all flags with their current state
     */
    FeatureFlagsManager.prototype.getAllFlags = function () {
        var _this = this;
        return DEFAULT_FEATURE_FLAGS.map(function (flag) {
            var _a;
            return (__assign(__assign({}, flag), { enabled: _this.isEnabled(flag.key), tenantId: (_a = _this.tenantId) !== null && _a !== void 0 ? _a : undefined }));
        });
    };
    /**
     * Get flags by category
     */
    FeatureFlagsManager.prototype.getFlagsByCategory = function (category) {
        return this.getAllFlags().filter(function (flag) { return flag.category === category; });
    };
    /**
     * Bulk update flags
     */
    FeatureFlagsManager.prototype.updateFlags = function (updates) {
        var _this = this;
        Object.entries(updates).forEach(function (_a) {
            var key = _a[0], enabled = _a[1];
            _this.flags.set(key, enabled);
        });
        this.saveFlags();
        this.notifyListeners();
    };
    /**
     * Reset all flags to defaults
     */
    FeatureFlagsManager.prototype.resetToDefaults = function () {
        var _this = this;
        this.flags.clear();
        DEFAULT_FEATURE_FLAGS.forEach(function (flag) {
            _this.flags.set(flag.key, flag.enabled);
        });
        this.saveFlags();
        this.notifyListeners();
    };
    /**
     * Export current configuration
     */
    FeatureFlagsManager.prototype.exportConfig = function () {
        var _a;
        var flagsObj = {};
        this.flags.forEach(function (enabled, key) {
            flagsObj[key] = enabled;
        });
        return {
            tenantId: (_a = this.tenantId) !== null && _a !== void 0 ? _a : 'default',
            tenantName: 'Default Tenant',
            flags: flagsObj,
        };
    };
    /**
     * Import configuration
     */
    FeatureFlagsManager.prototype.importConfig = function (config) {
        this.initialize(config.tenantId, config);
    };
    /**
     * Subscribe to flag changes
     */
    FeatureFlagsManager.prototype.subscribe = function (listener) {
        var _this = this;
        this.listeners.add(listener);
        return function () { return _this.listeners.delete(listener); };
    };
    /**
     * Load flags from localStorage
     */
    FeatureFlagsManager.prototype.loadFlags = function () {
        var _this = this;
        try {
            var stored = localStorage.getItem('feature_flags');
            if (stored) {
                var data = JSON.parse(stored);
                Object.entries(data).forEach(function (_a) {
                    var key = _a[0], enabled = _a[1];
                    _this.flags.set(key, enabled);
                });
            }
            else {
                // Initialize with defaults
                DEFAULT_FEATURE_FLAGS.forEach(function (flag) {
                    _this.flags.set(flag.key, flag.enabled);
                });
            }
        }
        catch (error) {
            console.error('Failed to load feature flags:', error);
        }
    };
    /**
     * Save flags to localStorage
     */
    FeatureFlagsManager.prototype.saveFlags = function () {
        try {
            var data_1 = {};
            this.flags.forEach(function (enabled, key) {
                data_1[key] = enabled;
            });
            localStorage.setItem('feature_flags', JSON.stringify(data_1));
        }
        catch (error) {
            console.error('Failed to save feature flags:', error);
        }
    };
    /**
     * Notify all listeners of flag changes
     */
    FeatureFlagsManager.prototype.notifyListeners = function () {
        var _this = this;
        this.listeners.forEach(function (listener) {
            listener(new Map(_this.flags));
        });
    };
    return FeatureFlagsManager;
}());
export { FeatureFlagsManager };
// Singleton instance
export var featureFlags = new FeatureFlagsManager();
/**
 * React hook for feature flags
 */
export function useFeatureFlag(flagKey) {
    var _a = React.useState(function () { return featureFlags.isEnabled(flagKey); }), enabled = _a[0], setEnabled = _a[1];
    React.useEffect(function () {
        var unsubscribe = featureFlags.subscribe(function (flags) {
            var _a;
            setEnabled((_a = flags.get(flagKey)) !== null && _a !== void 0 ? _a : false);
        });
        return unsubscribe;
    }, [flagKey]);
    return enabled;
}
/**
 * React hook for all feature flags
 */
export function useFeatureFlags() {
    var _a = React.useState(function () { return featureFlags.getAllFlags(); }), flags = _a[0], setFlags = _a[1];
    React.useEffect(function () {
        var unsubscribe = featureFlags.subscribe(function () {
            setFlags(featureFlags.getAllFlags());
        });
        return unsubscribe;
    }, []);
    return flags;
}
// Add React import for hooks
import React from 'react';
//# sourceMappingURL=FeatureFlags.js.map