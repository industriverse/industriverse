/**
 * Sensor Ingestion Service
 * 
 * Coordinates all sensor adapters and forwards readings to Capsule Creation Engine
 */

import { MQTTAdapter } from '../adapters/MQTTAdapter';
import type {
  SensorConfig,
  MQTTSensorConfig,
  SensorReading,
  SensorStatus,
} from '../types/sensor';

type SensorAdapter = MQTTAdapter; // Add OPCUAAdapter when TypeScript issues are resolved

export class SensorIngestionService {
  private adapters: Map<string, SensorAdapter> = new Map();
  private sensorConfigs: Map<string, SensorConfig> = new Map();
  private onReading: (reading: SensorReading) => void;
  private onError: (sensorId: string, error: Error) => void;
  private onStatusChange: (sensorId: string, status: SensorStatus) => void;

  constructor(
    onReading: (reading: SensorReading) => void,
    onError: (sensorId: string, error: Error) => void,
    onStatusChange: (sensorId: string, status: SensorStatus) => void
  ) {
    this.onReading = onReading;
    this.onError = onError;
    this.onStatusChange = onStatusChange;
  }

  /**
   * Add sensor configuration and start ingestion
   */
  async addSensor(config: SensorConfig): Promise<void> {
    try {
      console.log(`[SensorIngestion] Adding sensor: ${config.name} (${config.protocol})`);

      // Store config
      this.sensorConfigs.set(config.id, config);

      // Update status to connecting
      this.onStatusChange(config.id, 'connecting');

      // Create appropriate adapter
      const adapter = await this.createAdapter(config);

      // Store adapter
      this.adapters.set(config.id, adapter);

      // Connect adapter
      await adapter.connect();

      // Update status to active
      this.onStatusChange(config.id, 'active');

      console.log(`[SensorIngestion] Sensor ${config.name} connected successfully`);

    } catch (error) {
      console.error(`[SensorIngestion] Failed to add sensor ${config.name}:`, error);
      this.onStatusChange(config.id, 'error');
      this.onError(config.id, error as Error);
      throw error;
    }
  }

  /**
   * Create adapter based on protocol
   */
  private async createAdapter(config: SensorConfig): Promise<SensorAdapter> {
    switch (config.protocol) {
      case 'mqtt':
        return new MQTTAdapter(
          config as MQTTSensorConfig,
          (reading) => this.handleReading(reading),
          (error) => this.handleAdapterError(config.id, error)
        );

      // case 'opcua':
      //   return new OPCUAAdapter(
      //     config as OPCUASensorConfig,
      //     (reading) => this.handleReading(reading),
      //     (error) => this.handleAdapterError(config.id, error)
      //   );

      default:
        throw new Error(`Unsupported protocol: ${config.protocol}`);
    }
  }

  /**
   * Handle sensor reading from adapter
   */
  private handleReading(reading: SensorReading): void {
    try {
      console.log(`[SensorIngestion] Reading from ${reading.sensorId}:`, reading.data);

      // Update last reading timestamp
      const config = this.sensorConfigs.get(reading.sensorId);
      if (config) {
        config.lastReadingAt = reading.timestamp;
      }

      // Forward to callback
      this.onReading(reading);

    } catch (error) {
      console.error(`[SensorIngestion] Failed to handle reading:`, error);
      this.onError(reading.sensorId, error as Error);
    }
  }

  /**
   * Handle adapter error
   */
  private handleAdapterError(sensorId: string, error: Error): void {
    console.error(`[SensorIngestion] Adapter error for ${sensorId}:`, error);
    this.onStatusChange(sensorId, 'error');
    this.onError(sensorId, error);
  }

  /**
   * Remove sensor and stop ingestion
   */
  async removeSensor(sensorId: string): Promise<void> {
    try {
      console.log(`[SensorIngestion] Removing sensor: ${sensorId}`);

      const adapter = this.adapters.get(sensorId);
      if (adapter) {
        await adapter.disconnect();
        this.adapters.delete(sensorId);
      }

      this.sensorConfigs.delete(sensorId);

      this.onStatusChange(sensorId, 'inactive');

      console.log(`[SensorIngestion] Sensor ${sensorId} removed`);

    } catch (error) {
      console.error(`[SensorIngestion] Failed to remove sensor ${sensorId}:`, error);
      throw error;
    }
  }

  /**
   * Get sensor status
   */
  getSensorStatus(sensorId: string): SensorStatus {
    const adapter = this.adapters.get(sensorId);
    if (!adapter) {
      return 'inactive';
    }

    return adapter.isConnected() ? 'active' : 'error';
  }

  /**
   * Get all sensor configurations
   */
  getAllSensors(): SensorConfig[] {
    return Array.from(this.sensorConfigs.values());
  }

  /**
   * Get sensor configuration by ID
   */
  getSensor(sensorId: string): SensorConfig | undefined {
    return this.sensorConfigs.get(sensorId);
  }

  /**
   * Update sensor configuration
   */
  async updateSensor(sensorId: string, updates: Partial<SensorConfig>): Promise<void> {
    const config = this.sensorConfigs.get(sensorId);
    if (!config) {
      throw new Error(`Sensor ${sensorId} not found`);
    }

    // Remove old adapter
    await this.removeSensor(sensorId);

    // Update config
    const updatedConfig = { ...config, ...updates };

    // Add new adapter
    await this.addSensor(updatedConfig);
  }

  /**
   * Stop all sensors
   */
  async stopAll(): Promise<void> {
    console.log(`[SensorIngestion] Stopping all sensors...`);

    const promises = Array.from(this.adapters.keys()).map((sensorId) =>
      this.removeSensor(sensorId)
    );

    await Promise.all(promises);

    console.log(`[SensorIngestion] All sensors stopped`);
  }

  /**
   * Get ingestion statistics
   */
  getStatistics(): {
    totalSensors: number;
    activeSensors: number;
    errorSensors: number;
    inactiveSensors: number;
  } {
    const sensors = this.getAllSensors();
    
    return {
      totalSensors: sensors.length,
      activeSensors: sensors.filter((s) => this.getSensorStatus(s.id) === 'active').length,
      errorSensors: sensors.filter((s) => this.getSensorStatus(s.id) === 'error').length,
      inactiveSensors: sensors.filter((s) => this.getSensorStatus(s.id) === 'inactive').length,
    };
  }
}
