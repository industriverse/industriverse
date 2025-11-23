/**
 * useCapsuleWebSocket Hook
 * 
 * React hook for managing WebSocket connection to Capsule Gateway.
 * Provides easy integration with React components.
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { CapsuleWebSocket, type ConnectionState, type WebSocketMessage } from '@/services/CapsuleWebSocket';
import type { CapsuleData, CapsuleUpdate } from '@/types/capsule';

export interface UseCapsuleWebSocketOptions {
  url: string;
  authToken?: string;
  autoConnect?: boolean;
  onCapsuleUpdate?: (update: CapsuleUpdate) => void;
  onCapsuleNew?: (capsule: CapsuleData) => void;
  onCapsuleRemoved?: (capsuleId: string) => void;
  onError?: (error: Error) => void;
}

export interface UseCapsuleWebSocketReturn {
  connectionState: ConnectionState;
  connect: () => void;
  disconnect: () => void;
  send: (message: object) => void;
  isConnected: boolean;
  isConnecting: boolean;
  isDisconnected: boolean;
  hasError: boolean;
}

export function useCapsuleWebSocket(options: UseCapsuleWebSocketOptions): UseCapsuleWebSocketReturn {
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const wsRef = useRef<CapsuleWebSocket | null>(null);

  // Initialize WebSocket instance
  useEffect(() => {
    const ws = new CapsuleWebSocket({
      url: options.url,
      authToken: options.authToken,
      onStateChange: setConnectionState,
      onMessage: (message: WebSocketMessage) => {
        switch (message.type) {
          case 'capsule_update':
            options.onCapsuleUpdate?.(message.data);
            break;
          case 'capsule_new':
            options.onCapsuleNew?.(message.data);
            break;
          case 'capsule_removed':
            options.onCapsuleRemoved?.(message.data.capsuleId);
            break;
          case 'error':
            options.onError?.(new Error(message.data.message));
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
    return () => {
      ws.disconnect();
    };
  }, [options.url, options.authToken, options.autoConnect]);

  // Update auth token when it changes
  useEffect(() => {
    if (options.authToken && wsRef.current) {
      wsRef.current.updateAuthToken(options.authToken);
    }
  }, [options.authToken]);

  const connect = useCallback(() => {
    wsRef.current?.connect();
  }, []);

  const disconnect = useCallback(() => {
    wsRef.current?.disconnect();
  }, []);

  const send = useCallback((message: object) => {
    wsRef.current?.send(message);
  }, []);

  return {
    connectionState,
    connect,
    disconnect,
    send,
    isConnected: connectionState === 'connected',
    isConnecting: connectionState === 'connecting',
    isDisconnected: connectionState === 'disconnected',
    hasError: connectionState === 'error'
  };
}
