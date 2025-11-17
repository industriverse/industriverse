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

import type { CapsuleData, CapsuleUpdate } from '@/types/capsule';

export type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

export type WebSocketMessage = 
  | { type: 'capsule_update'; data: CapsuleUpdate }
  | { type: 'capsule_new'; data: CapsuleData }
  | { type: 'capsule_removed'; data: { capsuleId: string } }
  | { type: 'heartbeat'; data: { timestamp: string } }
  | { type: 'auth_success'; data: { userId: string } }
  | { type: 'auth_failed'; data: { reason: string } }
  | { type: 'error'; data: { message: string } };

export interface CapsuleWebSocketConfig {
  url: string;
  authToken?: string;
  reconnectDelay?: number;
  maxReconnectDelay?: number;
  heartbeatInterval?: number;
  onStateChange?: (state: ConnectionState) => void;
  onMessage?: (message: WebSocketMessage) => void;
  onError?: (error: Error) => void;
}

export class CapsuleWebSocket {
  private ws: WebSocket | null = null;
  private config: Required<CapsuleWebSocketConfig>;
  private state: ConnectionState = 'disconnected';
  private reconnectAttempts = 0;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private messageQueue: string[] = [];
  private isIntentionallyClosed = false;

  constructor(config: CapsuleWebSocketConfig) {
    this.config = {
      url: config.url,
      authToken: config.authToken || '',
      reconnectDelay: config.reconnectDelay || 1000,
      maxReconnectDelay: config.maxReconnectDelay || 30000,
      heartbeatInterval: config.heartbeatInterval || 30000,
      onStateChange: config.onStateChange || (() => {}),
      onMessage: config.onMessage || (() => {}),
      onError: config.onError || (() => {})
    };
  }

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN || this.ws?.readyState === WebSocket.CONNECTING) {
      console.warn('WebSocket already connected or connecting');
      return;
    }

    this.isIntentionallyClosed = false;
    this.setState('connecting');

    try {
      // Add auth token to URL if provided
      const url = this.config.authToken 
        ? `${this.config.url}?token=${this.config.authToken}`
        : this.config.url;

      this.ws = new WebSocket(url);
      this.setupEventHandlers();
    } catch (error) {
      this.handleError(error as Error);
      this.scheduleReconnect();
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.isIntentionallyClosed = true;
    this.clearReconnectTimeout();
    this.clearHeartbeat();
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.setState('disconnected');
  }

  /**
   * Send message to server
   */
  send(message: object): void {
    const payload = JSON.stringify(message);
    
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(payload);
    } else {
      // Queue message for sending when connection is restored
      this.messageQueue.push(payload);
      console.warn('WebSocket not connected, message queued');
    }
  }

  /**
   * Get current connection state
   */
  getState(): ConnectionState {
    return this.state;
  }

  /**
   * Update auth token
   */
  updateAuthToken(token: string): void {
    this.config.authToken = token;
    
    // Reconnect with new token if currently connected
    if (this.state === 'connected') {
      this.disconnect();
      this.connect();
    }
  }

  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.setState('connected');
      this.reconnectAttempts = 0;
      this.startHeartbeat();
      this.flushMessageQueue();
    };

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as WebSocketMessage;
        this.handleMessage(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onerror = (event) => {
      console.error('WebSocket error:', event);
      this.handleError(new Error('WebSocket connection error'));
    };

    this.ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason);
      this.clearHeartbeat();
      
      if (!this.isIntentionallyClosed) {
        this.setState('disconnected');
        this.scheduleReconnect();
      }
    };
  }

  private handleMessage(message: WebSocketMessage): void {
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
  }

  private handleError(error: Error): void {
    this.setState('error');
    this.config.onError(error);
  }

  private setState(newState: ConnectionState): void {
    if (this.state !== newState) {
      this.state = newState;
      this.config.onStateChange(newState);
    }
  }

  private scheduleReconnect(): void {
    if (this.isIntentionallyClosed) return;

    this.clearReconnectTimeout();

    // Exponential backoff with max delay
    const delay = Math.min(
      this.config.reconnectDelay * Math.pow(2, this.reconnectAttempts),
      this.config.maxReconnectDelay
    );

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts + 1})`);

    this.reconnectTimeout = setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, delay);
  }

  private clearReconnectTimeout(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
  }

  private startHeartbeat(): void {
    this.clearHeartbeat();

    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({ type: 'heartbeat', timestamp: new Date().toISOString() });
      }
    }, this.config.heartbeatInterval);
  }

  private clearHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0 && this.ws?.readyState === WebSocket.OPEN) {
      const message = this.messageQueue.shift();
      if (message) {
        this.ws.send(message);
      }
    }
  }
}
