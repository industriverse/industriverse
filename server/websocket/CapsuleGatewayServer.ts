/**
 * Capsule Gateway WebSocket Server
 * 
 * Real-time capsule broadcasting to connected clients
 */

import { WebSocketServer, WebSocket } from 'ws';
import type { Server } from 'http';

interface CapsuleData {
  id: string;
  title: string;
  description: string;
  status: 'active' | 'warning' | 'critical' | 'resolved' | 'dismissed';
  priority: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  createdAt: string;
  updatedAt: string;
  actions: string[];
  metrics?: Record<string, any>;
  metadata?: Record<string, any>;
}

interface ClientConnection {
  ws: WebSocket;
  userId?: string;
  subscriptions: Set<string>; // Capsule IDs or 'all'
  lastHeartbeat: number;
}

type WebSocketMessage =
  | { type: 'subscribe'; capsuleIds: string[] | 'all' }
  | { type: 'unsubscribe'; capsuleIds: string[] }
  | { type: 'action'; capsuleId: string; action: string; metadata?: Record<string, any> }
  | { type: 'heartbeat'; timestamp: string };

export class CapsuleGatewayServer {
  private wss: WebSocketServer;
  private clients: Map<WebSocket, ClientConnection> = new Map();
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private onAction?: (
    capsuleId: string,
    action: string,
    metadata?: Record<string, any>
  ) => Promise<void>;

  constructor(
    server: Server,
    onAction?: (capsuleId: string, action: string, metadata?: Record<string, any>) => Promise<void>
  ) {
    this.onAction = onAction;

    // Create WebSocket server
    this.wss = new WebSocketServer({
      server,
      path: '/ws',
    });

    console.log('[CapsuleGateway] WebSocket server created');

    // Handle connections
    this.wss.on('connection', (ws: WebSocket, request: any) => {
      this.handleConnection(ws, request);
    });

    // Start heartbeat checker
    this.startHeartbeatChecker();
  }

  /**
   * Handle new WebSocket connection
   */
  private handleConnection(ws: WebSocket, request: any): void {
    const clientIp = request.socket.remoteAddress;
    console.log(`[CapsuleGateway] New connection from ${clientIp}`);

    // Create client connection
    const client: ClientConnection = {
      ws,
      subscriptions: new Set(),
      lastHeartbeat: Date.now(),
    };

    this.clients.set(ws, client);

    // Handle messages
    ws.on('message', (data: WebSocket.Data) => {
      this.handleMessage(ws, data);
    });

    // Handle close
    ws.on('close', () => {
      console.log(`[CapsuleGateway] Client disconnected: ${clientIp}`);
      this.clients.delete(ws);
    });

    // Handle error
    ws.on('error', (error: Error) => {
      console.error(`[CapsuleGateway] WebSocket error:`, error);
      this.clients.delete(ws);
    });

    // Send welcome message
    this.send(ws, {
      type: 'connected',
      data: {
        message: 'Connected to Capsule Gateway',
        timestamp: new Date().toISOString(),
      },
    });
  }

  /**
   * Handle incoming message from client
   */
  private handleMessage(ws: WebSocket, data: any): void {
    try {
      const message: WebSocketMessage = JSON.parse(data.toString());
      const client = this.clients.get(ws);

      if (!client) {
        console.error('[CapsuleGateway] Client not found');
        return;
      }

      switch (message.type) {
        case 'subscribe':
          this.handleSubscribe(client, message.capsuleIds);
          break;

        case 'unsubscribe':
          this.handleUnsubscribe(client, message.capsuleIds);
          break;

        case 'action':
          this.handleAction(client, message.capsuleId, message.action, message.metadata);
          break;

        case 'heartbeat':
          this.handleHeartbeat(client);
          break;

        default:
          console.warn(`[CapsuleGateway] Unknown message type:`, message);
      }
    } catch (error) {
      console.error('[CapsuleGateway] Failed to handle message:', error);
      this.send(ws, {
        type: 'error',
        data: { message: 'Invalid message format' },
      });
    }
  }

  /**
   * Handle subscribe request
   */
  private handleSubscribe(client: ClientConnection, capsuleIds: string[] | 'all'): void {
    if (capsuleIds === 'all') {
      client.subscriptions.add('all');
      console.log('[CapsuleGateway] Client subscribed to all capsules');
    } else {
      for (const id of capsuleIds) {
        client.subscriptions.add(id);
      }
      console.log(`[CapsuleGateway] Client subscribed to ${capsuleIds.length} capsules`);
    }

    this.send(client.ws, {
      type: 'subscribed',
      data: { capsuleIds },
    });
  }

  /**
   * Handle unsubscribe request
   */
  private handleUnsubscribe(client: ClientConnection, capsuleIds: string[]): void {
    for (const id of capsuleIds) {
      client.subscriptions.delete(id);
    }

    console.log(`[CapsuleGateway] Client unsubscribed from ${capsuleIds.length} capsules`);

    this.send(client.ws, {
      type: 'unsubscribed',
      data: { capsuleIds },
    });
  }

  /**
   * Handle action request
   */
  private async handleAction(
    client: ClientConnection,
    capsuleId: string,
    action: string,
    metadata?: Record<string, any>
  ): Promise<void> {
    console.log(`[CapsuleGateway] Action received: ${action} on ${capsuleId}`);

    if (this.onAction) {
      try {
        await this.onAction(capsuleId, action, metadata);

        this.send(client.ws, {
          type: 'action_success',
          data: { capsuleId, action },
        });
      } catch (error) {
        console.error('[CapsuleGateway] Action failed:', error);
        this.send(client.ws, {
          type: 'action_failed',
          data: {
            capsuleId,
            action,
            error: (error as Error).message,
          },
        });
      }
    }
  }

  /**
   * Handle heartbeat
   */
  private handleHeartbeat(client: ClientConnection): void {
    client.lastHeartbeat = Date.now();

    this.send(client.ws, {
      type: 'heartbeat',
      data: { timestamp: new Date().toISOString() },
    });
  }

  /**
   * Broadcast new capsule to subscribed clients
   */
  broadcastNewCapsule(capsule: CapsuleData): void {
    console.log(`[CapsuleGateway] Broadcasting new capsule: ${capsule.id}`);

    const message = {
      type: 'capsule_new',
      data: capsule,
    };

    for (const [ws, client] of this.clients) {
      if (
        client.subscriptions.has('all') ||
        client.subscriptions.has(capsule.id)
      ) {
        this.send(ws, message);
      }
    }
  }

  /**
   * Broadcast capsule update to subscribed clients
   */
  broadcastCapsuleUpdate(capsuleId: string, updates: Partial<CapsuleData>): void {
    console.log(`[CapsuleGateway] Broadcasting update for capsule: ${capsuleId}`);

    const message = {
      type: 'capsule_update',
      data: {
        capsuleId,
        updates,
        timestamp: new Date().toISOString(),
      },
    };

    for (const [ws, client] of this.clients) {
      if (
        client.subscriptions.has('all') ||
        client.subscriptions.has(capsuleId)
      ) {
        this.send(ws, message);
      }
    }
  }

  /**
   * Broadcast capsule removal to subscribed clients
   */
  broadcastCapsuleRemoved(capsuleId: string): void {
    console.log(`[CapsuleGateway] Broadcasting removal of capsule: ${capsuleId}`);

    const message = {
      type: 'capsule_removed',
      data: { capsuleId },
    };

    for (const [ws, client] of this.clients) {
      if (
        client.subscriptions.has('all') ||
        client.subscriptions.has(capsuleId)
      ) {
        this.send(ws, message);
      }
    }
  }

  /**
   * Send message to specific client
   */
  private send(ws: WebSocket, message: any): void {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    }
  }

  /**
   * Start heartbeat checker (detect dead connections)
   */
  private startHeartbeatChecker(): void {
    this.heartbeatInterval = setInterval(() => {
      const now = Date.now();
      const timeout = 60000; // 60 seconds

      for (const [ws, client] of this.clients) {
        if (now - client.lastHeartbeat > timeout) {
          console.log('[CapsuleGateway] Client timed out, closing connection');
          ws.close();
          this.clients.delete(ws);
        }
      }
    }, 30000); // Check every 30 seconds
  }

  /**
   * Get connection statistics
   */
  getStatistics(): {
    totalConnections: number;
    subscriptions: { all: number; specific: number };
  } {
    let allSubscriptions = 0;
    let specificSubscriptions = 0;

    for (const client of this.clients.values()) {
      if (client.subscriptions.has('all')) {
        allSubscriptions++;
      } else {
        specificSubscriptions += client.subscriptions.size;
      }
    }

    return {
      totalConnections: this.clients.size,
      subscriptions: {
        all: allSubscriptions,
        specific: specificSubscriptions,
      },
    };
  }

  /**
   * Close server
   */
  close(): Promise<void> {
    return new Promise((resolve) => {
      console.log('[CapsuleGateway] Closing WebSocket server...');

      // Stop heartbeat checker
      if (this.heartbeatInterval) {
        clearInterval(this.heartbeatInterval);
        this.heartbeatInterval = null;
      }

      // Close all client connections
      for (const ws of this.clients.keys()) {
        ws.close();
      }
      this.clients.clear();

      // Close server
      this.wss.close(() => {
        console.log('[CapsuleGateway] WebSocket server closed');
        resolve();
      });
    });
  }
}
