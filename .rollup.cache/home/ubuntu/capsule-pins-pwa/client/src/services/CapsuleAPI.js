/**
 * Capsule Gateway API Service
 *
 * REST API client for Capsule Gateway Service
 */
import { __assign, __awaiter, __generator } from "tslib";
var CapsuleAPI = /** @class */ (function () {
    function CapsuleAPI(config) {
        this.config = {
            baseUrl: config.baseUrl,
            authToken: config.authToken || ''
        };
    }
    /**
     * Get all capsules
     */
    CapsuleAPI.prototype.getCapsules = function () {
        return __awaiter(this, void 0, void 0, function () {
            var response;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.fetch('/api/v1/capsules')];
                    case 1:
                        response = _a.sent();
                        return [2 /*return*/, response.json()];
                }
            });
        });
    };
    /**
     * Get capsule by ID
     */
    CapsuleAPI.prototype.getCapsule = function (id) {
        return __awaiter(this, void 0, void 0, function () {
            var response;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.fetch("/api/v1/capsules/".concat(id))];
                    case 1:
                        response = _a.sent();
                        return [2 /*return*/, response.json()];
                }
            });
        });
    };
    /**
     * Execute action on capsule
     */
    CapsuleAPI.prototype.executeAction = function (request) {
        return __awaiter(this, void 0, void 0, function () {
            var response;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.fetch('/api/v1/capsule/action', {
                            method: 'POST',
                            body: JSON.stringify(request)
                        })];
                    case 1:
                        response = _a.sent();
                        return [2 /*return*/, response.json()];
                }
            });
        });
    };
    /**
     * Get capsule statistics
     */
    CapsuleAPI.prototype.getStatistics = function () {
        return __awaiter(this, void 0, void 0, function () {
            var response;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.fetch('/api/v1/capsules/statistics')];
                    case 1:
                        response = _a.sent();
                        return [2 /*return*/, response.json()];
                }
            });
        });
    };
    /**
     * Update auth token
     */
    CapsuleAPI.prototype.updateAuthToken = function (token) {
        this.config.authToken = token;
    };
    /**
     * Internal fetch wrapper with auth and error handling
     */
    CapsuleAPI.prototype.fetch = function (path_1) {
        return __awaiter(this, arguments, void 0, function (path, options) {
            var url, headers, response_1, error, error_1;
            if (options === void 0) { options = {}; }
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        url = "".concat(this.config.baseUrl).concat(path);
                        headers = __assign({ 'Content-Type': 'application/json' }, (options.headers || {}));
                        if (this.config.authToken) {
                            headers['Authorization'] = "Bearer ".concat(this.config.authToken);
                        }
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 5, , 6]);
                        return [4 /*yield*/, fetch(url, __assign(__assign({}, options), { headers: headers }))];
                    case 2:
                        response_1 = _a.sent();
                        if (!!response_1.ok) return [3 /*break*/, 4];
                        return [4 /*yield*/, response_1.json().catch(function () { return ({
                                message: response_1.statusText
                            }); })];
                    case 3:
                        error = _a.sent();
                        throw new Error(error.message || "HTTP ".concat(response_1.status));
                    case 4: return [2 /*return*/, response_1];
                    case 5:
                        error_1 = _a.sent();
                        if (error_1 instanceof TypeError) {
                            throw new Error('Network error: Unable to reach server');
                        }
                        throw error_1;
                    case 6: return [2 /*return*/];
                }
            });
        });
    };
    return CapsuleAPI;
}());
export { CapsuleAPI };
// Create singleton instance
var apiInstance = null;
/**
 * Get API instance
 */
export function getAPI() {
    if (!apiInstance) {
        var baseUrl = import.meta.env.VITE_CAPSULE_GATEWAY_API || 'https://capsule-gateway.industriverse.io';
        var authToken = import.meta.env.VITE_AUTH_TOKEN || '';
        apiInstance = new CapsuleAPI({
            baseUrl: baseUrl,
            authToken: authToken
        });
    }
    return apiInstance;
}
/**
 * Update API auth token
 */
export function updateAPIToken(token) {
    getAPI().updateAuthToken(token);
}
//# sourceMappingURL=CapsuleAPI.js.map