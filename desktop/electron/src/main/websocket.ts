/**
 * WebSocket Manager
 * Handles real-time connection to Capsule Gateway
 */

import WebSocket from 'ws';
import { EventEmitter } from 'events';
import type { Capsule, CapsuleLaunchpad, WebSocketMessage } from '../types/capsule';

export interface WebSocketManagerEvents {
  connected: () => void;
  disconnected: () => void;
  message: (message: WebSocketMessage) => void;
  error: (error: Error) => void;
}

export declare interface WebSocketManager {
  on<K extends keyof WebSocketManagerEvents>(
    event: K,
    listener: WebSocketManagerEvents[K]
  ): this;
  emit<K extends keyof WebSocketManagerEvents>(
    event: K,
    ...args: Parameters<WebSocketManagerEvents[K]>
  ): boolean;
}

/**
 * WebSocket Manager with auto-reconnect
 */
export class WebSocketManager extends EventEmitter {
  private ws: WebSocket | null = null;
  private url: string;
  private authToken: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000; // Start with 1 second
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private isConnecting = false;
  private shouldReconnect = true;

  constructor(url: string, authToken: string) {
    super();
    this.url = url;
    this.authToken = authToken;
  }

  /**
   * Connect to WebSocket server
   */
  async connect(): Promise<void> {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      console.log('[WebSocket] Already connected or connecting');
      return;
    }

    this.isConnecting = true;
    this.shouldReconnect = true;

    try {
      console.log(`[WebSocket] Connecting to ${this.url}...`);

      this.ws = new WebSocket(this.url, {
        headers: {
          Authorization: `Bearer ${this.authToken}`,
        },
      });

      this.ws.on('open', () => this.handleOpen());
      this.ws.on('message', (data) => this.handleMessage(data));
      this.ws.on('close', (code, reason) => this.handleClose(code, reason));
      this.ws.on('error', (error) => this.handleError(error));
    } catch (error) {
      this.isConnecting = false;
      this.handleError(error as Error);
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    console.log('[WebSocket] Disconnecting...');
    this.shouldReconnect = false;

    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
  }

  /**
   * Send message to server
   */
  private send(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('[WebSocket] Cannot send message: not connected');
    }
  }

  /**
   * Handle WebSocket open event
   */
  private handleOpen(): void {
    console.log('[WebSocket] Connected');
    this.isConnecting = false;
    this.reconnectAttempts = 0;
    this.reconnectDelay = 1000;

    // Start heartbeat
    this.startHeartbeat();

    this.emit('connected');
  }

  /**
   * Handle WebSocket message event
   */
  private handleMessage(data: WebSocket.Data): void {
    try {
      const message: WebSocketMessage = JSON.parse(data.toString());
      console.log(`[WebSocket] Message received: ${message.type}`);
      this.emit('message', message);
    } catch (error) {
      console.error('[WebSocket] Failed to parse message:', error);
    }
  }

  /**
   * Handle WebSocket close event
   */
  private handleClose(code: number, reason: Buffer): void {
    console.log(`[WebSocket] Closed: ${code} - ${reason.toString()}`);
    this.isConnecting = false;

    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }

    this.emit('disconnected');

    // Auto-reconnect if not intentional disconnect
    if (this.shouldReconnect && code !== 1000) {
      this.attemptReconnect();
    }
  }

  /**
   * Handle WebSocket error event
   */
  private handleError(error: Error): void {
    console.error('[WebSocket] Error:', error.message);
    this.emit('error', error);
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WebSocket] Max reconnect attempts reached');
      this.emit('error', new Error('Max reconnect attempts reached'));
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000);

    console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    this.reconnectTimeout = setTimeout(() => {
      this.connect();
    }, delay);
  }

  /**
   * Start heartbeat to keep connection alive
   */
  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping', timestamp: new Date().toISOString() });
      }
    }, 30000); // Ping every 30 seconds
  }

  /**
   * Get user's launchpad
   */
  async getLaunchpad(userId: string): Promise<CapsuleLaunchpad> {
    return new Promise((resolve, reject) => {
      const requestId = Math.random().toString(36).substring(7);
      
      const timeout = setTimeout(() => {
        this.off('message', messageHandler);
        reject(new Error('Request timeout'));
      }, 5000);

      const messageHandler = (message: WebSocketMessage) => {
        if (message.type === 'launchpad_response' && message.payload.requestId === requestId) {
          clearTimeout(timeout);
          this.off('message', messageHandler);
          resolve(message.payload.launchpad);
        }
      };

      this.on('message', messageHandler);

      this.send({
        type: 'get_launchpad',
        payload: { userId, requestId },
        timestamp: new Date().toISOString(),
      });
    });
  }

  /**
   * Execute capsule action
   */
  async executeAction(capsuleId: string, actionId: string): Promise<{ success: boolean; message?: string }> {
    return new Promise((resolve, reject) => {
      const requestId = Math.random().toString(36).substring(7);
      
      const timeout = setTimeout(() => {
        this.off('message', messageHandler);
        reject(new Error('Request timeout'));
      }, 5000);

      const messageHandler = (message: WebSocketMessage) => {
        if (message.type === 'action_response' && message.payload.requestId === requestId) {
          clearTimeout(timeout);
          this.off('message', messageHandler);
          resolve(message.payload);
        }
      };

      this.on('message', messageHandler);

      this.send({
        type: 'execute_action',
        payload: { capsuleId, actionId, requestId },
        timestamp: new Date().toISOString(),
      });
    });
  }

  /**
   * Pin capsule
   */
  async pinCapsule(capsuleId: string, pinned: boolean): Promise<{ success: boolean }> {
    return new Promise((resolve, reject) => {
      const requestId = Math.random().toString(36).substring(7);
      
      const timeout = setTimeout(() => {
        this.off('message', messageHandler);
        reject(new Error('Request timeout'));
      }, 5000);

      const messageHandler = (message: WebSocketMessage) => {
        if (message.type === 'pin_response' && message.payload.requestId === requestId) {
          clearTimeout(timeout);
          this.off('message', messageHandler);
          resolve(message.payload);
        }
      };

      this.on('message', messageHandler);

      this.send({
        type: 'pin_capsule',
        payload: { capsuleId, pinned, requestId },
        timestamp: new Date().toISOString(),
      });
    });
  }

  /**
   * Hide capsule
   */
  async hideCapsule(capsuleId: string): Promise<{ success: boolean }> {
    return new Promise((resolve, reject) => {
      const requestId = Math.random().toString(36).substring(7);
      
      const timeout = setTimeout(() => {
        this.off('message', messageHandler);
        reject(new Error('Request timeout'));
      }, 5000);

      const messageHandler = (message: WebSocketMessage) => {
        if (message.type === 'hide_response' && message.payload.requestId === requestId) {
          clearTimeout(timeout);
          this.off('message', messageHandler);
          resolve(message.payload);
        }
      };

      this.on('message', messageHandler);

      this.send({
        type: 'hide_capsule',
        payload: { capsuleId, requestId },
        timestamp: new Date().toISOString(),
      });
    });
  }

  /**
   * Snooze capsule
   */
  async snoozeCapsule(capsuleId: string, duration: number): Promise<{ success: boolean }> {
    return new Promise((resolve, reject) => {
      const requestId = Math.random().toString(36).substring(7);
      
      const timeout = setTimeout(() => {
        this.off('message', messageHandler);
        reject(new Error('Request timeout'));
      }, 5000);

      const messageHandler = (message: WebSocketMessage) => {
        if (message.type === 'snooze_response' && message.payload.requestId === requestId) {
          clearTimeout(timeout);
          this.off('message', messageHandler);
          resolve(message.payload);
        }
      };

      this.on('message', messageHandler);

      this.send({
        type: 'snooze_capsule',
        payload: { capsuleId, duration, requestId },
        timestamp: new Date().toISOString(),
      });
    });
  }
}
