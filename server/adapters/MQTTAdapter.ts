/**
 * MQTT Sensor Adapter
 * 
 * Connects to MQTT brokers and subscribes to sensor topics
 */

import mqtt, { type MqttClient } from 'mqtt';
import type { MQTTSensorConfig, SensorReading } from '../types/sensor';

export class MQTTAdapter {
  private client: MqttClient | null = null;
  private config: MQTTSensorConfig;
  private onReading: (reading: SensorReading) => void;
  private onError: (error: Error) => void;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;

  constructor(
    config: MQTTSensorConfig,
    onReading: (reading: SensorReading) => void,
    onError: (error: Error) => void
  ) {
    this.config = config;
    this.onReading = onReading;
    this.onError = onError;
  }

  /**
   * Connect to MQTT broker and subscribe to topics
   */
  async connect(): Promise<void> {
    try {
      const options: mqtt.IClientOptions = {
        clientId: `dac-factory-${this.config.id}-${Date.now()}`,
        clean: true,
        reconnectPeriod: 5000,
        connectTimeout: 30000,
      };

      // Add credentials if provided
      if (this.config.credentials) {
        options.username = this.config.credentials.username;
        options.password = this.config.credentials.password;
      }

      console.log(`[MQTTAdapter] Connecting to ${this.config.endpoint}...`);
      
      this.client = mqtt.connect(this.config.endpoint, options);

      // Handle connection events
      this.client.on('connect', () => {
        console.log(`[MQTTAdapter] Connected to ${this.config.endpoint}`);
        this.reconnectAttempts = 0;
        this.subscribeToTopics();
      });

      this.client.on('error', (error) => {
        console.error(`[MQTTAdapter] Connection error:`, error);
        this.onError(error);
      });

      this.client.on('reconnect', () => {
        this.reconnectAttempts++;
        console.log(`[MQTTAdapter] Reconnecting... (attempt ${this.reconnectAttempts})`);
        
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
          console.error(`[MQTTAdapter] Max reconnect attempts reached`);
          this.disconnect();
          this.onError(new Error('Max reconnect attempts reached'));
        }
      });

      this.client.on('offline', () => {
        console.warn(`[MQTTAdapter] Client offline`);
      });

      this.client.on('message', (topic, message) => {
        this.handleMessage(topic, message);
      });

    } catch (error) {
      console.error(`[MQTTAdapter] Failed to connect:`, error);
      this.onError(error as Error);
      throw error;
    }
  }

  /**
   * Subscribe to configured topics
   */
  private subscribeToTopics(): void {
    if (!this.client) {
      console.error(`[MQTTAdapter] Client not initialized`);
      return;
    }

    const qos = this.config.qos ?? 1;

    this.config.topics.forEach((topic) => {
      this.client!.subscribe(topic, { qos }, (error) => {
        if (error) {
          console.error(`[MQTTAdapter] Failed to subscribe to ${topic}:`, error);
          this.onError(error);
        } else {
          console.log(`[MQTTAdapter] Subscribed to ${topic} (QoS ${qos})`);
        }
      });
    });
  }

  /**
   * Handle incoming MQTT message
   */
  private handleMessage(topic: string, message: Buffer): void {
    try {
      // Parse message (assume JSON format)
      const payload = JSON.parse(message.toString());
      
      // Map payload to sensor reading using dataMapping
      const data: Record<string, number | string | boolean> = {};
      
      for (const [key, path] of Object.entries(this.config.dataMapping)) {
        if (path) {
          // Support nested paths (e.g., "sensors.temperature")
          const value = this.getNestedValue(payload, path);
          if (value !== undefined) {
            data[key] = value;
          }
        }
      }

      // Create sensor reading
      const reading: SensorReading = {
        sensorId: this.config.id,
        timestamp: new Date(),
        data,
        raw: payload,
      };

      // Emit reading
      this.onReading(reading);

    } catch (error) {
      console.error(`[MQTTAdapter] Failed to parse message from ${topic}:`, error);
      this.onError(error as Error);
    }
  }

  /**
   * Get nested value from object using dot notation
   */
  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  }

  /**
   * Disconnect from MQTT broker
   */
  async disconnect(): Promise<void> {
    if (this.client) {
      console.log(`[MQTTAdapter] Disconnecting from ${this.config.endpoint}...`);
      
      return new Promise((resolve) => {
        this.client!.end(false, {}, () => {
          console.log(`[MQTTAdapter] Disconnected`);
          this.client = null;
          resolve();
        });
      });
    }
  }

  /**
   * Check if adapter is connected
   */
  isConnected(): boolean {
    return this.client?.connected ?? false;
  }

  /**
   * Publish message to topic (for testing/control)
   */
  async publish(topic: string, message: string | Buffer, qos: 0 | 1 | 2 = 1): Promise<void> {
    if (!this.client || !this.client.connected) {
      throw new Error('MQTT client not connected');
    }

    return new Promise((resolve, reject) => {
      this.client!.publish(topic, message, { qos }, (error) => {
        if (error) {
          reject(error);
        } else {
          resolve();
        }
      });
    });
  }
}
