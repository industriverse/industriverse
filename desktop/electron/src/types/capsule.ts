/**
 * Capsule Data Models
 * Shared types between main and renderer processes
 */

export enum CapsuleType {
  TASK = 'task',
  ALERT = 'alert',
  NOTIFICATION = 'notification',
  DECISION = 'decision',
  STATUS = 'status',
  WORKFLOW = 'workflow',
  CUSTOM = 'custom',
}

export enum CapsuleState {
  DRAFT = 'draft',
  ACTIVE = 'active',
  SNOOZED = 'snoozed',
  COMPLETED = 'completed',
  ARCHIVED = 'archived',
}

export enum CapsulePriority {
  CRITICAL = 'critical',
  HIGH = 'high',
  NORMAL = 'normal',
  LOW = 'low',
}

export interface CapsuleAction {
  id: string;
  label: string;
  type: 'primary' | 'secondary' | 'destructive';
  requiresConfirmation?: boolean;
  shortcut?: string;
}

export interface Capsule {
  id: string;
  type: CapsuleType;
  state: CapsuleState;
  priority: CapsulePriority;
  title: string;
  description?: string;
  metadata?: Record<string, any>;
  actions: CapsuleAction[];
  createdAt: string;
  updatedAt: string;
  expiresAt?: string;
  isPinned?: boolean;
  badgeCount?: number;
  utid?: string;
  energySignature?: number;
  consciousnessScore?: number;
}

export interface CapsuleLaunchpad {
  userId: string;
  capsules: Capsule[];
  totalCount: number;
  activeCount: number;
  timestamp: string;
}

export interface WebSocketMessage {
  type: 'capsule_update' | 'capsule_spawn' | 'capsule_delete' | 'launchpad_refresh';
  payload: any;
  timestamp: string;
}

export interface AppConfig {
  apiUrl: string;
  wsUrl: string;
  userId: string;
  authToken: string;
  autoLaunch: boolean;
  showBadgeCount: boolean;
  enableNotifications: boolean;
  theme: 'light' | 'dark' | 'system';
  shortcuts: Record<string, string>;
}
