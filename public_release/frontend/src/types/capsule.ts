export type CapsuleStatus = 'active' | 'idle' | 'error' | 'warning' | 'critical' | 'resolved' | 'dismissed' | 'optimizing' | 'standby';
export type CapsulePriority = 'low' | 'medium' | 'high' | 'critical';
export type CapsuleAction = 'ignite' | 'shutdown' | 'restart' | 'mitigate' | 'inspect' | 'dismiss' | 'escalate' | 'acknowledge';
export type CapsuleViewState = 'pill' | 'expanded' | 'full';

export interface Capsule {
  capsule_id: string;
  name: string;
  category: string;
  status: CapsuleStatus;
  prin_score: number;
  energy_usage: number;
  utid?: string;
  area_code?: number;
  entropy?: number;
  version?: string;
}

export interface CapsuleActionPayload {
  action: CapsuleAction;
  parameters?: Record<string, any>;
}

export interface CapsuleData {
  id: string;
  title: string;
  description: string;
  status: CapsuleStatus;
  priority: number; // Changed to number to match usage in CapsulePill (P{priority})
  source: string;
  timestamp: string;
  actions: CapsuleAction[];
  metadata: Record<string, any>;
  utid?: string;
  proofId?: string;
  energyConsumed?: number;
  carbonFootprint?: number;
}

export interface CapsuleUpdate {
  id: string;
  status?: CapsuleStatus;
  metrics?: Record<string, any>;
}
