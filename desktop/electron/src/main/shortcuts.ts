/**
 * Keyboard Shortcut Manager
 * Handles global keyboard shortcuts for capsule actions
 */

import { globalShortcut } from 'electron';

export class KeyboardShortcutManager {
  private registeredShortcuts: Map<string, () => void> = new Map();

  /**
   * Register a global keyboard shortcut
   */
  registerShortcut(accelerator: string, callback: () => void): boolean {
    try {
      // Unregister if already registered
      if (this.registeredShortcuts.has(accelerator)) {
        this.unregisterShortcut(accelerator);
      }

      // Register shortcut
      const success = globalShortcut.register(accelerator, callback);

      if (success) {
        this.registeredShortcuts.set(accelerator, callback);
        console.log(`[Shortcuts] Registered: ${accelerator}`);
      } else {
        console.warn(`[Shortcuts] Failed to register: ${accelerator}`);
      }

      return success;
    } catch (error) {
      console.error(`[Shortcuts] Error registering ${accelerator}:`, error);
      return false;
    }
  }

  /**
   * Unregister a global keyboard shortcut
   */
  unregisterShortcut(accelerator: string): void {
    if (this.registeredShortcuts.has(accelerator)) {
      globalShortcut.unregister(accelerator);
      this.registeredShortcuts.delete(accelerator);
      console.log(`[Shortcuts] Unregistered: ${accelerator}`);
    }
  }

  /**
   * Unregister all shortcuts
   */
  unregisterAll(): void {
    globalShortcut.unregisterAll();
    this.registeredShortcuts.clear();
    console.log('[Shortcuts] Unregistered all shortcuts');
  }

  /**
   * Check if shortcut is registered
   */
  isRegistered(accelerator: string): boolean {
    return globalShortcut.isRegistered(accelerator);
  }

  /**
   * Get all registered shortcuts
   */
  getRegisteredShortcuts(): string[] {
    return Array.from(this.registeredShortcuts.keys());
  }
}
