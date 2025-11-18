/**
 * Shadow Twin Consensus Client (TypeScript)
 * 
 * Browser-based distributed consensus validation
 * Ported from Python implementation (shadow_twin_consensus_client_v3.py)
 */

export interface Hypothesis {
  hypothesis_id: string;
  content: string;
  capsule_id?: string;
  metadata?: Record<string, any>;
}

export interface Prediction {
  predictor_id: string;
  predictor_name: string;
  validity_score: number;
  confidence: number;
  weight: number;
  status: 'success' | 'error';
  error?: string;
}

export interface ConsensusResult {
  consensus: boolean;
  pct: number; // Probability of Consensus Truth
  weighted_score: number;
  avg_score: number;
  predictions: Prediction[];
  timestamp: string;
  reason?: string;
}

interface Predictor {
  name: string;
  url: string;
  namespace: string;
  weight: number;
  enabled: boolean;
}

export class ShadowTwinConsensusClient {
  private predictors: Record<string, Predictor>;
  private pctThreshold: number;
  private validityThreshold: number;

  constructor() {
    // Configure predictors (can be overridden via config)
    this.predictors = {
      primary: {
        name: 'integration-bridge',
        url: '/api/shadow-twin/predict', // Proxied through our backend
        namespace: 'shadow-twin-integration',
        weight: 1.5,
        enabled: true,
      },
      controller: {
        name: 'shadow-twin-controller',
        url: '/api/shadow-twin/controller', // Proxied through our backend
        namespace: 'capsule-dna-registry',
        weight: 0.8,
        enabled: true,
      },
    };

    this.pctThreshold = 0.90; // 90% consensus required
    this.validityThreshold = 0.75; // 75% validity score required
  }

  /**
   * Predict hypothesis validity using distributed consensus
   */
  async predictHypothesisValidity(hypothesis: Hypothesis): Promise<ConsensusResult> {
    console.log('[ShadowTwinConsensus] Starting prediction for:', hypothesis.hypothesis_id);

    const predictions: Prediction[] = [];

    // Query all enabled predictors in parallel
    const predictorPromises = Object.entries(this.predictors)
      .filter(([_, predictor]) => predictor.enabled)
      .map(([id, predictor]) => this.queryPredictor(id, predictor, hypothesis));

    const results = await Promise.allSettled(predictorPromises);

    // Collect successful predictions
    results.forEach((result, index) => {
      if (result.status === 'fulfilled' && result.value) {
        predictions.push(result.value);
      }
    });

    // Check if we have enough predictors
    if (predictions.length < 2) {
      console.warn('[ShadowTwinConsensus] Insufficient predictors responded');
      return {
        consensus: false,
        pct: 0.0,
        weighted_score: 0.0,
        avg_score: 0.0,
        predictions,
        timestamp: new Date().toISOString(),
        reason: 'Insufficient predictors responded',
      };
    }

    // Calculate consensus metrics
    const scores = predictions.map((p) => p.validity_score);
    const weights = predictions.map((p) => p.weight);

    const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
    const variance = scores.reduce((sum, score) => sum + Math.pow(score - avgScore, 2), 0) / scores.length;
    const stdev = Math.sqrt(variance);

    const weightedScore =
      scores.reduce((sum, score, i) => sum + score * weights[i], 0) /
      weights.reduce((a, b) => a + b, 0);

    // Calculate PCT (Probability of Consensus Truth)
    // PCT = 1 - (standard_deviation / mean)
    const pct = avgScore > 0 ? Math.max(0, Math.min(1, 1.0 - stdev / avgScore)) : 0.0;

    // Determine consensus
    const consensus = pct >= this.pctThreshold && weightedScore >= this.validityThreshold;

    console.log('[ShadowTwinConsensus] Results:', {
      pct: pct.toFixed(3),
      weighted_score: weightedScore.toFixed(3),
      consensus: consensus ? 'APPROVED' : 'REJECTED',
    });

    return {
      consensus,
      pct,
      weighted_score: weightedScore,
      avg_score: avgScore,
      predictions,
      timestamp: new Date().toISOString(),
      reason: consensus
        ? 'Consensus reached'
        : `PCT ${pct.toFixed(3)} < ${this.pctThreshold} or Score ${weightedScore.toFixed(3)} < ${this.validityThreshold}`,
    };
  }

  /**
   * Query a single predictor
   */
  private async queryPredictor(
    id: string,
    predictor: Predictor,
    hypothesis: Hypothesis
  ): Promise<Prediction | null> {
    console.log(`[ShadowTwinConsensus] Querying ${predictor.name}...`);

    try {
      const response = await fetch(predictor.url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(hypothesis),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();

      // Extract validity score (handle different response formats)
      const validityScore =
        result.validity_score ??
        result.score ??
        result.prediction ??
        0.85; // Default fallback

      console.log(`[ShadowTwinConsensus] ${predictor.name} score: ${validityScore.toFixed(3)}`);

      return {
        predictor_id: id,
        predictor_name: predictor.name,
        validity_score: Number(validityScore),
        confidence: 0.95,
        weight: predictor.weight,
        status: 'success',
      };
    } catch (error) {
      console.error(`[ShadowTwinConsensus] ${predictor.name} error:`, error);

      return {
        predictor_id: id,
        predictor_name: predictor.name,
        validity_score: 0.0,
        confidence: 0.0,
        weight: predictor.weight,
        status: 'error',
        error: (error as Error).message,
      };
    }
  }

  /**
   * Get predictor status
   */
  async getPredictorStatus(): Promise<Record<string, { status: 'online' | 'offline'; latency?: number }>> {
    const statusPromises = Object.entries(this.predictors)
      .filter(([_, predictor]) => predictor.enabled)
      .map(async ([id, predictor]) => {
        const startTime = Date.now();
        try {
          const response = await fetch(predictor.url.replace('/predict', '/health'), {
            method: 'GET',
            signal: AbortSignal.timeout(5000),
          });

          const latency = Date.now() - startTime;

          return [
            id,
            {
              status: response.ok ? ('online' as const) : ('offline' as const),
              latency,
            },
          ];
        } catch {
          return [
            id,
            {
              status: 'offline' as const,
            },
          ];
        }
      });

    const results = await Promise.all(statusPromises);
    return Object.fromEntries(results);
  }

  /**
   * Configure predictors
   */
  configurePredictors(config: Partial<Record<string, Partial<Predictor>>>) {
    Object.entries(config).forEach(([id, updates]) => {
      if (this.predictors[id]) {
        this.predictors[id] = { ...this.predictors[id], ...updates };
      }
    });
  }

  /**
   * Set consensus thresholds
   */
  setThresholds(pct?: number, validity?: number) {
    if (pct !== undefined) {
      this.pctThreshold = pct;
    }
    if (validity !== undefined) {
      this.validityThreshold = validity;
    }
  }

  /**
   * Get current configuration
   */
  getConfig() {
    return {
      predictors: this.predictors,
      pctThreshold: this.pctThreshold,
      validityThreshold: this.validityThreshold,
    };
  }
}

// Singleton instance
let consensusClient: ShadowTwinConsensusClient | null = null;

export function getShadowTwinConsensusClient(): ShadowTwinConsensusClient {
  if (!consensusClient) {
    consensusClient = new ShadowTwinConsensusClient();
  }
  return consensusClient;
}
