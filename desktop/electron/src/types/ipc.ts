/**
 * IPC (Inter-Process Communication) Types
 * Defines the contract between main and renderer processes
 */

import { Capsule, CapsuleLaunchpad, AppConfig } from './capsule';

/**
 * Channels for IPC communication
 */
export enum IPCChannel {
  // Capsule operations
  GET_LAUNCHPAD = 'capsule:get-launchpad',
  EXECUTE_ACTION = 'capsule:execute-action',
  PIN_CAPSULE = 'capsule:pin',
  HIDE_CAPSULE = 'capsule:hide',
  SNOOZE_CAPSULE = 'capsule:snooze',
  
  // WebSocket events
  WS_CONNECTED = 'ws:connected',
  WS_DISCONNECTED = 'ws:disconnected',
  WS_MESSAGE = 'ws:message',
  WS_ERROR = 'ws:error',
  
  // App configuration
  GET_CONFIG = 'config:get',
  SET_CONFIG = 'config:set',
  
  // Window management
  SHOW_WINDOW = 'window:show',
  HIDE_WINDOW = 'window:hide',
  TOGGLE_WINDOW = 'window:toggle',
  
  // Notifications
  SHOW_NOTIFICATION = 'notification:show',
  
  // Shortcuts
  REGISTER_SHORTCUT = 'shortcut:register',
  UNREGISTER_SHORTCUT = 'shortcut:unregister',
}

/**
 * Request/Response types for each IPC channel
 */
export interface IPCRequest {
  [IPCChannel.GET_LAUNCHPAD]: { userId: string };
  [IPCChannel.EXECUTE_ACTION]: { capsuleId: string; actionId: string };
  [IPCChannel.PIN_CAPSULE]: { capsuleId: string; pinned: boolean };
  [IPCChannel.HIDE_CAPSULE]: { capsuleId: string };
  [IPCChannel.SNOOZE_CAPSULE]: { capsuleId: string; duration: number };
  [IPCChannel.GET_CONFIG]: void;
  [IPCChannel.SET_CONFIG]: Partial<AppConfig>;
  [IPCChannel.SHOW_NOTIFICATION]: { title: string; body: string; capsuleId?: string };
  [IPCChannel.REGISTER_SHORTCUT]: { key: string; action: string };
  [IPCChannel.UNREGISTER_SHORTCUT]: { key: string };
}

export interface IPCResponse {
  [IPCChannel.GET_LAUNCHPAD]: CapsuleLaunchpad;
  [IPCChannel.EXECUTE_ACTION]: { success: boolean; message?: string };
  [IPCChannel.PIN_CAPSULE]: { success: boolean };
  [IPCChannel.HIDE_CAPSULE]: { success: boolean };
  [IPCChannel.SNOOZE_CAPSULE]: { success: boolean };
  [IPCChannel.GET_CONFIG]: AppConfig;
  [IPCChannel.SET_CONFIG]: { success: boolean };
  [IPCChannel.SHOW_NOTIFICATION]: { success: boolean };
  [IPCChannel.REGISTER_SHORTCUT]: { success: boolean };
  [IPCChannel.UNREGISTER_SHORTCUT]: { success: boolean };
}

/**
 * Events sent from main to renderer
 */
export interface IPCEvent {
  [IPCChannel.WS_CONNECTED]: void;
  [IPCChannel.WS_DISCONNECTED]: void;
  [IPCChannel.WS_MESSAGE]: { type: string; payload: any };
  [IPCChannel.WS_ERROR]: { error: string };
}

/**
 * Type-safe IPC API exposed to renderer
 */
export interface ElectronAPI {
  // Invoke methods (request-response)
  invoke<K extends keyof IPCRequest>(
    channel: K,
    data: IPCRequest[K]
  ): Promise<IPCResponse[K]>;
  
  // Send methods (one-way)
  send(channel: string, data?: any): void;
  
  // Listen methods (event handlers)
  on<K extends keyof IPCEvent>(
    channel: K,
    callback: (data: IPCEvent[K]) => void
  ): () => void;
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}
