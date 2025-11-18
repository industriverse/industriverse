/**
 * Capsule Creation Engine
 * 
 * Transforms sensor readings into actionable capsules using rules
 */

import type { SensorReading } from '../types/sensor';
// Using client types for now - should be moved to shared/types
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

export interface CapsuleRule {
  id: string;
  name: string;
  enabled: boolean;
  condition: {
    sensorId: string;
    metric: string; // e.g., 'temperature', 'pressure', 'vibration'
    operator: '>' | '<' | '==' | '!=' | '>=' | '<=';
    threshold: number;
    timeWindow?: number; // seconds - for time-based conditions
  };
  capsule: {
    title: string;
    description: string;
    status: 'active' | 'warning' | 'critical';
    priority: 'low' | 'medium' | 'high' | 'critical';
    category: string;
    actions: string[]; // Available actions
    metadata?: Record<string, any>;
  };
}

export class CapsuleCreationEngine {
  private rules: Map<string, CapsuleRule> = new Map();
  private sensorHistory: Map<string, SensorReading[]> = new Map();
  private activeCapsules: Map<string, CapsuleData> = new Map();
  private onCapsuleCreated: (capsule: CapsuleData) => void;
  private onCapsuleUpdated: (capsuleId: string, updates: Partial<CapsuleData>) => void;

  constructor(
    onCapsuleCreated: (capsule: CapsuleData) => void,
    onCapsuleUpdated: (capsuleId: string, updates: Partial<CapsuleData>) => void
  ) {
    this.onCapsuleCreated = onCapsuleCreated;
    this.onCapsuleUpdated = onCapsuleUpdated;
  }

  /**
   * Add capsule creation rule
   */
  addRule(rule: CapsuleRule): void {
    console.log(`[CapsuleEngine] Adding rule: ${rule.name}`);
    this.rules.set(rule.id, rule);
  }

  /**
   * Remove capsule creation rule
   */
  removeRule(ruleId: string): void {
    console.log(`[CapsuleEngine] Removing rule: ${ruleId}`);
    this.rules.delete(ruleId);
  }

  /**
   * Get all rules
   */
  getRules(): CapsuleRule[] {
    return Array.from(this.rules.values());
  }

  /**
   * Get rule by ID
   */
  getRule(ruleId: string): CapsuleRule | undefined {
    return this.rules.get(ruleId);
  }

  /**
   * Update rule
   */
  updateRule(ruleId: string, updates: Partial<CapsuleRule>): void {
    const rule = this.rules.get(ruleId);
    if (!rule) {
      throw new Error(`Rule ${ruleId} not found`);
    }

    const updatedRule = { ...rule, ...updates };
    this.rules.set(ruleId, updatedRule);
    console.log(`[CapsuleEngine] Updated rule: ${rule.name}`);
  }

  /**
   * Process sensor reading and evaluate rules
   */
  processSensorReading(reading: SensorReading): void {
    try {
      // Store reading in history
      this.storeSensorReading(reading);

      // Evaluate all rules for this sensor
      for (const rule of this.rules.values()) {
        if (!rule.enabled) {
          continue;
        }

        if (rule.condition.sensorId === reading.sensorId) {
          this.evaluateRule(rule, reading);
        }
      }

    } catch (error) {
      console.error(`[CapsuleEngine] Failed to process reading:`, error);
    }
  }

  /**
   * Store sensor reading in history
   */
  private storeSensorReading(reading: SensorReading): void {
    const history = this.sensorHistory.get(reading.sensorId) || [];
    history.push(reading);

    // Keep only last 1000 readings per sensor
    if (history.length > 1000) {
      history.shift();
    }

    this.sensorHistory.set(reading.sensorId, history);
  }

  /**
   * Evaluate rule against sensor reading
   */
  private evaluateRule(rule: CapsuleRule, reading: SensorReading): void {
    try {
      // Get metric value from reading
      const metricValue = reading.data[rule.condition.metric];
      
      if (metricValue === undefined) {
        return; // Metric not present in this reading
      }

      // Convert to number if needed
      const numericValue = typeof metricValue === 'number' 
        ? metricValue 
        : parseFloat(String(metricValue));

      if (isNaN(numericValue)) {
        console.warn(`[CapsuleEngine] Invalid numeric value for ${rule.condition.metric}: ${metricValue}`);
        return;
      }

      // Evaluate condition
      const conditionMet = this.evaluateCondition(
        numericValue,
        rule.condition.operator,
        rule.condition.threshold
      );

      if (conditionMet) {
        console.log(`[CapsuleEngine] Rule triggered: ${rule.name}`);
        this.createOrUpdateCapsule(rule, reading, numericValue);
      }

    } catch (error) {
      console.error(`[CapsuleEngine] Failed to evaluate rule ${rule.name}:`, error);
    }
  }

  /**
   * Evaluate condition operator
   */
  private evaluateCondition(value: number, operator: string, threshold: number): boolean {
    switch (operator) {
      case '>':
        return value > threshold;
      case '<':
        return value < threshold;
      case '==':
        return value === threshold;
      case '!=':
        return value !== threshold;
      case '>=':
        return value >= threshold;
      case '<=':
        return value <= threshold;
      default:
        console.warn(`[CapsuleEngine] Unknown operator: ${operator}`);
        return false;
    }
  }

  /**
   * Create or update capsule based on rule
   */
  private createOrUpdateCapsule(rule: CapsuleRule, reading: SensorReading, metricValue: number): void {
    // Check if capsule already exists for this rule
    const existingCapsule = this.findCapsuleByRule(rule.id);

    if (existingCapsule) {
      // Update existing capsule
      const updates: Partial<CapsuleData> = {
        metrics: {
          ...existingCapsule.metrics,
          [rule.condition.metric]: metricValue,
          timestamp: reading.timestamp.toISOString(),
        },
        updatedAt: new Date().toISOString(),
      };

      this.activeCapsules.set(existingCapsule.id, {
        ...existingCapsule,
        ...updates,
      });

      this.onCapsuleUpdated(existingCapsule.id, updates);
      console.log(`[CapsuleEngine] Updated capsule: ${existingCapsule.title}`);

    } else {
      // Create new capsule
      const capsule: CapsuleData = {
        id: `capsule_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        title: this.interpolateTemplate(rule.capsule.title, { metricValue, reading }),
        description: this.interpolateTemplate(rule.capsule.description, { metricValue, reading }),
        status: rule.capsule.status,
        priority: rule.capsule.priority,
        category: rule.capsule.category,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        actions: rule.capsule.actions,
        metrics: {
          [rule.condition.metric]: metricValue,
          sensorId: reading.sensorId,
          ruleId: rule.id,
          timestamp: reading.timestamp.toISOString(),
        },
        metadata: {
          ...rule.capsule.metadata,
          ruleId: rule.id,
          ruleName: rule.name,
          sensorId: reading.sensorId,
        },
      };

      this.activeCapsules.set(capsule.id, capsule);
      this.onCapsuleCreated(capsule);
      console.log(`[CapsuleEngine] Created capsule: ${capsule.title}`);
    }
  }

  /**
   * Find capsule created by specific rule
   */
  private findCapsuleByRule(ruleId: string): CapsuleData | undefined {
    return Array.from(this.activeCapsules.values()).find(
      (capsule) => capsule.metadata?.ruleId === ruleId
    );
  }

  /**
   * Interpolate template string with variables
   */
  private interpolateTemplate(
    template: string,
    vars: { metricValue: number; reading: SensorReading }
  ): string {
    return template
      .replace(/\{metricValue\}/g, vars.metricValue.toFixed(2))
      .replace(/\{sensorId\}/g, vars.reading.sensorId)
      .replace(/\{timestamp\}/g, vars.reading.timestamp.toISOString());
  }

  /**
   * Resolve capsule (remove from active list)
   */
  resolveCapsule(capsuleId: string): void {
    this.activeCapsules.delete(capsuleId);
    console.log(`[CapsuleEngine] Resolved capsule: ${capsuleId}`);
  }

  /**
   * Get all active capsules
   */
  getActiveCapsules(): CapsuleData[] {
    return Array.from(this.activeCapsules.values());
  }

  /**
   * Get capsule by ID
   */
  getCapsule(capsuleId: string): CapsuleData | undefined {
    return this.activeCapsules.get(capsuleId);
  }

  /**
   * Get statistics
   */
  getStatistics(): {
    totalRules: number;
    enabledRules: number;
    activeCapsules: number;
    capsulesByStatus: Record<string, number>;
  } {
    const capsules = this.getActiveCapsules();
    
    const capsulesByStatus: Record<string, number> = {};
    for (const capsule of capsules) {
      capsulesByStatus[capsule.status] = (capsulesByStatus[capsule.status] || 0) + 1;
    }

    return {
      totalRules: this.rules.size,
      enabledRules: Array.from(this.rules.values()).filter((r) => r.enabled).length,
      activeCapsules: capsules.length,
      capsulesByStatus,
    };
  }

  /**
   * Load default rules
   */
  loadDefaultRules(): void {
    // Temperature threshold rule
    this.addRule({
      id: 'temp_critical',
      name: 'Motor Overheating',
      enabled: true,
      condition: {
        sensorId: 'motor_001',
        metric: 'temperature',
        operator: '>',
        threshold: 80,
      },
      capsule: {
        title: 'Motor 001 Overheating',
        description: 'Temperature exceeded 80°C (current: {metricValue}°C)',
        status: 'critical',
        priority: 'critical',
        category: 'equipment_health',
        actions: ['acknowledge', 'mitigate', 'inspect', 'escalate'],
        metadata: {
          equipmentId: 'motor_001',
          location: 'Assembly Line 3',
        },
      },
    });

    // Pressure warning rule
    this.addRule({
      id: 'pressure_warning',
      name: 'High Pressure Alert',
      enabled: true,
      condition: {
        sensorId: 'pressure_sensor_001',
        metric: 'pressure',
        operator: '>',
        threshold: 85,
      },
      capsule: {
        title: 'High Pressure Detected',
        description: 'Pressure exceeded 85 PSI (current: {metricValue} PSI)',
        status: 'warning',
        priority: 'high',
        category: 'safety',
        actions: ['acknowledge', 'inspect', 'dismiss'],
        metadata: {
          equipmentId: 'compressor_001',
          location: 'Compressor Room',
        },
      },
    });

    // Vibration anomaly rule
    this.addRule({
      id: 'vibration_anomaly',
      name: 'Abnormal Vibration',
      enabled: true,
      condition: {
        sensorId: 'vibration_sensor_001',
        metric: 'vibration',
        operator: '>',
        threshold: 70,
      },
      capsule: {
        title: 'Abnormal Vibration Detected',
        description: 'Vibration level exceeded 70 Hz (current: {metricValue} Hz)',
        status: 'warning',
        priority: 'high',
        category: 'predictive_maintenance',
        actions: ['acknowledge', 'inspect', 'schedule_maintenance'],
        metadata: {
          equipmentId: 'motor_001',
          location: 'Assembly Line 3',
        },
      },
    });

    console.log(`[CapsuleEngine] Loaded ${this.rules.size} default rules`);
  }
}
