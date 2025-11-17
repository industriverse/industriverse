/**
 * Capsule data types for Capsule Pins PWA
 * 
 * These types define the structure of capsule data received from
 * the Capsule Gateway Service and displayed in the UI.
 */

export type CapsuleStatus = 'active' | 'warning' | 'critical' | 'resolved' | 'dismissed';

export type CapsuleAction = 'mitigate' | 'inspect' | 'dismiss' | 'escalate' | 'acknowledge';

export interface CapsuleData {
  id: string;
  title: string;
  description: string;
  status: CapsuleStatus;
  priority: number; // 1-5, where 5 is highest
  timestamp: string; // ISO 8601 timestamp
  source: string; // e.g., "thermal_sampler", "world_model", "microadapt_edge"
  metadata: Record<string, any>;
  actions: CapsuleAction[];
  utid?: string; // Unique Traceable ID from Remix Lab
  proofId?: string; // Proof ID from ProofEconomy
  energyConsumed?: number; // Joules
  carbonFootprint?: number; // kg CO2
}

export interface CapsuleUpdate {
  capsuleId: string;
  updates: Partial<CapsuleData>;
  timestamp: string;
}

export type CapsuleViewState = 'pill' | 'expanded' | 'full';

export interface CapsuleActionResult {
  success: boolean;
  message: string;
  updatedCapsule?: CapsuleData;
}
