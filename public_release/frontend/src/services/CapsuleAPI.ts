/**
 * Capsule Gateway API Service
 * 
 * REST API client for Capsule Gateway Service
 */

import type { CapsuleData, CapsuleAction } from '@/types/capsule';

export interface APIConfig {
  baseUrl: string;
  authToken?: string;
}

export interface ActionRequest {
  capsuleId: string;
  action: CapsuleAction;
  userId?: string;
  metadata?: Record<string, any>;
}

export interface ActionResponse {
  success: boolean;
  capsuleId: string;
  action: CapsuleAction;
  timestamp: string;
  message?: string;
}

export class CapsuleAPI {
  private config: Required<APIConfig>;

  constructor(config: APIConfig) {
    this.config = {
      baseUrl: config.baseUrl,
      authToken: config.authToken || ''
    };
  }

  /**
   * Get all capsules
   */
  async getCapsules(): Promise<CapsuleData[]> {
    const response = await this.fetch('/api/v1/capsules');
    return response.json();
  }

  /**
   * Get capsule by ID
   */
  async getCapsule(id: string): Promise<CapsuleData> {
    const response = await this.fetch(`/api/v1/capsules/${id}`);
    return response.json();
  }

  /**
   * Execute action on capsule
   */
  async executeAction(request: ActionRequest): Promise<ActionResponse> {
    const response = await this.fetch('/api/v1/capsule/action', {
      method: 'POST',
      body: JSON.stringify(request)
    });
    return response.json();
  }

  /**
   * Get capsule statistics
   */
  async getStatistics(): Promise<{
    total: number;
    active: number;
    warning: number;
    critical: number;
    resolved: number;
    dismissed: number;
  }> {
    const response = await this.fetch('/api/v1/capsules/statistics');
    return response.json();
  }

  /**
   * Update auth token
   */
  updateAuthToken(token: string): void {
    this.config.authToken = token;
  }

  /**
   * Internal fetch wrapper with auth and error handling
   */
  private async fetch(path: string, options: RequestInit = {}): Promise<Response> {
    const url = `${this.config.baseUrl}${path}`;
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {})
    };

    if (this.config.authToken) {
      headers['Authorization'] = `Bearer ${this.config.authToken}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          message: response.statusText
        }));
        throw new Error(error.message || `HTTP ${response.status}`);
      }

      return response;
    } catch (error) {
      if (error instanceof TypeError) {
        throw new Error('Network error: Unable to reach server');
      }
      throw error;
    }
  }
}

// Create singleton instance
let apiInstance: CapsuleAPI | null = null;

/**
 * Get API instance
 */
export function getAPI(): CapsuleAPI {
  if (!apiInstance) {
    const baseUrl = import.meta.env.VITE_CAPSULE_GATEWAY_API || 'https://capsule-gateway.industriverse.io';
    const authToken = import.meta.env.VITE_AUTH_TOKEN || '';
    
    apiInstance = new CapsuleAPI({
      baseUrl,
      authToken
    });
  }
  
  return apiInstance;
}

/**
 * Update API auth token
 */
export function updateAPIToken(token: string): void {
  getAPI().updateAuthToken(token);
}
