/**
 * Feature Flags Service
 * Week 8: White-Label Platform - Phase 4
 * 
 * Per-tenant feature flag management for white-label deployments.
 * Enables/disables features at runtime without code changes.
 */

export interface FeatureFlag {
  key: string;
  name: string;
  description: string;
  enabled: boolean;
  tenantId?: string;
  category: 'core' | 'widget' | 'ami' | 'integration' | 'experimental';
}

export interface TenantFeatureConfig {
  tenantId: string;
  tenantName: string;
  flags: Record<string, boolean>;
}

/**
 * Default feature flags available across all deployments
 */
export const DEFAULT_FEATURE_FLAGS: FeatureFlag[] = [
  // Core Features
  {
    key: 'websocket_realtime',
    name: 'WebSocket Real-Time Updates',
    description: 'Enable real-time capsule updates via WebSocket',
    enabled: true,
    category: 'core',
  },
  {
    key: 'offline_mode',
    name: 'Offline Mode',
    description: 'Enable offline-first PWA capabilities',
    enabled: true,
    category: 'core',
  },
  {
    key: 'push_notifications',
    name: 'Push Notifications',
    description: 'Enable browser push notifications',
    enabled: true,
    category: 'core',
  },

  // Widget Features
  {
    key: 'widget_wallet_orb',
    name: 'Wallet Orb Widget',
    description: 'Enable wallet balance visualization widget',
    enabled: true,
    category: 'widget',
  },
  {
    key: 'widget_proof_ticker',
    name: 'Proof Ticker Widget',
    description: 'Enable proof generation feed widget',
    enabled: true,
    category: 'widget',
  },
  {
    key: 'widget_capsule_card',
    name: 'Capsule Card Widget',
    description: 'Enable capsule display widget',
    enabled: true,
    category: 'widget',
  },
  {
    key: 'widget_energy_gauge',
    name: 'Energy Gauge Widget',
    description: 'Enable energy visualization widget',
    enabled: true,
    category: 'widget',
  },
  {
    key: 'widget_utid_badge',
    name: 'UTID Badge Widget',
    description: 'Enable UTID display widget',
    enabled: true,
    category: 'widget',
  },
  {
    key: 'widget_ami_pulse',
    name: 'AmI Pulse Widget',
    description: 'Enable ambient intelligence activity widget',
    enabled: true,
    category: 'widget',
  },
  {
    key: 'widget_shadow_twin',
    name: 'Shadow Twin Widget',
    description: 'Enable digital twin sync widget',
    enabled: true,
    category: 'widget',
  },

  // AmI Features
  {
    key: 'ami_context_awareness',
    name: 'Context Awareness',
    description: 'Enable AmI context-aware intelligence',
    enabled: true,
    category: 'ami',
  },
  {
    key: 'ami_proactive',
    name: 'Proactive Intelligence',
    description: 'Enable AmI proactive predictions',
    enabled: true,
    category: 'ami',
  },
  {
    key: 'ami_seamless',
    name: 'Seamless Integration',
    description: 'Enable AmI seamless user experience',
    enabled: true,
    category: 'ami',
  },
  {
    key: 'ami_adaptive',
    name: 'Adaptive Learning',
    description: 'Enable AmI adaptive behavior',
    enabled: true,
    category: 'ami',
  },
  {
    key: 'cosmic_fabric',
    name: 'Cosmic Intelligence Fabric',
    description: 'Enable federated learning across deployments',
    enabled: true,
    category: 'ami',
  },

  // Integration Features
  {
    key: 'mcp_protocol',
    name: 'MCP Protocol',
    description: 'Enable Model Context Protocol integration',
    enabled: true,
    category: 'integration',
  },
  {
    key: 'a2a_protocol',
    name: 'A2A Protocol',
    description: 'Enable Agent-to-Agent communication',
    enabled: true,
    category: 'integration',
  },
  {
    key: 'thermal_computing',
    name: 'Thermal Computing',
    description: 'Enable JAX/Jasmin thermodynamic computing',
    enabled: true,
    category: 'integration',
  },
  {
    key: 'microadapt_edge',
    name: 'MicroAdaptEdge',
    description: 'Enable edge device optimization',
    enabled: true,
    category: 'integration',
  },

  // Experimental Features
  {
    key: 'experimental_voice_control',
    name: 'Voice Control',
    description: 'Enable voice commands for capsule management',
    enabled: false,
    category: 'experimental',
  },
  {
    key: 'experimental_ar_view',
    name: 'AR Visualization',
    description: 'Enable augmented reality capsule visualization',
    enabled: false,
    category: 'experimental',
  },
  {
    key: 'experimental_quantum_sim',
    name: 'Quantum Simulation',
    description: 'Enable quantum computing simulation for optimization',
    enabled: false,
    category: 'experimental',
  },
];

/**
 * Feature Flags Manager
 */
export class FeatureFlagsManager {
  private flags: Map<string, boolean> = new Map();
  private tenantId: string | null = null;
  private listeners: Set<(flags: Map<string, boolean>) => void> = new Set();

  constructor() {
    this.loadFlags();
  }

  /**
   * Initialize feature flags for a specific tenant
   */
  initialize(tenantId: string, config?: TenantFeatureConfig): void {
    this.tenantId = tenantId;
    
    if (config) {
      // Load tenant-specific configuration
      Object.entries(config.flags).forEach(([key, enabled]) => {
        this.flags.set(key, enabled);
      });
    } else {
      // Load default flags
      DEFAULT_FEATURE_FLAGS.forEach(flag => {
        this.flags.set(flag.key, flag.enabled);
      });
    }

    this.saveFlags();
    this.notifyListeners();
  }

  /**
   * Check if a feature is enabled
   */
  isEnabled(flagKey: string): boolean {
    return this.flags.get(flagKey) ?? false;
  }

  /**
   * Enable a feature flag
   */
  enable(flagKey: string): void {
    this.flags.set(flagKey, true);
    this.saveFlags();
    this.notifyListeners();
  }

  /**
   * Disable a feature flag
   */
  disable(flagKey: string): void {
    this.flags.set(flagKey, false);
    this.saveFlags();
    this.notifyListeners();
  }

  /**
   * Toggle a feature flag
   */
  toggle(flagKey: string): void {
    const current = this.isEnabled(flagKey);
    this.flags.set(flagKey, !current);
    this.saveFlags();
    this.notifyListeners();
  }

  /**
   * Get all flags with their current state
   */
  getAllFlags(): FeatureFlag[] {
    return DEFAULT_FEATURE_FLAGS.map(flag => ({
      ...flag,
      enabled: this.isEnabled(flag.key),
      tenantId: this.tenantId ?? undefined,
    }));
  }

  /**
   * Get flags by category
   */
  getFlagsByCategory(category: FeatureFlag['category']): FeatureFlag[] {
    return this.getAllFlags().filter(flag => flag.category === category);
  }

  /**
   * Bulk update flags
   */
  updateFlags(updates: Record<string, boolean>): void {
    Object.entries(updates).forEach(([key, enabled]) => {
      this.flags.set(key, enabled);
    });
    this.saveFlags();
    this.notifyListeners();
  }

  /**
   * Reset all flags to defaults
   */
  resetToDefaults(): void {
    this.flags.clear();
    DEFAULT_FEATURE_FLAGS.forEach(flag => {
      this.flags.set(flag.key, flag.enabled);
    });
    this.saveFlags();
    this.notifyListeners();
  }

  /**
   * Export current configuration
   */
  exportConfig(): TenantFeatureConfig {
    const flagsObj: Record<string, boolean> = {};
    this.flags.forEach((enabled, key) => {
      flagsObj[key] = enabled;
    });

    return {
      tenantId: this.tenantId ?? 'default',
      tenantName: 'Default Tenant',
      flags: flagsObj,
    };
  }

  /**
   * Import configuration
   */
  importConfig(config: TenantFeatureConfig): void {
    this.initialize(config.tenantId, config);
  }

  /**
   * Subscribe to flag changes
   */
  subscribe(listener: (flags: Map<string, boolean>) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  /**
   * Load flags from localStorage
   */
  private loadFlags(): void {
    try {
      const stored = localStorage.getItem('feature_flags');
      if (stored) {
        const data = JSON.parse(stored);
        Object.entries(data).forEach(([key, enabled]) => {
          this.flags.set(key, enabled as boolean);
        });
      } else {
        // Initialize with defaults
        DEFAULT_FEATURE_FLAGS.forEach(flag => {
          this.flags.set(flag.key, flag.enabled);
        });
      }
    } catch (error) {
      console.error('Failed to load feature flags:', error);
    }
  }

  /**
   * Save flags to localStorage
   */
  private saveFlags(): void {
    try {
      const data: Record<string, boolean> = {};
      this.flags.forEach((enabled, key) => {
        data[key] = enabled;
      });
      localStorage.setItem('feature_flags', JSON.stringify(data));
    } catch (error) {
      console.error('Failed to save feature flags:', error);
    }
  }

  /**
   * Notify all listeners of flag changes
   */
  private notifyListeners(): void {
    this.listeners.forEach(listener => {
      listener(new Map(this.flags));
    });
  }
}

// Singleton instance
export const featureFlags = new FeatureFlagsManager();

/**
 * React hook for feature flags
 */
export function useFeatureFlag(flagKey: string): boolean {
  const [enabled, setEnabled] = React.useState(() => featureFlags.isEnabled(flagKey));

  React.useEffect(() => {
    const unsubscribe = featureFlags.subscribe((flags) => {
      setEnabled(flags.get(flagKey) ?? false);
    });
    return unsubscribe;
  }, [flagKey]);

  return enabled;
}

/**
 * React hook for all feature flags
 */
export function useFeatureFlags(): FeatureFlag[] {
  const [flags, setFlags] = React.useState(() => featureFlags.getAllFlags());

  React.useEffect(() => {
    const unsubscribe = featureFlags.subscribe(() => {
      setFlags(featureFlags.getAllFlags());
    });
    return unsubscribe;
  }, []);

  return flags;
}

// Add React import for hooks
import React from 'react';
