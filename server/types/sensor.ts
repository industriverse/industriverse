/**
 * Sensor Configuration Types
 * 
 * Defines types for factory sensor integration (MQTT, OPC-UA, HTTP)
 */

export type SensorProtocol = 'mqtt' | 'opcua' | 'modbus' | 'http';

export type SensorStatus = 'active' | 'inactive' | 'error' | 'connecting';

export interface SensorCredentials {
  username?: string;
  password?: string;
  certificate?: string;
  privateKey?: string;
}

export interface SensorDataMapping {
  temperature?: string;
  pressure?: string;
  vibration?: string;
  humidity?: string;
  power?: string;
  speed?: string;
  [key: string]: string | undefined;
}

export interface SensorConfig {
  id: string;
  name: string;
  protocol: SensorProtocol;
  endpoint: string;
  credentials?: SensorCredentials;
  pollInterval?: number; // seconds (for HTTP polling)
  dataMapping: SensorDataMapping;
  status: SensorStatus;
  lastReadingAt?: Date;
  metadata?: Record<string, any>;
}

export interface SensorReading {
  sensorId: string;
  timestamp: Date;
  data: Record<string, number | string | boolean>;
  raw?: any; // Raw sensor data
}

export interface MQTTSensorConfig extends SensorConfig {
  protocol: 'mqtt';
  endpoint: string; // mqtt://broker.example.com:1883
  topics: string[]; // MQTT topics to subscribe to
  qos?: 0 | 1 | 2; // Quality of Service
}

export interface OPCUASensorConfig extends SensorConfig {
  protocol: 'opcua';
  endpoint: string; // opc.tcp://plc.example.com:4840
  nodeIds: string[]; // OPC-UA node IDs to monitor
  samplingInterval?: number; // milliseconds
}

export interface HTTPSensorConfig extends SensorConfig {
  protocol: 'http';
  endpoint: string; // https://api.example.com/sensor/data
  method: 'GET' | 'POST';
  headers?: Record<string, string>;
  body?: any;
  pollInterval: number; // Required for HTTP
}

export interface ModbusSensorConfig extends SensorConfig {
  protocol: 'modbus';
  endpoint: string; // modbus://device.example.com:502
  slaveId: number;
  registers: {
    address: number;
    type: 'coil' | 'discrete' | 'holding' | 'input';
    length: number;
    name: string;
  }[];
}
