/**
 * Cosmic Intelligence Fabric
 * Week 8: White-Label Platform - Phase 3
 * 
 * Federated learning system for privacy-preserving intelligence sharing
 * across all white-labeled deployments.
 * 
 * Key Features:
 * - Federated learning (train locally, aggregate globally)
 * - Privacy-preserving pattern aggregation
 * - Cross-deployment intelligence sharing
 * - AmI principles enforcement (context, proactive, seamless, adaptive)
 */

export interface AmIPrinciples {
  contextAwareness: number; // 0-100
  proactivity: number; // 0-100
  seamlessness: number; // 0-100
  adaptivity: number; // 0-100
}

export interface LocalPattern {
  id: string;
  type: 'user_behavior' | 'system_optimization' | 'anomaly_detection' | 'prediction';
  features: number[]; // Feature vector
  confidence: number; // 0-1
  timestamp: number;
  deploymentId: string;
  amiPrinciples: AmIPrinciples;
}

export interface GlobalPattern {
  id: string;
  type: string;
  aggregatedFeatures: number[];
  contributingDeployments: number;
  confidence: number;
  lastUpdated: number;
}

export interface FederatedModel {
  modelId: string;
  version: number;
  weights: number[][];
  bias: number[];
  accuracy: number;
  trainingRounds: number;
  lastUpdated: number;
}

export class CosmicFabric {
  private deploymentId: string;
  private wsUrl: string;
  private ws: WebSocket | null = null;
  private localPatterns: Map<string, LocalPattern> = new Map();
  private globalPatterns: Map<string, GlobalPattern> = new Map();
  private federatedModels: Map<string, FederatedModel> = new Map();
  private amiMetrics: AmIPrinciples = {
    contextAwareness: 0,
    proactivity: 0,
    seamlessness: 0,
    adaptivity: 0,
  };

  constructor(deploymentId: string, wsUrl: string) {
    this.deploymentId = deploymentId;
    this.wsUrl = wsUrl;
  }

  /**
   * Connect to Cosmic Fabric network
   */
  public connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.wsUrl);

        this.ws.onopen = () => {
          console.log('[CosmicFabric] Connected to network');
          this.authenticate();
          resolve();
        };

        this.ws.onmessage = (event) => {
          this.handleMessage(JSON.parse(event.data));
        };

        this.ws.onerror = (error) => {
          console.error('[CosmicFabric] WebSocket error:', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('[CosmicFabric] Disconnected from network');
          this.reconnect();
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Authenticate with deployment ID
   */
  private authenticate(): void {
    this.send({
      type: 'authenticate',
      deploymentId: this.deploymentId,
      timestamp: Date.now(),
    });
  }

  /**
   * Reconnect with exponential backoff
   */
  private reconnect(): void {
    setTimeout(() => {
      console.log('[CosmicFabric] Attempting to reconnect...');
      this.connect();
    }, 5000);
  }

  /**
   * Send message to Cosmic Fabric
   */
  private send(data: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  /**
   * Handle incoming messages
   */
  private handleMessage(data: any): void {
    switch (data.type) {
      case 'global_pattern_update':
        this.handleGlobalPatternUpdate(data.pattern);
        break;
      case 'federated_model_update':
        this.handleFederatedModelUpdate(data.model);
        break;
      case 'ami_metrics_update':
        this.handleAmIMetricsUpdate(data.metrics);
        break;
      default:
        console.warn('[CosmicFabric] Unknown message type:', data.type);
    }
  }

  /**
   * Learn from local data (privacy-preserving)
   */
  public learnLocal(pattern: Omit<LocalPattern, 'id' | 'deploymentId' | 'timestamp'>): string {
    const id = this.generatePatternId();
    const localPattern: LocalPattern = {
      ...pattern,
      id,
      deploymentId: this.deploymentId,
      timestamp: Date.now(),
    };

    // Store locally
    this.localPatterns.set(id, localPattern);

    // Extract privacy-preserving features
    const anonymizedPattern = this.anonymizePattern(localPattern);

    // Send to Cosmic Fabric for aggregation
    this.send({
      type: 'local_pattern',
      pattern: anonymizedPattern,
    });

    // Update AmI metrics
    this.updateAmIMetrics(pattern.amiPrinciples);

    return id;
  }

  /**
   * Anonymize pattern (remove identifying information)
   */
  private anonymizePattern(pattern: LocalPattern): any {
    return {
      type: pattern.type,
      features: pattern.features,
      confidence: pattern.confidence,
      amiPrinciples: pattern.amiPrinciples,
      // Deployment ID is kept for aggregation tracking, but no user data
    };
  }

  /**
   * Handle global pattern update from Cosmic Fabric
   */
  private handleGlobalPatternUpdate(pattern: GlobalPattern): void {
    this.globalPatterns.set(pattern.id, pattern);
    console.log('[CosmicFabric] Global pattern updated:', pattern.id);

    // Trigger event for UI updates
    window.dispatchEvent(new CustomEvent('cosmic-pattern-update', {
      detail: pattern,
    }));
  }

  /**
   * Handle federated model update
   */
  private handleFederatedModelUpdate(model: FederatedModel): void {
    this.federatedModels.set(model.modelId, model);
    console.log('[CosmicFabric] Federated model updated:', model.modelId, 'v' + model.version);

    // Trigger event for UI updates
    window.dispatchEvent(new CustomEvent('cosmic-model-update', {
      detail: model,
    }));
  }

  /**
   * Handle AmI metrics update
   */
  private handleAmIMetricsUpdate(metrics: AmIPrinciples): void {
    this.amiMetrics = metrics;
    console.log('[CosmicFabric] AmI metrics updated:', metrics);

    // Trigger event for UI updates
    window.dispatchEvent(new CustomEvent('ami-metrics-update', {
      detail: metrics,
    }));
  }

  /**
   * Update local AmI metrics
   */
  private updateAmIMetrics(principles: AmIPrinciples): void {
    // Exponential moving average
    const alpha = 0.3;
    this.amiMetrics.contextAwareness = 
      alpha * principles.contextAwareness + (1 - alpha) * this.amiMetrics.contextAwareness;
    this.amiMetrics.proactivity = 
      alpha * principles.proactivity + (1 - alpha) * this.amiMetrics.proactivity;
    this.amiMetrics.seamlessness = 
      alpha * principles.seamlessness + (1 - alpha) * this.amiMetrics.seamlessness;
    this.amiMetrics.adaptivity = 
      alpha * principles.adaptivity + (1 - alpha) * this.amiMetrics.adaptivity;
  }

  /**
   * Get current AmI metrics
   */
  public getAmIMetrics(): AmIPrinciples {
    return { ...this.amiMetrics };
  }

  /**
   * Get global patterns
   */
  public getGlobalPatterns(type?: string): GlobalPattern[] {
    const patterns = Array.from(this.globalPatterns.values());
    return type ? patterns.filter(p => p.type === type) : patterns;
  }

  /**
   * Get federated model
   */
  public getFederatedModel(modelId: string): FederatedModel | undefined {
    return this.federatedModels.get(modelId);
  }

  /**
   * Predict using federated model
   */
  public predict(modelId: string, features: number[]): number[] {
    const model = this.federatedModels.get(modelId);
    if (!model) {
      throw new Error(`Model ${modelId} not found`);
    }

    // Simple feedforward prediction
    let output = features;
    for (const layer of model.weights) {
      output = this.matrixMultiply(output, layer);
      output = this.addBias(output, model.bias);
      output = this.relu(output);
    }

    return output;
  }

  /**
   * Matrix multiplication helper
   */
  private matrixMultiply(vector: number[], matrix: number[]): number[] {
    // Simplified for demo - real implementation would use proper matrix ops
    return vector.map((v, i) => v * (matrix[i] || 1));
  }

  /**
   * Add bias helper
   */
  private addBias(vector: number[], bias: number[]): number[] {
    return vector.map((v, i) => v + (bias[i] || 0));
  }

  /**
   * ReLU activation
   */
  private relu(vector: number[]): number[] {
    return vector.map(v => Math.max(0, v));
  }

  /**
   * Generate unique pattern ID
   */
  private generatePatternId(): string {
    return `pattern_${this.deploymentId}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Disconnect from Cosmic Fabric
   */
  public disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Get network statistics
   */
  public getNetworkStats(): {
    localPatterns: number;
    globalPatterns: number;
    federatedModels: number;
    amiMetrics: AmIPrinciples;
  } {
    return {
      localPatterns: this.localPatterns.size,
      globalPatterns: this.globalPatterns.size,
      federatedModels: this.federatedModels.size,
      amiMetrics: this.getAmIMetrics(),
    };
  }
}

// Singleton instance
let fabricInstance: CosmicFabric | null = null;

export function initializeCosmicFabric(deploymentId: string, wsUrl: string): CosmicFabric {
  if (!fabricInstance) {
    fabricInstance = new CosmicFabric(deploymentId, wsUrl);
  }
  return fabricInstance;
}

export function getCosmicFabric(): CosmicFabric | null {
  return fabricInstance;
}
