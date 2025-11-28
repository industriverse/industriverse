import { Server as HTTPServer } from 'http';
import { Server as SocketIOServer, Socket } from 'socket.io';
import { getDb } from './db';
import { amiMetrics } from '../drizzle/schema';
import type { InsertAmiMetric } from '../drizzle/schema';

let io: SocketIOServer | null = null;

export function initializeWebSocket(httpServer: HTTPServer) {
  io = new SocketIOServer(httpServer, {
    cors: {
      origin: '*', // Configure appropriately for production
      methods: ['GET', 'POST'],
    },
    path: '/api/socket.io',
  });

  io.on('connection', (socket: Socket) => {
    console.log(`[WebSocket] Client connected: ${socket.id}`);

    // Handle tenant room subscription
    socket.on('subscribe:tenant', (tenantId: string) => {
      socket.join(`tenant:${tenantId}`);
      console.log(`[WebSocket] Client ${socket.id} subscribed to tenant: ${tenantId}`);
      
      socket.emit('subscribed', { tenantId });
    });

    // Handle deployment room subscription
    socket.on('subscribe:deployment', (deploymentId: string) => {
      socket.join(`deployment:${deploymentId}`);
      console.log(`[WebSocket] Client ${socket.id} subscribed to deployment: ${deploymentId}`);
      
      socket.emit('subscribed', { deploymentId });
    });

    // Handle unsubscribe
    socket.on('unsubscribe', (room: string) => {
      socket.leave(room);
      console.log(`[WebSocket] Client ${socket.id} unsubscribed from: ${room}`);
    });

    socket.on('disconnect', () => {
      console.log(`[WebSocket] Client disconnected: ${socket.id}`);
    });
  });

  // Start AmI metrics streaming for all active tenants
  startAmiMetricsStreaming();

  return io;
}

export function getSocketIO(): SocketIOServer | null {
  return io;
}

/**
 * Broadcast AmI metric update to all subscribers
 */
export async function broadcastAmiMetric(metric: InsertAmiMetric) {
  if (!io) return;

  const db = await getDb();
  if (!db) return;

  try {
    // Save to database
    await db.insert(amiMetrics).values(metric);

    // Broadcast to all connected clients (for aggregated views)
    io.emit('ami:metric', metric);

    // Also broadcast to specific rooms for filtered views
    io.to(`tenant:${metric.tenantId}`).emit('ami:metric', metric);

    if (metric.deploymentId) {
      io.to(`deployment:${metric.deploymentId}`).emit('ami:metric', metric);
    }

    console.log(`[WebSocket] Broadcasted AmI metric: ${metric.principle} = ${metric.value}% for tenant ${metric.tenantId}`);
  } catch (error) {
    console.error('[WebSocket] Failed to broadcast AmI metric:', error);
  }
}

/**
 * Generate and stream mock AmI metrics for demonstration
 * In production, this would be replaced with real sensor data
 */
function startAmiMetricsStreaming() {
  // Mock tenant IDs (in production, fetch from database)
  const mockTenants = [
    { tenantId: 'tsmc-fab18', deploymentId: 'tsmc-fab18-prod' },
    { tenantId: 'intel-oregon', deploymentId: 'intel-oregon-prod' },
    { tenantId: 'samsung-austin', deploymentId: 'samsung-austin-prod' },
  ];

  const principles: Array<'context' | 'proactivity' | 'seamlessness' | 'adaptivity'> = [
    'context',
    'proactivity',
    'seamlessness',
    'adaptivity',
  ];

  const baseValues = {
    context: 82,
    proactivity: 78,
    seamlessness: 94,
    adaptivity: 85,
  };

  // Generate metrics every 2 seconds
  setInterval(async () => {
    for (const tenant of mockTenants) {
      for (const principle of principles) {
        const baseValue = baseValues[principle];
        const variance = (Math.random() - 0.5) * 10;
        const value = Math.round(Math.max(0, Math.min(100, baseValue + variance)));

        const metric: InsertAmiMetric = {
          tenantId: tenant.tenantId,
          deploymentId: tenant.deploymentId,
          principle,
          value,
          timestamp: new Date(),
        };

        await broadcastAmiMetric(metric);
      }
    }
  }, 2000);

  console.log('[WebSocket] AmI metrics streaming started');
}

/**
 * Broadcast custom event to tenant
 */
export function broadcastToTenant(tenantId: string, event: string, data: any) {
  if (!io) return;
  io.to(`tenant:${tenantId}`).emit(event, data);
}

/**
 * Broadcast custom event to deployment
 */
export function broadcastToDeployment(deploymentId: string, event: string, data: any) {
  if (!io) return;
  io.to(`deployment:${deploymentId}`).emit(event, data);
}
