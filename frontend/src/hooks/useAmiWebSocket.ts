import { useEffect, useState, useCallback, useRef } from 'react';
import { io, Socket } from 'socket.io-client';

export interface AmiMetric {
  tenantId: string;
  deploymentId: string;
  principle: 'context' | 'proactivity' | 'seamlessness' | 'adaptivity';
  value: number;
  timestamp: Date;
}

export interface AmiMetrics {
  context: number;
  proactivity: number;
  seamlessness: number;
  adaptivity: number;
}

interface UseAmiWebSocketOptions {
  tenantId?: string;
  deploymentId?: string;
  autoConnect?: boolean;
}

export function useAmiWebSocket(options: UseAmiWebSocketOptions = {}) {
  const { tenantId, deploymentId, autoConnect = true } = options;
  
  const [isConnected, setIsConnected] = useState(false);
  const [metrics, setMetrics] = useState<AmiMetrics>({
    context: 0,
    proactivity: 0,
    seamlessness: 0,
    adaptivity: 0,
  });
  const [history, setHistory] = useState<AmiMetric[]>([]);
  const socketRef = useRef<Socket | null>(null);

  const connect = useCallback(() => {
    if (socketRef.current?.connected) {
      return;
    }

    // Connect to WebSocket server
    const socket = io({
      path: '/api/socket.io',
      transports: ['websocket', 'polling'],
    });

    socket.on('connect', () => {
      console.log('[AmI WebSocket] Connected');
      setIsConnected(true);

      // Subscribe to tenant or deployment room
      if (tenantId) {
        socket.emit('subscribe:tenant', tenantId);
      }
      if (deploymentId) {
        socket.emit('subscribe:deployment', deploymentId);
      }
    });

    socket.on('disconnect', () => {
      console.log('[AmI WebSocket] Disconnected');
      setIsConnected(false);
    });

    socket.on('subscribed', (data: { tenantId?: string; deploymentId?: string }) => {
      console.log('[AmI WebSocket] Subscribed:', data);
    });

    socket.on('ami:metric', (metric: AmiMetric) => {
      console.log('[AmI WebSocket] Received metric:', metric);

      // Update current metrics
      setMetrics((prev) => ({
        ...prev,
        [metric.principle]: metric.value,
      }));

      // Add to history (keep last 100)
      setHistory((prev) => {
        const newHistory = [metric, ...prev].slice(0, 100);
        return newHistory;
      });
    });

    socketRef.current = socket;
  }, [tenantId, deploymentId]);

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
      setIsConnected(false);
    }
  }, []);

  const subscribe = useCallback((roomType: 'tenant' | 'deployment', roomId: string) => {
    if (!socketRef.current?.connected) {
      console.warn('[AmI WebSocket] Not connected, cannot subscribe');
      return;
    }

    if (roomType === 'tenant') {
      socketRef.current.emit('subscribe:tenant', roomId);
    } else {
      socketRef.current.emit('subscribe:deployment', roomId);
    }
  }, []);

  const unsubscribe = useCallback((room: string) => {
    if (!socketRef.current?.connected) {
      return;
    }

    socketRef.current.emit('unsubscribe', room);
  }, []);

  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    isConnected,
    metrics,
    history,
    connect,
    disconnect,
    subscribe,
    unsubscribe,
  };
}
