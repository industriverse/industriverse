/**
 * AmI Context Awareness Module
 * Week 8: White-Label Platform - Phase 3
 *
 * Implements the 4 AmI principles:
 * 1. Context-awareness - Perceives user state automatically
 * 2. Proactivity - Anticipates needs without commands
 * 3. Seamless integration - Intelligence blends invisibly
 * 4. Adaptivity - Uniquely tailored per user
 */
import { __assign, __spreadArray } from "tslib";
import { getCosmicFabric } from './CosmicFabric';
var AmIContextService = /** @class */ (function () {
    function AmIContextService(userId) {
        this.adaptiveRules = [];
        this.predictionHistory = [];
        this.contextHistory = [];
        this.maxHistorySize = 100;
        this.context = this.initializeContext(userId);
        this.setupDefaultRules();
        this.startContextMonitoring();
    }
    /**
     * Initialize user context
     */
    AmIContextService.prototype.initializeContext = function (userId) {
        return {
            userId: userId,
            sessionId: this.generateSessionId(),
            location: 'home',
            timeOfDay: this.getTimeOfDay(),
            deviceType: this.detectDeviceType(),
            networkQuality: 'good',
            preferences: {},
            recentActions: [],
            timestamp: Date.now(),
        };
    };
    /**
     * Start monitoring context changes
     */
    AmIContextService.prototype.startContextMonitoring = function () {
        var _this = this;
        // Monitor location changes
        window.addEventListener('popstate', function () {
            _this.updateLocation();
        });
        // Monitor network quality
        if ('connection' in navigator) {
            var connection = navigator.connection;
            connection.addEventListener('change', function () {
                _this.updateNetworkQuality();
            });
        }
        // Monitor battery level (if available)
        if ('getBattery' in navigator) {
            navigator.getBattery().then(function (battery) {
                _this.context.batteryLevel = battery.level * 100;
                battery.addEventListener('levelchange', function () {
                    _this.context.batteryLevel = battery.level * 100;
                    _this.onContextChange();
                });
            });
        }
        // Update time of day every minute
        setInterval(function () {
            var newTimeOfDay = _this.getTimeOfDay();
            if (newTimeOfDay !== _this.context.timeOfDay) {
                _this.context.timeOfDay = newTimeOfDay;
                _this.onContextChange();
            }
        }, 60000);
    };
    /**
     * Update current location
     */
    AmIContextService.prototype.updateLocation = function () {
        var path = window.location.pathname;
        var location = 'home';
        if (path.includes('/settings'))
            location = 'settings';
        else if (path.includes('/catalog'))
            location = 'catalog';
        else if (path.includes('/widgets'))
            location = 'widgets';
        else if (path.includes('/admin'))
            location = 'admin';
        if (location !== this.context.location) {
            this.context.location = location;
            this.onContextChange();
        }
    };
    /**
     * Update network quality
     */
    AmIContextService.prototype.updateNetworkQuality = function () {
        if ('connection' in navigator) {
            var connection = navigator.connection;
            var effectiveType = connection.effectiveType;
            var quality = 'good';
            if (effectiveType === '4g')
                quality = 'excellent';
            else if (effectiveType === '3g')
                quality = 'good';
            else if (effectiveType === '2g')
                quality = 'poor';
            else if (!navigator.onLine)
                quality = 'offline';
            if (quality !== this.context.networkQuality) {
                this.context.networkQuality = quality;
                this.onContextChange();
            }
        }
    };
    /**
     * Get time of day
     */
    AmIContextService.prototype.getTimeOfDay = function () {
        var hour = new Date().getHours();
        if (hour >= 5 && hour < 12)
            return 'morning';
        if (hour >= 12 && hour < 17)
            return 'afternoon';
        if (hour >= 17 && hour < 21)
            return 'evening';
        return 'night';
    };
    /**
     * Detect device type
     */
    AmIContextService.prototype.detectDeviceType = function () {
        var width = window.innerWidth;
        if (width < 768)
            return 'mobile';
        if (width < 1024)
            return 'tablet';
        return 'desktop';
    };
    /**
     * Generate session ID
     */
    AmIContextService.prototype.generateSessionId = function () {
        return "session_".concat(Date.now(), "_").concat(Math.random().toString(36).substr(2, 9));
    };
    /**
     * Context changed - trigger AmI logic
     */
    AmIContextService.prototype.onContextChange = function () {
        this.context.timestamp = Date.now();
        // Save to history
        this.contextHistory.push(__assign({}, this.context));
        if (this.contextHistory.length > this.maxHistorySize) {
            this.contextHistory.shift();
        }
        // Calculate AmI metrics
        var amiMetrics = this.calculateAmIMetrics();
        // Send to Cosmic Fabric for learning
        var fabric = getCosmicFabric();
        if (fabric) {
            fabric.learnLocal({
                type: 'user_behavior',
                features: this.contextToFeatures(this.context),
                confidence: 0.8,
                amiPrinciples: amiMetrics,
            });
        }
        // Run adaptive rules
        this.runAdaptiveRules();
        // Make predictions
        this.predictUserNeeds();
        // Emit event
        window.dispatchEvent(new CustomEvent('ami-context-change', {
            detail: { context: this.context, amiMetrics: amiMetrics },
        }));
    };
    /**
     * Convert context to feature vector
     */
    AmIContextService.prototype.contextToFeatures = function (context) {
        return [
            context.location === 'home' ? 1 : 0,
            context.location === 'settings' ? 1 : 0,
            context.location === 'catalog' ? 1 : 0,
            context.location === 'widgets' ? 1 : 0,
            context.location === 'admin' ? 1 : 0,
            context.timeOfDay === 'morning' ? 1 : 0,
            context.timeOfDay === 'afternoon' ? 1 : 0,
            context.timeOfDay === 'evening' ? 1 : 0,
            context.timeOfDay === 'night' ? 1 : 0,
            context.deviceType === 'mobile' ? 1 : 0,
            context.deviceType === 'tablet' ? 1 : 0,
            context.deviceType === 'desktop' ? 1 : 0,
            context.networkQuality === 'excellent' ? 1 : 0,
            context.networkQuality === 'good' ? 1 : 0,
            context.networkQuality === 'poor' ? 1 : 0,
            context.batteryLevel ? context.batteryLevel / 100 : 1,
            context.recentActions.length / 10,
        ];
    };
    /**
     * Calculate AmI metrics
     */
    AmIContextService.prototype.calculateAmIMetrics = function () {
        var contextAwareness = this.calculateContextAwareness();
        var proactivity = this.calculateProactivity();
        var seamlessness = this.calculateSeamlessness();
        var adaptivity = this.calculateAdaptivity();
        return {
            contextAwareness: contextAwareness,
            proactivity: proactivity,
            seamlessness: seamlessness,
            adaptivity: adaptivity,
        };
    };
    /**
     * Calculate context awareness score
     */
    AmIContextService.prototype.calculateContextAwareness = function () {
        // Based on how much context we're tracking
        var score = 0;
        if (this.context.location)
            score += 20;
        if (this.context.timeOfDay)
            score += 20;
        if (this.context.deviceType)
            score += 20;
        if (this.context.networkQuality)
            score += 20;
        if (this.context.batteryLevel !== undefined)
            score += 10;
        if (this.context.recentActions.length > 0)
            score += 10;
        return score;
    };
    /**
     * Calculate proactivity score
     */
    AmIContextService.prototype.calculateProactivity = function () {
        // Based on predictions made
        var recentPredictions = this.predictionHistory.filter(function (p) { return Date.now() - p.timestamp < 60000; } // Last minute
        );
        return Math.min(100, recentPredictions.length * 20);
    };
    /**
     * Calculate seamlessness score
     */
    AmIContextService.prototype.calculateSeamlessness = function () {
        // Based on how invisible the AmI is (fewer interruptions)
        var recentActions = this.context.recentActions.length;
        return Math.max(0, 100 - recentActions * 5);
    };
    /**
     * Calculate adaptivity score
     */
    AmIContextService.prototype.calculateAdaptivity = function () {
        // Based on adaptive rules triggered
        var enabledRules = this.adaptiveRules.filter(function (r) { return r.enabled; }).length;
        return Math.min(100, enabledRules * 10);
    };
    /**
     * Setup default adaptive rules
     */
    AmIContextService.prototype.setupDefaultRules = function () {
        var _this = this;
        // Rule: Low battery + poor network = suggest offline mode
        this.addAdaptiveRule({
            id: 'low_battery_offline',
            condition: function (ctx) {
                return (ctx.batteryLevel || 100) < 20 && ctx.networkQuality === 'poor';
            },
            action: function (ctx) {
                _this.suggestAction('Enable offline mode to save battery', 0.8);
            },
            priority: 10,
            enabled: true,
        });
        // Rule: Evening + home = suggest theme switch
        this.addAdaptiveRule({
            id: 'evening_dark_theme',
            condition: function (ctx) {
                return ctx.timeOfDay === 'evening' && ctx.location === 'home';
            },
            action: function (ctx) {
                _this.suggestAction('Switch to dark theme for better readability', 0.7);
            },
            priority: 5,
            enabled: true,
        });
        // Rule: Mobile + catalog = suggest filters
        this.addAdaptiveRule({
            id: 'mobile_catalog_filters',
            condition: function (ctx) {
                return ctx.deviceType === 'mobile' && ctx.location === 'catalog';
            },
            action: function (ctx) {
                _this.suggestAction('Use filters to find capsules faster', 0.6);
            },
            priority: 3,
            enabled: true,
        });
    };
    /**
     * Add adaptive rule
     */
    AmIContextService.prototype.addAdaptiveRule = function (rule) {
        this.adaptiveRules.push(rule);
        this.adaptiveRules.sort(function (a, b) { return b.priority - a.priority; });
    };
    /**
     * Run adaptive rules
     */
    AmIContextService.prototype.runAdaptiveRules = function () {
        for (var _i = 0, _a = this.adaptiveRules; _i < _a.length; _i++) {
            var rule = _a[_i];
            if (rule.enabled && rule.condition(this.context)) {
                rule.action(this.context);
            }
        }
    };
    /**
     * Predict user needs
     */
    AmIContextService.prototype.predictUserNeeds = function () {
        // Simple heuristic-based predictions
        // In production, this would use the federated model from Cosmic Fabric
        if (this.context.location === 'home' && this.context.recentActions.length === 0) {
            this.addPrediction({
                type: 'navigation',
                suggestion: 'View capsule catalog',
                confidence: 0.6,
                reasoning: 'Users typically browse catalog after landing',
                timestamp: Date.now(),
            });
        }
        if (this.context.location === 'catalog' && this.context.recentActions.includes('search')) {
            this.addPrediction({
                type: 'action',
                suggestion: 'Apply filters to refine search',
                confidence: 0.7,
                reasoning: 'Search followed by filtering is common pattern',
                timestamp: Date.now(),
            });
        }
    };
    /**
     * Add prediction
     */
    AmIContextService.prototype.addPrediction = function (prediction) {
        this.predictionHistory.push(prediction);
        if (this.predictionHistory.length > this.maxHistorySize) {
            this.predictionHistory.shift();
        }
        // Emit event
        window.dispatchEvent(new CustomEvent('ami-prediction', {
            detail: prediction,
        }));
    };
    /**
     * Suggest action to user
     */
    AmIContextService.prototype.suggestAction = function (suggestion, confidence) {
        console.log("[AmI] Suggestion: ".concat(suggestion, " (confidence: ").concat(confidence, ")"));
        // In production, this would show a subtle notification
        // For now, just log and emit event
        window.dispatchEvent(new CustomEvent('ami-suggestion', {
            detail: { suggestion: suggestion, confidence: confidence },
        }));
    };
    /**
     * Record user action
     */
    AmIContextService.prototype.recordAction = function (action) {
        this.context.recentActions.push(action);
        if (this.context.recentActions.length > 20) {
            this.context.recentActions.shift();
        }
        this.onContextChange();
    };
    /**
     * Get current context
     */
    AmIContextService.prototype.getContext = function () {
        return __assign({}, this.context);
    };
    /**
     * Get predictions
     */
    AmIContextService.prototype.getPredictions = function () {
        return __spreadArray([], this.predictionHistory, true);
    };
    /**
     * Update user preferences
     */
    AmIContextService.prototype.updatePreferences = function (preferences) {
        this.context.preferences = __assign(__assign({}, this.context.preferences), preferences);
        this.onContextChange();
    };
    return AmIContextService;
}());
export { AmIContextService };
// Singleton instance
var amiContextInstance = null;
export function initializeAmIContext(userId) {
    if (!amiContextInstance) {
        amiContextInstance = new AmIContextService(userId);
    }
    return amiContextInstance;
}
export function getAmIContext() {
    return amiContextInstance;
}
//# sourceMappingURL=AmIContext.js.map