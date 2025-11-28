/**
 * OPC-UA Sensor Adapter
 * 
 * Connects to OPC-UA servers (PLCs) and monitors node values
 */

import {
  OPCUAClient,
  MessageSecurityMode,
  SecurityPolicy,
  AttributeIds,
  ClientSubscription,
  ClientMonitoredItem,
  DataValue,
  type UserIdentityInfo,
} from 'node-opcua';
import type { OPCUASensorConfig, SensorReading } from '../types/sensor';

export class OPCUAAdapter {
  private client: OPCUAClient | null = null;
  private subscription: ClientSubscription | null = null;
  private monitoredItems: Map<string, ClientMonitoredItem> = new Map();
  private config: OPCUASensorConfig;
  private onReading: (reading: SensorReading) => void;
  private onError: (error: Error) => void;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectTimer: NodeJS.Timeout | null = null;

  constructor(
    config: OPCUASensorConfig,
    onReading: (reading: SensorReading) => void,
    onError: (error: Error) => void
  ) {
    this.config = config;
    this.onReading = onReading;
    this.onError = onError;
  }

  /**
   * Connect to OPC-UA server and create subscription
   */
  async connect(): Promise<void> {
    try {
      console.log(`[OPCUAAdapter] Connecting to ${this.config.endpoint}...`);

      // Create client
      this.client = OPCUAClient.create({
        applicationName: 'DAC Factory',
        connectionStrategy: {
          initialDelay: 1000,
          maxRetry: this.maxReconnectAttempts,
        },
        securityMode: MessageSecurityMode.None,
        securityPolicy: SecurityPolicy.None,
        endpointMustExist: false,
      });

      // Handle connection events
      this.client.on('backoff', (retry, delay) => {
        console.log(`[OPCUAAdapter] Backoff: retry ${retry}, delay ${delay}ms`);
      });

      this.client.on('connection_lost', () => {
        console.warn(`[OPCUAAdapter] Connection lost`);
        this.handleConnectionLost();
      });

      this.client.on('connection_reestablished', () => {
        console.log(`[OPCUAAdapter] Connection reestablished`);
        this.reconnectAttempts = 0;
      });

      // Connect to server
      await this.client.connect(this.config.endpoint);
      console.log(`[OPCUAAdapter] Connected to ${this.config.endpoint}`);

      // Create session
      const userIdentity: UserIdentityInfo = this.config.credentials
        ? {
            type: 1, // UserNameIdentityToken
            userName: this.config.credentials.username,
            password: this.config.credentials.password,
          }
        : { type: 0 }; // Anonymous

      const session = await this.client.createSession(userIdentity);
      console.log(`[OPCUAAdapter] Session created`);

      // Create subscription
      this.subscription = await session.createSubscription2({
        requestedPublishingInterval: this.config.samplingInterval ?? 1000,
        requestedLifetimeCount: 100,
        requestedMaxKeepAliveCount: 10,
        maxNotificationsPerPublish: 100,
        publishingEnabled: true,
        priority: 10,
      });

      console.log(`[OPCUAAdapter] Subscription created`);

      // Monitor node IDs
      await this.monitorNodeIds();

      this.reconnectAttempts = 0;

    } catch (error) {
      console.error(`[OPCUAAdapter] Failed to connect:`, error);
      this.onError(error as Error);
      this.handleConnectionLost();
      throw error;
    }
  }

  /**
   * Monitor configured node IDs
   */
  private async monitorNodeIds(): Promise<void> {
    if (!this.subscription) {
      console.error(`[OPCUAAdapter] Subscription not initialized`);
      return;
    }

    for (const nodeId of this.config.nodeIds) {
      try {
        const monitoredItem = await this.subscription.monitor(
          {
            nodeId,
            attributeId: AttributeIds.Value,
          },
          {
            samplingInterval: this.config.samplingInterval ?? 1000,
            discardOldest: true,
            queueSize: 10,
          }
        );

        // Handle value changes
        monitoredItem.on('changed', (dataValue: DataValue) => {
          this.handleValueChange(nodeId, dataValue);
        });

        // Handle errors
        monitoredItem.on('err', (error: Error) => {
          console.error(`[OPCUAAdapter] Error monitoring ${nodeId}:`, error);
          this.onError(error);
        });

        this.monitoredItems.set(nodeId, monitoredItem);
        console.log(`[OPCUAAdapter] Monitoring ${nodeId}`);

      } catch (error) {
        console.error(`[OPCUAAdapter] Failed to monitor ${nodeId}:`, error);
        this.onError(error as Error);
      }
    }
  }

  /**
   * Handle value change from monitored node
   */
  private handleValueChange(nodeId: string, dataValue: DataValue): void {
    try {
      // Find mapping for this node ID
      const mappingKey = Object.entries(this.config.dataMapping).find(
        ([_, path]) => path === nodeId
      )?.[0];

      if (!mappingKey) {
        console.warn(`[OPCUAAdapter] No mapping found for node ${nodeId}`);
        return;
      }

      // Extract value
      const value = dataValue.value.value;

      // Create sensor reading
      const reading: SensorReading = {
        sensorId: this.config.id,
        timestamp: dataValue.sourceTimestamp || new Date(),
        data: {
          [mappingKey]: value,
        },
        raw: {
          nodeId,
          statusCode: dataValue.statusCode.value,
          sourceTimestamp: dataValue.sourceTimestamp,
          serverTimestamp: dataValue.serverTimestamp,
        },
      };

      // Emit reading
      this.onReading(reading);

    } catch (error) {
      console.error(`[OPCUAAdapter] Failed to handle value change:`, error);
      this.onError(error as Error);
    }
  }

  /**
   * Handle connection lost
   */
  private handleConnectionLost(): void {
    this.reconnectAttempts++;
    
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error(`[OPCUAAdapter] Max reconnect attempts reached`);
      this.onError(new Error('Max reconnect attempts reached'));
      return;
    }

    // Attempt reconnection after delay
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    console.log(`[OPCUAAdapter] Reconnecting in ${delay}ms... (attempt ${this.reconnectAttempts})`);

    this.reconnectTimer = setTimeout(() => {
      this.connect().catch((error) => {
        console.error(`[OPCUAAdapter] Reconnection failed:`, error);
      });
    }, delay);
  }

  /**
   * Disconnect from OPC-UA server
   */
  async disconnect(): Promise<void> {
    try {
      console.log(`[OPCUAAdapter] Disconnecting from ${this.config.endpoint}...`);

      // Clear reconnect timer
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer);
        this.reconnectTimer = null;
      }

      // Terminate monitored items
      for (const [nodeId, item] of this.monitoredItems) {
        try {
          await item.terminate();
          console.log(`[OPCUAAdapter] Terminated monitoring for ${nodeId}`);
        } catch (error) {
          console.error(`[OPCUAAdapter] Failed to terminate ${nodeId}:`, error);
        }
      }
      this.monitoredItems.clear();

      // Delete subscription
      if (this.subscription) {
        try {
          await this.subscription.terminate();
          console.log(`[OPCUAAdapter] Subscription terminated`);
        } catch (error) {
          console.error(`[OPCUAAdapter] Failed to terminate subscription:`, error);
        }
        this.subscription = null;
      }

      // Close session and disconnect
      if (this.client) {
        try {
          await this.client.disconnect();
          console.log(`[OPCUAAdapter] Disconnected`);
        } catch (error) {
          console.error(`[OPCUAAdapter] Failed to disconnect:`, error);
        }
        this.client = null;
      }

    } catch (error) {
      console.error(`[OPCUAAdapter] Error during disconnect:`, error);
      throw error;
    }
  }

  /**
   * Check if adapter is connected
   */
  isConnected(): boolean {
    return this.client !== null && this.subscription !== null;
  }

  /**
   * Read node value (one-time read)
   */
  async readNodeValue(nodeId: string): Promise<any> {
    if (!this.client) {
      throw new Error('OPC-UA client not connected');
    }

    const session = this.client.getSession();
    if (!session) {
      throw new Error('No active session');
    }

    const dataValue = await session.read({
      nodeId,
      attributeId: AttributeIds.Value,
    });

    return dataValue.value.value;
  }

  /**
   * Write node value (for control/testing)
   */
  async writeNodeValue(nodeId: string, value: any): Promise<void> {
    if (!this.client) {
      throw new Error('OPC-UA client not connected');
    }

    const session = this.client.getSession();
    if (!session) {
      throw new Error('No active session');
    }

    await session.write({
      nodeId,
      attributeId: AttributeIds.Value,
      value: {
        value: {
          dataType: 'Double', // Adjust based on actual data type
          value,
        },
      },
    });
  }
}
