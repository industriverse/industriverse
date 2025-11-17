/**
 * Service Worker Registration
 *
 * Handles service worker registration and updates
 */
import { __awaiter, __generator } from "tslib";
var ServiceWorkerManager = /** @class */ (function () {
    function ServiceWorkerManager() {
        this.registration = null;
        this.callbacks = [];
    }
    /**
     * Register service worker
     */
    ServiceWorkerManager.prototype.register = function () {
        return __awaiter(this, arguments, void 0, function (swUrl) {
            var _a, error_1;
            var _this = this;
            if (swUrl === void 0) { swUrl = '/sw.js'; }
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        if (!('serviceWorker' in navigator)) {
                            console.warn('Service Worker not supported');
                            this.notifyCallbacks({
                                registered: false,
                                installing: false,
                                waiting: false,
                                active: false,
                                error: new Error('Service Worker not supported')
                            });
                            return [2 /*return*/, null];
                        }
                        _b.label = 1;
                    case 1:
                        _b.trys.push([1, 3, , 4]);
                        console.log('Registering service worker...');
                        _a = this;
                        return [4 /*yield*/, navigator.serviceWorker.register(swUrl, {
                                scope: '/'
                            })];
                    case 2:
                        _a.registration = _b.sent();
                        console.log('Service worker registered:', this.registration.scope);
                        // Listen for updates
                        this.registration.addEventListener('updatefound', function () {
                            console.log('Service worker update found');
                            _this.handleUpdate();
                        });
                        // Check for updates periodically
                        setInterval(function () {
                            var _a;
                            (_a = _this.registration) === null || _a === void 0 ? void 0 : _a.update();
                        }, 60 * 60 * 1000); // Check every hour
                        this.notifyCallbacks(this.getStatus());
                        return [2 /*return*/, this.registration];
                    case 3:
                        error_1 = _b.sent();
                        console.error('Service worker registration failed:', error_1);
                        this.notifyCallbacks({
                            registered: false,
                            installing: false,
                            waiting: false,
                            active: false,
                            error: error_1
                        });
                        return [2 /*return*/, null];
                    case 4: return [2 /*return*/];
                }
            });
        });
    };
    /**
     * Unregister service worker
     */
    ServiceWorkerManager.prototype.unregister = function () {
        return __awaiter(this, void 0, void 0, function () {
            var result, error_2;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        if (!this.registration) {
                            return [2 /*return*/, false];
                        }
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        return [4 /*yield*/, this.registration.unregister()];
                    case 2:
                        result = _a.sent();
                        console.log('Service worker unregistered:', result);
                        this.registration = null;
                        this.notifyCallbacks({
                            registered: false,
                            installing: false,
                            waiting: false,
                            active: false,
                            error: null
                        });
                        return [2 /*return*/, result];
                    case 3:
                        error_2 = _a.sent();
                        console.error('Service worker unregistration failed:', error_2);
                        return [2 /*return*/, false];
                    case 4: return [2 /*return*/];
                }
            });
        });
    };
    /**
     * Update service worker
     */
    ServiceWorkerManager.prototype.update = function () {
        return __awaiter(this, void 0, void 0, function () {
            var error_3;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        if (!this.registration) {
                            console.warn('No service worker registered');
                            return [2 /*return*/];
                        }
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        return [4 /*yield*/, this.registration.update()];
                    case 2:
                        _a.sent();
                        console.log('Service worker update check completed');
                        return [3 /*break*/, 4];
                    case 3:
                        error_3 = _a.sent();
                        console.error('Service worker update failed:', error_3);
                        return [3 /*break*/, 4];
                    case 4: return [2 /*return*/];
                }
            });
        });
    };
    /**
     * Skip waiting and activate new service worker
     */
    ServiceWorkerManager.prototype.skipWaiting = function () {
        var _a;
        if (!((_a = this.registration) === null || _a === void 0 ? void 0 : _a.waiting)) {
            console.warn('No waiting service worker');
            return;
        }
        this.registration.waiting.postMessage({ type: 'SKIP_WAITING' });
    };
    /**
     * Get current status
     */
    ServiceWorkerManager.prototype.getStatus = function () {
        if (!this.registration) {
            return {
                registered: false,
                installing: false,
                waiting: false,
                active: false,
                error: null
            };
        }
        return {
            registered: true,
            installing: !!this.registration.installing,
            waiting: !!this.registration.waiting,
            active: !!this.registration.active,
            error: null
        };
    };
    /**
     * Subscribe to status changes
     */
    ServiceWorkerManager.prototype.subscribe = function (callback) {
        var _this = this;
        this.callbacks.push(callback);
        // Immediately call with current status
        callback(this.getStatus());
        // Return unsubscribe function
        return function () {
            _this.callbacks = _this.callbacks.filter(function (cb) { return cb !== callback; });
        };
    };
    ServiceWorkerManager.prototype.handleUpdate = function () {
        var _this = this;
        var _a;
        var installingWorker = (_a = this.registration) === null || _a === void 0 ? void 0 : _a.installing;
        if (!installingWorker)
            return;
        installingWorker.addEventListener('statechange', function () {
            if (installingWorker.state === 'installed') {
                if (navigator.serviceWorker.controller) {
                    // New service worker available
                    console.log('New service worker available');
                    _this.notifyCallbacks(_this.getStatus());
                }
                else {
                    // Service worker installed for first time
                    console.log('Service worker installed');
                    _this.notifyCallbacks(_this.getStatus());
                }
            }
        });
    };
    ServiceWorkerManager.prototype.notifyCallbacks = function (status) {
        this.callbacks.forEach(function (callback) {
            try {
                callback(status);
            }
            catch (error) {
                console.error('Service worker callback error:', error);
            }
        });
    };
    return ServiceWorkerManager;
}());
// Export singleton instance
export var swManager = new ServiceWorkerManager();
/**
 * Register service worker (convenience function)
 */
export function registerServiceWorker() {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            return [2 /*return*/, swManager.register()];
        });
    });
}
/**
 * Unregister service worker (convenience function)
 */
export function unregisterServiceWorker() {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            return [2 /*return*/, swManager.unregister()];
        });
    });
}
//# sourceMappingURL=sw-register.js.map