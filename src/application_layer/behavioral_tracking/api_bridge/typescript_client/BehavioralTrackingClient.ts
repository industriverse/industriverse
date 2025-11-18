/**
 * Behavioral Tracking Client (TypeScript)
 * Week 17 Day 2: TypeScript Client for Unified Behavioral Tracking
 *
 * This client connects Week 16 TypeScript/JavaScript frontends to the
 * Week 9 Python behavioral tracking backend via REST API.
 *
 * Usage:
 * ```typescript
 * const client = new BehavioralTrackingClient('http://localhost:8001');
 *
 * // Track interaction
 * await client.trackInteraction({
 *   event_type: 'click',
 *   user_id: 'user123',
 *   session_id: 'sess456',
 *   capsule_id: 'cap789'
 * });
 *
 * // Get behavioral vector
 * const bv = await client.getBehavioralVector('user123');
 * ```
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

// =============================================================================
// Type Definitions
// =============================================================================

export interface InteractionEvent {
  event_id?: string;
  timestamp?: string;
  event_type: string;
  severity?: string;

  // User context
  user_id: string;
  session_id: string;
  device_id?: string;
  device_type?: 'web' | 'ios' | 'android' | 'desktop' | 'wearable';

  // Capsule context
  capsule_id?: string;
  capsule_type?: string;
  capsule_category?: string;

  // Interaction details
  interaction_target?: string;
  action_id?: string;
  component_id?: string;

  // Timing metrics
  duration_ms?: number;
  time_since_last_interaction_ms?: number;

  // Interaction data
  interaction_data?: Record<string, any>;

  // Result
  success?: boolean;
  error_message?: string;

  // Behavioral context
  context?: Record<string, any>;
}

export interface InteractionEventResponse {
  event_id: string;
  status: string;
  timestamp: string;
}

export interface BehavioralVector {
  user_id: string;
  computed_at: string;
  version: number;

  usage_patterns: Record<string, any>;
  preferences: Record<string, any>;
  expertise_level: Record<string, any>;
  engagement_metrics: Record<string, any>;
  adaptive_ux_config: Record<string, any>;
  metadata: Record<string, any>;

  created_at: string;
  updated_at: string;
}

export interface UserSession {
  session_id: string;
  user_id: string;
  started_at: string;
  last_interaction_at?: string;
  ended_at?: string;
  device_id?: string;
  device_type?: string;

  event_count: number;
  unique_capsules_count: number;
  duration_minutes?: number;

  interaction_type_distribution: Record<string, number>;
  capsule_types_visited: string[];

  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface EngagementScore {
  user_id: string;
  engagement_score: number;
  confidence: number;
  last_computed: string;
  factors: Record<string, any>;
}

export interface UserInteractionsResponse {
  user_id: string;
  count: number;
  limit: number;
  offset: number;
  interactions: any[];
}

export interface HealthCheckResponse {
  status: string;
  service: string;
  version: string;
  timestamp: string;
}

// =============================================================================
// Behavioral Tracking Client
// =============================================================================

export class BehavioralTrackingClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = 'http://localhost:8001') {
    this.baseURL = baseURL;

    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      this.handleError
    );
  }

  /**
   * Handle API errors
   */
  private handleError(error: AxiosError): Promise<never> {
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const data = error.response.data as any;

      console.error(`Behavioral Tracking API Error [${status}]:`, data);

      throw new Error(data.detail || `API Error: ${status}`);
    } else if (error.request) {
      // Request made but no response
      console.error('Behavioral Tracking API: No response from server');
      throw new Error('No response from behavioral tracking server');
    } else {
      // Error in request setup
      console.error('Behavioral Tracking API Error:', error.message);
      throw error;
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    const response = await this.client.get<HealthCheckResponse>(
      '/api/v1/behavioral/health'
    );
    return response.data;
  }

  /**
   * Track a user interaction event
   */
  async trackInteraction(
    event: InteractionEvent
  ): Promise<InteractionEventResponse> {
    const response = await this.client.post<InteractionEventResponse>(
      '/api/v1/behavioral/interactions',
      event
    );
    return response.data;
  }

  /**
   * Get behavioral vector for a user
   */
  async getBehavioralVector(user_id: string): Promise<BehavioralVector> {
    const response = await this.client.get<BehavioralVector>(
      `/api/v1/behavioral/vectors/${user_id}`
    );
    return response.data;
  }

  /**
   * Compute (or recompute) behavioral vector for a user
   */
  async computeBehavioralVector(user_id: string): Promise<BehavioralVector> {
    const response = await this.client.post<BehavioralVector>(
      `/api/v1/behavioral/vectors/${user_id}/compute`
    );
    return response.data;
  }

  /**
   * Get engagement score for a user
   */
  async getEngagementScore(user_id: string): Promise<EngagementScore> {
    const response = await this.client.get<EngagementScore>(
      `/api/v1/behavioral/vectors/${user_id}/engagement`
    );
    return response.data;
  }

  /**
   * Get session details
   */
  async getSession(session_id: string): Promise<UserSession> {
    const response = await this.client.get<UserSession>(
      `/api/v1/behavioral/sessions/${session_id}`
    );
    return response.data;
  }

  /**
   * Get interaction history for a user
   */
  async getUserInteractions(
    user_id: string,
    options: {
      limit?: number;
      offset?: number;
      start_date?: string;
      end_date?: string;
    } = {}
  ): Promise<UserInteractionsResponse> {
    const params = new URLSearchParams();

    if (options.limit) params.append('limit', options.limit.toString());
    if (options.offset) params.append('offset', options.offset.toString());
    if (options.start_date) params.append('start_date', options.start_date);
    if (options.end_date) params.append('end_date', options.end_date);

    const response = await this.client.get<UserInteractionsResponse>(
      `/api/v1/behavioral/interactions/${user_id}?${params.toString()}`
    );
    return response.data;
  }

  /**
   * Clear cached behavioral data for a user
   */
  async clearCache(user_id: string): Promise<{ status: string; user_id: string }> {
    const response = await this.client.delete(
      `/api/v1/behavioral/vectors/${user_id}/cache`
    );
    return response.data;
  }

  /**
   * Helper: Track capsule click
   */
  async trackCapsuleClick(
    user_id: string,
    session_id: string,
    capsule_id: string,
    capsule_type: string
  ): Promise<InteractionEventResponse> {
    return this.trackInteraction({
      event_type: 'click',
      user_id,
      session_id,
      capsule_id,
      capsule_type,
      interaction_target: 'capsule',
    });
  }

  /**
   * Helper: Track capsule expand
   */
  async trackCapsuleExpand(
    user_id: string,
    session_id: string,
    capsule_id: string,
    capsule_type: string
  ): Promise<InteractionEventResponse> {
    return this.trackInteraction({
      event_type: 'expand',
      user_id,
      session_id,
      capsule_id,
      capsule_type,
      interaction_target: 'capsule',
    });
  }

  /**
   * Helper: Track capsule acknowledge
   */
  async trackCapsuleAcknowledge(
    user_id: string,
    session_id: string,
    capsule_id: string,
    capsule_type: string
  ): Promise<InteractionEventResponse> {
    return this.trackInteraction({
      event_type: 'acknowledge',
      user_id,
      session_id,
      capsule_id,
      capsule_type,
      interaction_target: 'capsule',
    });
  }

  /**
   * Helper: Track capsule complete
   */
  async trackCapsuleComplete(
    user_id: string,
    session_id: string,
    capsule_id: string,
    capsule_type: string,
    duration_ms?: number
  ): Promise<InteractionEventResponse> {
    return this.trackInteraction({
      event_type: 'complete',
      user_id,
      session_id,
      capsule_id,
      capsule_type,
      interaction_target: 'capsule',
      duration_ms,
    });
  }
}

// =============================================================================
// React Hook (Optional)
// =============================================================================

/**
 * React Hook for behavioral tracking
 *
 * Usage:
 * ```typescript
 * const { trackInteraction, behavioralVector, loading } = useBehavioralTracking('user123');
 * ```
 */
export function useBehavioralTracking(user_id: string, session_id: string) {
  const [behavioralVector, setBehavioralVector] = React.useState<BehavioralVector | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<Error | null>(null);

  const client = React.useMemo(
    () => new BehavioralTrackingClient(),
    []
  );

  // Load behavioral vector on mount
  React.useEffect(() => {
    async function loadBehavioralVector() {
      try {
        setLoading(true);
        const bv = await client.getBehavioralVector(user_id);
        setBehavioralVector(bv);
      } catch (err) {
        console.warn('Failed to load behavioral vector:', err);
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    }

    if (user_id) {
      loadBehavioralVector();
    }
  }, [user_id, client]);

  // Track interaction helper
  const trackInteraction = React.useCallback(
    async (event: Partial<InteractionEvent>) => {
      try {
        await client.trackInteraction({
          user_id,
          session_id,
          ...event,
        } as InteractionEvent);
      } catch (err) {
        console.error('Failed to track interaction:', err);
      }
    },
    [user_id, session_id, client]
  );

  // Recompute behavioral vector
  const recomputeBehavioralVector = React.useCallback(async () => {
    try {
      setLoading(true);
      const bv = await client.computeBehavioralVector(user_id);
      setBehavioralVector(bv);
    } catch (err) {
      console.error('Failed to recompute behavioral vector:', err);
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [user_id, client]);

  return {
    behavioralVector,
    loading,
    error,
    trackInteraction,
    recomputeBehavioralVector,
  };
}

// Note: React import is assumed to be available in the consuming application
// If using this file standalone, add: import * as React from 'react';

export default BehavioralTrackingClient;
