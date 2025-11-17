/**
 * Preload Script
 * Secure bridge between main and renderer processes
 * Exposes limited, type-safe API to renderer
 */

import { contextBridge, ipcRenderer } from 'electron';
import type { ElectronAPI, IPCRequest, IPCResponse, IPCEvent } from '../types/ipc';

/**
 * Type-safe IPC API implementation
 */
const electronAPI: ElectronAPI = {
  /**
   * Invoke a request-response IPC call
   */
  invoke: async <K extends keyof IPCRequest>(
    channel: K,
    data: IPCRequest[K]
  ): Promise<IPCResponse[K]> => {
    return await ipcRenderer.invoke(channel, data);
  },

  /**
   * Send a one-way message to main process
   */
  send: (channel: string, data?: any): void => {
    ipcRenderer.send(channel, data);
  },

  /**
   * Listen to events from main process
   * Returns unsubscribe function
   */
  on: <K extends keyof IPCEvent>(
    channel: K,
    callback: (data: IPCEvent[K]) => void
  ): (() => void) => {
    const subscription = (_event: Electron.IpcRendererEvent, data: IPCEvent[K]) => {
      callback(data);
    };
    
    ipcRenderer.on(channel, subscription);
    
    // Return unsubscribe function
    return () => {
      ipcRenderer.removeListener(channel, subscription);
    };
  },
};

/**
 * Expose API to renderer process
 * This is the ONLY way renderer can communicate with main
 */
contextBridge.exposeInMainWorld('electronAPI', electronAPI);

/**
 * Security: Log when preload script is loaded
 */
console.log('[Preload] Secure IPC bridge initialized');
