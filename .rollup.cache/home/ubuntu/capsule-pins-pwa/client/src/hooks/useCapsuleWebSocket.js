/**
 * useCapsuleWebSocket Hook
 *
 * React hook for managing WebSocket connection to Capsule Gateway.
 * Provides easy integration with React components.
 */
import { useEffect, useRef, useState, useCallback } from 'react';
import { CapsuleWebSocket } from '@/services/CapsuleWebSocket';
export function useCapsuleWebSocket(options) {
    var _a = useState('disconnected'), connectionState = _a[0], setConnectionState = _a[1];
    var wsRef = useRef(null);
    // Initialize WebSocket instance
    useEffect(function () {
        var ws = new CapsuleWebSocket({
            url: options.url,
            authToken: options.authToken,
            onStateChange: setConnectionState,
            onMessage: function (message) {
                var _a, _b, _c, _d;
                switch (message.type) {
                    case 'capsule_update':
                        (_a = options.onCapsuleUpdate) === null || _a === void 0 ? void 0 : _a.call(options, message.data);
                        break;
                    case 'capsule_new':
                        (_b = options.onCapsuleNew) === null || _b === void 0 ? void 0 : _b.call(options, message.data);
                        break;
                    case 'capsule_removed':
                        (_c = options.onCapsuleRemoved) === null || _c === void 0 ? void 0 : _c.call(options, message.data.capsuleId);
                        break;
                    case 'error':
                        (_d = options.onError) === null || _d === void 0 ? void 0 : _d.call(options, new Error(message.data.message));
                        break;
                }
            },
            onError: options.onError
        });
        wsRef.current = ws;
        // Auto-connect if enabled
        if (options.autoConnect !== false) {
            ws.connect();
        }
        // Cleanup on unmount
        return function () {
            ws.disconnect();
        };
    }, [options.url, options.authToken, options.autoConnect]);
    // Update auth token when it changes
    useEffect(function () {
        if (options.authToken && wsRef.current) {
            wsRef.current.updateAuthToken(options.authToken);
        }
    }, [options.authToken]);
    var connect = useCallback(function () {
        var _a;
        (_a = wsRef.current) === null || _a === void 0 ? void 0 : _a.connect();
    }, []);
    var disconnect = useCallback(function () {
        var _a;
        (_a = wsRef.current) === null || _a === void 0 ? void 0 : _a.disconnect();
    }, []);
    var send = useCallback(function (message) {
        var _a;
        (_a = wsRef.current) === null || _a === void 0 ? void 0 : _a.send(message);
    }, []);
    return {
        connectionState: connectionState,
        connect: connect,
        disconnect: disconnect,
        send: send,
        isConnected: connectionState === 'connected',
        isConnecting: connectionState === 'connecting',
        isDisconnected: connectionState === 'disconnected',
        hasError: connectionState === 'error'
    };
}
//# sourceMappingURL=useCapsuleWebSocket.js.map