/**
 * CapsuleWebSocket Service
 *
 * Manages WebSocket connection to Capsule Gateway Service for real-time updates.
 * Features:
 * - Automatic reconnection with exponential backoff
 * - Heartbeat mechanism to keep connection alive
 * - Message queue for offline actions
 * - Type-safe message handling
 */
var CapsuleWebSocket = /** @class */ (function () {
    function CapsuleWebSocket(config) {
        this.ws = null;
        this.state = 'disconnected';
        this.reconnectAttempts = 0;
        this.reconnectTimeout = null;
        this.heartbeatInterval = null;
        this.messageQueue = [];
        this.isIntentionallyClosed = false;
        this.config = {
            url: config.url,
            authToken: config.authToken || '',
            reconnectDelay: config.reconnectDelay || 1000,
            maxReconnectDelay: config.maxReconnectDelay || 30000,
            heartbeatInterval: config.heartbeatInterval || 30000,
            onStateChange: config.onStateChange || (function () { }),
            onMessage: config.onMessage || (function () { }),
            onError: config.onError || (function () { })
        };
    }
    /**
     * Connect to WebSocket server
     */
    CapsuleWebSocket.prototype.connect = function () {
        var _a, _b;
        if (((_a = this.ws) === null || _a === void 0 ? void 0 : _a.readyState) === WebSocket.OPEN || ((_b = this.ws) === null || _b === void 0 ? void 0 : _b.readyState) === WebSocket.CONNECTING) {
            console.warn('WebSocket already connected or connecting');
            return;
        }
        this.isIntentionallyClosed = false;
        this.setState('connecting');
        try {
            // Add auth token to URL if provided
            var url = this.config.authToken
                ? "".concat(this.config.url, "?token=").concat(this.config.authToken)
                : this.config.url;
            this.ws = new WebSocket(url);
            this.setupEventHandlers();
        }
        catch (error) {
            this.handleError(error);
            this.scheduleReconnect();
        }
    };
    /**
     * Disconnect from WebSocket server
     */
    CapsuleWebSocket.prototype.disconnect = function () {
        this.isIntentionallyClosed = true;
        this.clearReconnectTimeout();
        this.clearHeartbeat();
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.setState('disconnected');
    };
    /**
     * Send message to server
     */
    CapsuleWebSocket.prototype.send = function (message) {
        var _a;
        var payload = JSON.stringify(message);
        if (((_a = this.ws) === null || _a === void 0 ? void 0 : _a.readyState) === WebSocket.OPEN) {
            this.ws.send(payload);
        }
        else {
            // Queue message for sending when connection is restored
            this.messageQueue.push(payload);
            console.warn('WebSocket not connected, message queued');
        }
    };
    /**
     * Get current connection state
     */
    CapsuleWebSocket.prototype.getState = function () {
        return this.state;
    };
    /**
     * Update auth token
     */
    CapsuleWebSocket.prototype.updateAuthToken = function (token) {
        this.config.authToken = token;
        // Reconnect with new token if currently connected
        if (this.state === 'connected') {
            this.disconnect();
            this.connect();
        }
    };
    CapsuleWebSocket.prototype.setupEventHandlers = function () {
        var _this = this;
        if (!this.ws)
            return;
        this.ws.onopen = function () {
            console.log('WebSocket connected');
            _this.setState('connected');
            _this.reconnectAttempts = 0;
            _this.startHeartbeat();
            _this.flushMessageQueue();
        };
        this.ws.onmessage = function (event) {
            try {
                var message = JSON.parse(event.data);
                _this.handleMessage(message);
            }
            catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };
        this.ws.onerror = function (event) {
            var errorMessage = 'WebSocket connection failed. This is expected in development mode with mock data.';
            // Only log as warning in development, error in production
            if (import.meta.env.DEV) {
                console.warn('WebSocket connection unavailable:', errorMessage);
            }
            else {
                console.error('WebSocket error:', event);
            }
            _this.handleError(new Error(errorMessage));
        };
        this.ws.onclose = function (event) {
            console.log('WebSocket closed:', event.code, event.reason);
            _this.clearHeartbeat();
            if (!_this.isIntentionallyClosed) {
                _this.setState('disconnected');
                _this.scheduleReconnect();
            }
        };
    };
    CapsuleWebSocket.prototype.handleMessage = function (message) {
        // Handle heartbeat responses
        if (message.type === 'heartbeat') {
            // Heartbeat received, connection is alive
            return;
        }
        // Handle auth responses
        if (message.type === 'auth_success') {
            console.log('Authentication successful:', message.data.userId);
            return;
        }
        if (message.type === 'auth_failed') {
            console.error('Authentication failed:', message.data.reason);
            this.setState('error');
            return;
        }
        // Forward message to callback
        this.config.onMessage(message);
    };
    CapsuleWebSocket.prototype.handleError = function (error) {
        this.setState('error');
        // Don't trigger error callback in development mode for connection failures
        if (!import.meta.env.DEV || !error.message.includes('expected in development')) {
            this.config.onError(error);
        }
    };
    CapsuleWebSocket.prototype.setState = function (newState) {
        if (this.state !== newState) {
            this.state = newState;
            this.config.onStateChange(newState);
        }
    };
    CapsuleWebSocket.prototype.scheduleReconnect = function () {
        var _this = this;
        if (this.isIntentionallyClosed)
            return;
        this.clearReconnectTimeout();
        // Exponential backoff with max delay
        var delay = Math.min(this.config.reconnectDelay * Math.pow(2, this.reconnectAttempts), this.config.maxReconnectDelay);
        console.log("Reconnecting in ".concat(delay, "ms (attempt ").concat(this.reconnectAttempts + 1, ")"));
        this.reconnectTimeout = setTimeout(function () {
            _this.reconnectAttempts++;
            _this.connect();
        }, delay);
    };
    CapsuleWebSocket.prototype.clearReconnectTimeout = function () {
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
            this.reconnectTimeout = null;
        }
    };
    CapsuleWebSocket.prototype.startHeartbeat = function () {
        var _this = this;
        this.clearHeartbeat();
        this.heartbeatInterval = setInterval(function () {
            var _a;
            if (((_a = _this.ws) === null || _a === void 0 ? void 0 : _a.readyState) === WebSocket.OPEN) {
                _this.send({ type: 'heartbeat', timestamp: new Date().toISOString() });
            }
        }, this.config.heartbeatInterval);
    };
    CapsuleWebSocket.prototype.clearHeartbeat = function () {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    };
    CapsuleWebSocket.prototype.flushMessageQueue = function () {
        var _a;
        while (this.messageQueue.length > 0 && ((_a = this.ws) === null || _a === void 0 ? void 0 : _a.readyState) === WebSocket.OPEN) {
            var message = this.messageQueue.shift();
            if (message) {
                this.ws.send(message);
            }
        }
    };
    return CapsuleWebSocket;
}());
export { CapsuleWebSocket };
//# sourceMappingURL=CapsuleWebSocket.js.map