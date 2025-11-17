/**
 * Capsule Client SDK - TypeScript
 * 
 * Production-ready client for Deploy Anywhere Capsules (DACs)
 * Works in: Web browsers, React Native, Node.js
 */

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

export enum CapsuleType {
  ALERT = "alert",
  NOTIFICATION = "notification",
  TASK = "task",
  UPDATE = "update",
  PROGRESS = "progress"
}

export enum CapsuleStatus {
  ACTIVE = "active",
  PENDING = "pending",
  RESOLVED = "resolved",
  DISMISSED = "dismissed",
  EXPIRED = "expired"
}

export enum CapsulePriority {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical"
}

export enum CapsuleAction {
  MITIGATE = "mitigate",
  INSPECT = "inspect",
  DISMISS = "dismiss",
  APPROVE = "approve",
  REJECT = "reject",
  SNOOZE = "snooze",
  ESCALATE = "escalate"
}

export enum PresentationMode {
  COMPACT = "compact",
  MINIMAL = "minimal",
  EXPANDED = "expanded",
  FULL = "full"
}

export interface CapsuleAttributes {
  capsule_id: string;
  capsule_type: CapsuleType;
  title: string;
  subtitle?: string;
  icon_name: string;
  primary_color: string;
  created_at: string;
  expires_at?: string;
  deep_link_url?: string;
  metadata?: Record<string, any>;
}

export interface CapsuleContentState {
  status: CapsuleStatus;
  priority: CapsulePriority;
  progress?: number;
  status_message?: string;
  metric_value?: string;
  metric_label?: string;
  actions?: CapsuleAction[];
  presentation_mode?: PresentationMode;
  updated_at?: string;
}

export interface Capsule {
  attributes: CapsuleAttributes;
  content_state: CapsuleContentState;
}

export interface CapsuleClientConfig {
  apiUrl: string;
  wsUrl: string;
  apiKey?: string;
  userId?: string;
  deviceId?: string;
  autoReconnect?: boolean;
  reconnectInterval?: number;
  heartbeatInterval?: number;
  debug?: boolean;
}

export interface ActionResult {
  success: boolean;
  message?: string;
  data?: any;
}

// ============================================================================
// CAPSULE CLIENT
// ============================================================================

export class CapsuleClient {
  private config: Required<CapsuleClientConfig>;
  private ws: WebSocket | null = null;
  private jwt: string | null = null;
  private capsules: Map<string, Capsule> = new Map();
  private listeners: Map<string, Set<(capsule: Capsule) => void>> = new Map();
  private reconnectTimer: any = null;
  private heartbeatTimer: any = null;
  private isConnecting: boolean = false;

  constructor(config: CapsuleClientConfig) {
    this.config = {
      apiUrl: config.apiUrl,
      wsUrl: config.wsUrl,
      apiKey: config.apiKey || "",
      userId: config.userId || "",
      deviceId: config.deviceId || this.generateDeviceId(),
      autoReconnect: config.autoReconnect !== false,
      reconnectInterval: config.reconnectInterval || 5000,
      heartbeatInterval: config.heartbeatInterval || 30000,
      debug: config.debug || false
    };
  }

  // ========================================================================
  // CONNECTION MANAGEMENT
  // ========================================================================

  async connect(): Promise<void> {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      this.log("Already connected or connecting");
      return;
    }

    this.isConnecting = true;

    try {
      // Get JWT token
      this.jwt = await this.getJWTToken();
      
      // Connect WebSocket
      await this.connectWebSocket();
      
      this.log("Connected successfully");
    } catch (error) {
      this.log("Connection failed:", error);
      this.isConnecting = false;
      
      if (this.config.autoReconnect) {
        this.scheduleReconnect();
      }
      
      throw error;
    }
  }

  private async connectWebSocket(): Promise<void> {
    return new Promise((resolve, reject) => {
      const wsUrl = `${this.config.wsUrl}/ws?token=${this.jwt}`;
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.log("WebSocket connected");
        this.isConnecting = false;
        this.startHeartbeat();
        resolve();
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(event.data);
      };

      this.ws.onerror = (error) => {
        this.log("WebSocket error:", error);
        if (this.isConnecting) {
          reject(error);
        }
      };

      this.ws.onclose = () => {
        this.log("WebSocket closed");
        this.stopHeartbeat();
        
        if (this.config.autoReconnect) {
          this.scheduleReconnect();
        }
      };
    });
  }

  disconnect(): void {
    this.log("Disconnecting...");
    
    this.stopHeartbeat();
    this.stopReconnect();
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.jwt = null;
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      return;
    }

    this.log(`Reconnecting in ${this.config.reconnectInterval}ms...`);
    
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect().catch(() => {
        // Will auto-retry if autoReconnect is enabled
      });
    }, this.config.reconnectInterval);
  }

  private stopReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: "ping" }));
      }
    }, this.config.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  // ========================================================================
  // AUTHENTICATION
  // ========================================================================

  private async getJWTToken(): Promise<string> {
    const response = await fetch(`${this.config.apiUrl}/ws/token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(this.config.apiKey && { "X-API-Key": this.config.apiKey })
      },
      body: JSON.stringify({
        user_id: this.config.userId,
        device_id: this.config.deviceId
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to get JWT token: ${response.statusText}`);
    }

    const data = await response.json();
    return data.token;
  }

  // ========================================================================
  // CAPSULE MANAGEMENT
  // ========================================================================

  async getCapsules(): Promise<Capsule[]> {
    const response = await this.apiRequest("GET", "/activities");
    return response.activities || [];
  }

  async getCapsule(capsuleId: string): Promise<Capsule | null> {
    try {
      const response = await this.apiRequest("GET", `/activity/${capsuleId}`);
      return response.activity || null;
    } catch (error) {
      this.log("Failed to get capsule:", error);
      return null;
    }
  }

  async createCapsule(capsule: Capsule): Promise<boolean> {
    try {
      await this.apiRequest("POST", "/create-activity", capsule);
      return true;
    } catch (error) {
      this.log("Failed to create capsule:", error);
      return false;
    }
  }

  async updateCapsule(capsule: Capsule): Promise<boolean> {
    try {
      await this.apiRequest("PUT", "/update", capsule);
      return true;
    } catch (error) {
      this.log("Failed to update capsule:", error);
      return false;
    }
  }

  async performAction(capsuleId: string, action: CapsuleAction, data?: any): Promise<ActionResult> {
    try {
      const response = await this.apiRequest("POST", "/action", {
        capsule_id: capsuleId,
        action,
        data
      });
      
      return {
        success: true,
        message: response.message,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        message: error.message || "Action failed"
      };
    }
  }

  // ========================================================================
  // REAL-TIME UPDATES
  // ========================================================================

  onCapsuleUpdate(capsuleId: string, callback: (capsule: Capsule) => void): () => void {
    if (!this.listeners.has(capsuleId)) {
      this.listeners.set(capsuleId, new Set());
    }
    
    this.listeners.get(capsuleId)!.add(callback);
    
    // Return unsubscribe function
    return () => {
      const listeners = this.listeners.get(capsuleId);
      if (listeners) {
        listeners.delete(callback);
        if (listeners.size === 0) {
          this.listeners.delete(capsuleId);
        }
      }
    };
  }

  onAnyCapsuleUpdate(callback: (capsule: Capsule) => void): () => void {
    return this.onCapsuleUpdate("*", callback);
  }

  private handleMessage(data: string): void {
    try {
      const message = JSON.parse(data);
      
      if (message.type === "pong") {
        // Heartbeat response
        return;
      }
      
      if (message.type === "capsule_update" && message.capsule) {
        const capsule: Capsule = message.capsule;
        this.capsules.set(capsule.attributes.capsule_id, capsule);
        
        // Notify specific listeners
        const listeners = this.listeners.get(capsule.attributes.capsule_id);
        if (listeners) {
          listeners.forEach(callback => callback(capsule));
        }
        
        // Notify wildcard listeners
        const wildcardListeners = this.listeners.get("*");
        if (wildcardListeners) {
          wildcardListeners.forEach(callback => callback(capsule));
        }
      }
    } catch (error) {
      this.log("Failed to handle message:", error);
    }
  }

  // ========================================================================
  // HTTP API
  // ========================================================================

  private async apiRequest(method: string, path: string, body?: any): Promise<any> {
    const response = await fetch(`${this.config.apiUrl}${path}`, {
      method,
      headers: {
        "Content-Type": "application/json",
        ...(this.config.apiKey && { "X-API-Key": this.config.apiKey }),
        ...(this.jwt && { "Authorization": `Bearer ${this.jwt}` })
      },
      ...(body && { body: JSON.stringify(body) })
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }

    return response.json();
  }

  // ========================================================================
  // UTILITIES
  // ========================================================================

  private generateDeviceId(): string {
    return `device-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private log(...args: any[]): void {
    if (this.config.debug) {
      console.log("[CapsuleClient]", ...args);
    }
  }

  getLocalCapsules(): Capsule[] {
    return Array.from(this.capsules.values());
  }

  getLocalCapsule(capsuleId: string): Capsule | undefined {
    return this.capsules.get(capsuleId);
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

// ============================================================================
// EXPORTS
// ============================================================================

export default CapsuleClient;
