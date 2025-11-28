/**
 * AmI Context Awareness Module
 * Week 8: White-Label Platform - Phase 3
 * 
 * Implements the 4 AmI principles:
 * 1. Context-awareness - Perceives user state automatically
 * 2. Proactivity - Anticipates needs without commands
 * 3. Seamless integration - Intelligence blends invisibly
 * 4. Adaptivity - Uniquely tailored per user
 */

import { AmIPrinciples, LocalPattern, getCosmicFabric } from './CosmicFabric';

export interface UserContext {
  userId: string;
  sessionId: string;
  location: 'home' | 'settings' | 'catalog' | 'widgets' | 'admin';
  timeOfDay: 'morning' | 'afternoon' | 'evening' | 'night';
  deviceType: 'mobile' | 'tablet' | 'desktop';
  networkQuality: 'excellent' | 'good' | 'poor' | 'offline';
  batteryLevel?: number; // 0-100
  preferences: Record<string, any>;
  recentActions: string[];
  timestamp: number;
}

export interface PredictedNeed {
  type: 'navigation' | 'action' | 'information' | 'optimization';
  suggestion: string;
  confidence: number; // 0-1
  reasoning: string;
  timestamp: number;
}

export interface AdaptiveRule {
  id: string;
  condition: (context: UserContext) => boolean;
  action: (context: UserContext) => void;
  priority: number;
  enabled: boolean;
}

export class AmIContextService {
  private context: UserContext;
  private adaptiveRules: AdaptiveRule[] = [];
  private predictionHistory: PredictedNeed[] = [];
  private contextHistory: UserContext[] = [];
  private maxHistorySize = 100;

  constructor(userId: string) {
    this.context = this.initializeContext(userId);
    this.setupDefaultRules();
    this.startContextMonitoring();
  }

  /**
   * Initialize user context
   */
  private initializeContext(userId: string): UserContext {
    return {
      userId,
      sessionId: this.generateSessionId(),
      location: 'home',
      timeOfDay: this.getTimeOfDay(),
      deviceType: this.detectDeviceType(),
      networkQuality: 'good',
      preferences: {},
      recentActions: [],
      timestamp: Date.now(),
    };
  }

  /**
   * Start monitoring context changes
   */
  private startContextMonitoring(): void {
    // Monitor location changes
    window.addEventListener('popstate', () => {
      this.updateLocation();
    });

    // Monitor network quality
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      connection.addEventListener('change', () => {
        this.updateNetworkQuality();
      });
    }

    // Monitor battery level (if available)
    if ('getBattery' in navigator) {
      (navigator as any).getBattery().then((battery: any) => {
        this.context.batteryLevel = battery.level * 100;
        battery.addEventListener('levelchange', () => {
          this.context.batteryLevel = battery.level * 100;
          this.onContextChange();
        });
      });
    }

    // Update time of day every minute
    setInterval(() => {
      const newTimeOfDay = this.getTimeOfDay();
      if (newTimeOfDay !== this.context.timeOfDay) {
        this.context.timeOfDay = newTimeOfDay;
        this.onContextChange();
      }
    }, 60000);
  }

  /**
   * Update current location
   */
  private updateLocation(): void {
    const path = window.location.pathname;
    let location: UserContext['location'] = 'home';
    
    if (path.includes('/settings')) location = 'settings';
    else if (path.includes('/catalog')) location = 'catalog';
    else if (path.includes('/widgets')) location = 'widgets';
    else if (path.includes('/admin')) location = 'admin';

    if (location !== this.context.location) {
      this.context.location = location;
      this.onContextChange();
    }
  }

  /**
   * Update network quality
   */
  private updateNetworkQuality(): void {
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      const effectiveType = connection.effectiveType;
      
      let quality: UserContext['networkQuality'] = 'good';
      if (effectiveType === '4g') quality = 'excellent';
      else if (effectiveType === '3g') quality = 'good';
      else if (effectiveType === '2g') quality = 'poor';
      else if (!navigator.onLine) quality = 'offline';

      if (quality !== this.context.networkQuality) {
        this.context.networkQuality = quality;
        this.onContextChange();
      }
    }
  }

  /**
   * Get time of day
   */
  private getTimeOfDay(): UserContext['timeOfDay'] {
    const hour = new Date().getHours();
    if (hour >= 5 && hour < 12) return 'morning';
    if (hour >= 12 && hour < 17) return 'afternoon';
    if (hour >= 17 && hour < 21) return 'evening';
    return 'night';
  }

  /**
   * Detect device type
   */
  private detectDeviceType(): UserContext['deviceType'] {
    const width = window.innerWidth;
    if (width < 768) return 'mobile';
    if (width < 1024) return 'tablet';
    return 'desktop';
  }

  /**
   * Generate session ID
   */
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Context changed - trigger AmI logic
   */
  private onContextChange(): void {
    this.context.timestamp = Date.now();
    
    // Save to history
    this.contextHistory.push({ ...this.context });
    if (this.contextHistory.length > this.maxHistorySize) {
      this.contextHistory.shift();
    }

    // Calculate AmI metrics
    const amiMetrics = this.calculateAmIMetrics();

    // Send to Cosmic Fabric for learning
    const fabric = getCosmicFabric();
    if (fabric) {
      fabric.learnLocal({
        type: 'user_behavior',
        features: this.contextToFeatures(this.context),
        confidence: 0.8,
        amiPrinciples: amiMetrics,
      });
    }

    // Run adaptive rules
    this.runAdaptiveRules();

    // Make predictions
    this.predictUserNeeds();

    // Emit event
    window.dispatchEvent(new CustomEvent('ami-context-change', {
      detail: { context: this.context, amiMetrics },
    }));
  }

  /**
   * Convert context to feature vector
   */
  private contextToFeatures(context: UserContext): number[] {
    return [
      context.location === 'home' ? 1 : 0,
      context.location === 'settings' ? 1 : 0,
      context.location === 'catalog' ? 1 : 0,
      context.location === 'widgets' ? 1 : 0,
      context.location === 'admin' ? 1 : 0,
      context.timeOfDay === 'morning' ? 1 : 0,
      context.timeOfDay === 'afternoon' ? 1 : 0,
      context.timeOfDay === 'evening' ? 1 : 0,
      context.timeOfDay === 'night' ? 1 : 0,
      context.deviceType === 'mobile' ? 1 : 0,
      context.deviceType === 'tablet' ? 1 : 0,
      context.deviceType === 'desktop' ? 1 : 0,
      context.networkQuality === 'excellent' ? 1 : 0,
      context.networkQuality === 'good' ? 1 : 0,
      context.networkQuality === 'poor' ? 1 : 0,
      context.batteryLevel ? context.batteryLevel / 100 : 1,
      context.recentActions.length / 10,
    ];
  }

  /**
   * Calculate AmI metrics
   */
  private calculateAmIMetrics(): AmIPrinciples {
    const contextAwareness = this.calculateContextAwareness();
    const proactivity = this.calculateProactivity();
    const seamlessness = this.calculateSeamlessness();
    const adaptivity = this.calculateAdaptivity();

    return {
      contextAwareness,
      proactivity,
      seamlessness,
      adaptivity,
    };
  }

  /**
   * Calculate context awareness score
   */
  private calculateContextAwareness(): number {
    // Based on how much context we're tracking
    let score = 0;
    if (this.context.location) score += 20;
    if (this.context.timeOfDay) score += 20;
    if (this.context.deviceType) score += 20;
    if (this.context.networkQuality) score += 20;
    if (this.context.batteryLevel !== undefined) score += 10;
    if (this.context.recentActions.length > 0) score += 10;
    return score;
  }

  /**
   * Calculate proactivity score
   */
  private calculateProactivity(): number {
    // Based on predictions made
    const recentPredictions = this.predictionHistory.filter(
      p => Date.now() - p.timestamp < 60000 // Last minute
    );
    return Math.min(100, recentPredictions.length * 20);
  }

  /**
   * Calculate seamlessness score
   */
  private calculateSeamlessness(): number {
    // Based on how invisible the AmI is (fewer interruptions)
    const recentActions = this.context.recentActions.length;
    return Math.max(0, 100 - recentActions * 5);
  }

  /**
   * Calculate adaptivity score
   */
  private calculateAdaptivity(): number {
    // Based on adaptive rules triggered
    const enabledRules = this.adaptiveRules.filter(r => r.enabled).length;
    return Math.min(100, enabledRules * 10);
  }

  /**
   * Setup default adaptive rules
   */
  private setupDefaultRules(): void {
    // Rule: Low battery + poor network = suggest offline mode
    this.addAdaptiveRule({
      id: 'low_battery_offline',
      condition: (ctx) => 
        (ctx.batteryLevel || 100) < 20 && ctx.networkQuality === 'poor',
      action: (ctx) => {
        this.suggestAction('Enable offline mode to save battery', 0.8);
      },
      priority: 10,
      enabled: true,
    });

    // Rule: Evening + home = suggest theme switch
    this.addAdaptiveRule({
      id: 'evening_dark_theme',
      condition: (ctx) => 
        ctx.timeOfDay === 'evening' && ctx.location === 'home',
      action: (ctx) => {
        this.suggestAction('Switch to dark theme for better readability', 0.7);
      },
      priority: 5,
      enabled: true,
    });

    // Rule: Mobile + catalog = suggest filters
    this.addAdaptiveRule({
      id: 'mobile_catalog_filters',
      condition: (ctx) => 
        ctx.deviceType === 'mobile' && ctx.location === 'catalog',
      action: (ctx) => {
        this.suggestAction('Use filters to find capsules faster', 0.6);
      },
      priority: 3,
      enabled: true,
    });
  }

  /**
   * Add adaptive rule
   */
  public addAdaptiveRule(rule: AdaptiveRule): void {
    this.adaptiveRules.push(rule);
    this.adaptiveRules.sort((a, b) => b.priority - a.priority);
  }

  /**
   * Run adaptive rules
   */
  private runAdaptiveRules(): void {
    for (const rule of this.adaptiveRules) {
      if (rule.enabled && rule.condition(this.context)) {
        rule.action(this.context);
      }
    }
  }

  /**
   * Predict user needs
   */
  private predictUserNeeds(): void {
    // Simple heuristic-based predictions
    // In production, this would use the federated model from Cosmic Fabric

    if (this.context.location === 'home' && this.context.recentActions.length === 0) {
      this.addPrediction({
        type: 'navigation',
        suggestion: 'View capsule catalog',
        confidence: 0.6,
        reasoning: 'Users typically browse catalog after landing',
        timestamp: Date.now(),
      });
    }

    if (this.context.location === 'catalog' && this.context.recentActions.includes('search')) {
      this.addPrediction({
        type: 'action',
        suggestion: 'Apply filters to refine search',
        confidence: 0.7,
        reasoning: 'Search followed by filtering is common pattern',
        timestamp: Date.now(),
      });
    }
  }

  /**
   * Add prediction
   */
  private addPrediction(prediction: PredictedNeed): void {
    this.predictionHistory.push(prediction);
    if (this.predictionHistory.length > this.maxHistorySize) {
      this.predictionHistory.shift();
    }

    // Emit event
    window.dispatchEvent(new CustomEvent('ami-prediction', {
      detail: prediction,
    }));
  }

  /**
   * Suggest action to user
   */
  private suggestAction(suggestion: string, confidence: number): void {
    console.log(`[AmI] Suggestion: ${suggestion} (confidence: ${confidence})`);
    
    // In production, this would show a subtle notification
    // For now, just log and emit event
    window.dispatchEvent(new CustomEvent('ami-suggestion', {
      detail: { suggestion, confidence },
    }));
  }

  /**
   * Record user action
   */
  public recordAction(action: string): void {
    this.context.recentActions.push(action);
    if (this.context.recentActions.length > 20) {
      this.context.recentActions.shift();
    }
    this.onContextChange();
  }

  /**
   * Get current context
   */
  public getContext(): UserContext {
    return { ...this.context };
  }

  /**
   * Get predictions
   */
  public getPredictions(): PredictedNeed[] {
    return [...this.predictionHistory];
  }

  /**
   * Update user preferences
   */
  public updatePreferences(preferences: Record<string, any>): void {
    this.context.preferences = { ...this.context.preferences, ...preferences };
    this.onContextChange();
  }
}

// Singleton instance
let amiContextInstance: AmIContextService | null = null;

export function initializeAmIContext(userId: string): AmIContextService {
  if (!amiContextInstance) {
    amiContextInstance = new AmIContextService(userId);
  }
  return amiContextInstance;
}

export function getAmIContext(): AmIContextService | null {
  return amiContextInstance;
}
