/**
 * Service Worker Registration
 * 
 * Handles service worker registration and updates
 */

export interface ServiceWorkerStatus {
  registered: boolean;
  installing: boolean;
  waiting: boolean;
  active: boolean;
  error: Error | null;
}

export type ServiceWorkerCallback = (status: ServiceWorkerStatus) => void;

class ServiceWorkerManager {
  private registration: ServiceWorkerRegistration | null = null;
  private callbacks: ServiceWorkerCallback[] = [];

  /**
   * Register service worker
   */
  async register(swUrl: string = '/sw.js'): Promise<ServiceWorkerRegistration | null> {
    if (!('serviceWorker' in navigator)) {
      console.warn('Service Worker not supported');
      this.notifyCallbacks({
        registered: false,
        installing: false,
        waiting: false,
        active: false,
        error: new Error('Service Worker not supported')
      });
      return null;
    }

    try {
      console.log('Registering service worker...');
      
      this.registration = await navigator.serviceWorker.register(swUrl, {
        scope: '/'
      });

      console.log('Service worker registered:', this.registration.scope);

      // Listen for updates
      this.registration.addEventListener('updatefound', () => {
        console.log('Service worker update found');
        this.handleUpdate();
      });

      // Check for updates periodically
      setInterval(() => {
        this.registration?.update();
      }, 60 * 60 * 1000); // Check every hour

      this.notifyCallbacks(this.getStatus());
      return this.registration;
    } catch (error) {
      console.error('Service worker registration failed:', error);
      this.notifyCallbacks({
        registered: false,
        installing: false,
        waiting: false,
        active: false,
        error: error as Error
      });
      return null;
    }
  }

  /**
   * Unregister service worker
   */
  async unregister(): Promise<boolean> {
    if (!this.registration) {
      return false;
    }

    try {
      const result = await this.registration.unregister();
      console.log('Service worker unregistered:', result);
      this.registration = null;
      this.notifyCallbacks({
        registered: false,
        installing: false,
        waiting: false,
        active: false,
        error: null
      });
      return result;
    } catch (error) {
      console.error('Service worker unregistration failed:', error);
      return false;
    }
  }

  /**
   * Update service worker
   */
  async update(): Promise<void> {
    if (!this.registration) {
      console.warn('No service worker registered');
      return;
    }

    try {
      await this.registration.update();
      console.log('Service worker update check completed');
    } catch (error) {
      console.error('Service worker update failed:', error);
    }
  }

  /**
   * Skip waiting and activate new service worker
   */
  skipWaiting(): void {
    if (!this.registration?.waiting) {
      console.warn('No waiting service worker');
      return;
    }

    this.registration.waiting.postMessage({ type: 'SKIP_WAITING' });
  }

  /**
   * Get current status
   */
  getStatus(): ServiceWorkerStatus {
    if (!this.registration) {
      return {
        registered: false,
        installing: false,
        waiting: false,
        active: false,
        error: null
      };
    }

    return {
      registered: true,
      installing: !!this.registration.installing,
      waiting: !!this.registration.waiting,
      active: !!this.registration.active,
      error: null
    };
  }

  /**
   * Subscribe to status changes
   */
  subscribe(callback: ServiceWorkerCallback): () => void {
    this.callbacks.push(callback);
    
    // Immediately call with current status
    callback(this.getStatus());

    // Return unsubscribe function
    return () => {
      this.callbacks = this.callbacks.filter(cb => cb !== callback);
    };
  }

  private handleUpdate(): void {
    const installingWorker = this.registration?.installing;
    if (!installingWorker) return;

    installingWorker.addEventListener('statechange', () => {
      if (installingWorker.state === 'installed') {
        if (navigator.serviceWorker.controller) {
          // New service worker available
          console.log('New service worker available');
          this.notifyCallbacks(this.getStatus());
        } else {
          // Service worker installed for first time
          console.log('Service worker installed');
          this.notifyCallbacks(this.getStatus());
        }
      }
    });
  }

  private notifyCallbacks(status: ServiceWorkerStatus): void {
    this.callbacks.forEach(callback => {
      try {
        callback(status);
      } catch (error) {
        console.error('Service worker callback error:', error);
      }
    });
  }
}

// Export singleton instance
export const swManager = new ServiceWorkerManager();

/**
 * Register service worker (convenience function)
 */
export async function registerServiceWorker(): Promise<ServiceWorkerRegistration | null> {
  return swManager.register();
}

/**
 * Unregister service worker (convenience function)
 */
export async function unregisterServiceWorker(): Promise<boolean> {
  return swManager.unregister();
}
