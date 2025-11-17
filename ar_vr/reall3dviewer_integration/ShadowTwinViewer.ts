/**
 * Shadow Twin Viewer with 3D Gaussian Splatting + Capsule Overlays
 * 
 * Integrates Reall3DViewer for photorealistic Shadow Twin rendering with
 * real-time capsule overlays in AR/VR environments.
 * 
 * Architecture:
 *   1. Load Shadow Twin .spx models from S3
 *   2. Render capsules as 3D overlays at spatial coordinates
 *   3. Handle AR/VR interactions (tap, gaze, controller)
 *   4. Real-time capsule updates via WebSocket
 * 
 * Dependencies:
 *   - @reall3d/reall3dviewer (NPM package)
 *   - three.js (peer dependency)
 *   - WebSocket client
 * 
 * Usage:
 *   const viewer = new ShadowTwinViewer({
 *     container: document.getElementById('viewer'),
 *     shadowTwinId: 'motor_001',
 *     capsuleGatewayUrl: 'wss://capsule-gateway.industriverse.io/ws'
 *   });
 *   
 *   await viewer.initialize();
 *   viewer.addCapsuleOverlay(capsule, position);
 */

import * as THREE from 'three';
import { Reall3dViewer } from '@reall3d/reall3dviewer';

// ============================================================================
// Type Definitions
// ============================================================================

export interface ShadowTwinViewerConfig {
  /** DOM container for viewer */
  container: HTMLElement;
  
  /** Shadow Twin unique identifier */
  shadowTwinId: string;
  
  /** Capsule Gateway WebSocket URL */
  capsuleGatewayUrl: string;
  
  /** S3 base URL for .spx models */
  modelBaseUrl?: string;
  
  /** Viewer quality level (1-9) */
  qualityLevel?: number;
  
  /** Enable AR mode (mobile camera passthrough) */
  enableAR?: boolean;
  
  /** Enable VR mode (headset immersive) */
  enableVR?: boolean;
  
  /** Authentication token for WebSocket */
  authToken?: string;
}

export interface Capsule {
  id: string;
  title: string;
  description: string;
  status: 'critical' | 'warning' | 'active' | 'resolved' | 'dismissed';
  priority: 1 | 2 | 3 | 4 | 5;
  timestamp: string;
  source: string;
  metadata: Record<string, any>;
  actions: string[];
  
  /** 3D spatial position on Shadow Twin */
  position?: THREE.Vector3;
  
  /** Shadow Twin component ID (e.g., 'motor_bearing_A') */
  componentId?: string;
}

export interface CapsuleOverlayConfig {
  /** Capsule data */
  capsule: Capsule;
  
  /** 3D position in world coordinates */
  position: THREE.Vector3;
  
  /** Scale factor for capsule mesh */
  scale?: number;
  
  /** Enable pulsing animation */
  enablePulse?: boolean;
  
  /** Enable glow effect */
  enableGlow?: boolean;
}

export interface CapsuleMetrics {
  total: number;
  critical: number;
  warning: number;
  active: number;
  resolved: number;
  dismissed: number;
}

// ============================================================================
// Capsule Overlay Class
// ============================================================================

class CapsuleOverlay {
  public mesh: THREE.Mesh;
  public label: THREE.Sprite;
  public capsule: Capsule;
  
  private glowMesh?: THREE.Mesh;
  private pulseAnimation?: number;
  
  constructor(config: CapsuleOverlayConfig) {
    this.capsule = config.capsule;
    
    // Create capsule 3D mesh
    this.mesh = this.createCapsuleMesh(config);
    this.mesh.position.copy(config.position);
    this.mesh.userData.capsule = config.capsule;
    this.mesh.userData.type = 'capsule_overlay';
    
    // Create text label
    this.label = this.createLabel(config.capsule.title);
    this.label.position.set(
      config.position.x,
      config.position.y + 0.5,
      config.position.z
    );
    
    // Add glow effect if enabled
    if (config.enableGlow) {
      this.glowMesh = this.createGlowMesh(config);
      this.glowMesh.position.copy(config.position);
    }
    
    // Start pulse animation if enabled
    if (config.enablePulse) {
      this.startPulseAnimation();
    }
  }
  
  private createCapsuleMesh(config: CapsuleOverlayConfig): THREE.Mesh {
    const scale = config.scale || 0.1;
    
    // Geometry: Sphere for simplicity (can be customized)
    const geometry = new THREE.SphereGeometry(scale, 32, 32);
    
    // Material: Color-coded by status
    const color = this.getColorByStatus(config.capsule.status);
    const material = new THREE.MeshStandardMaterial({
      color: color,
      emissive: color,
      emissiveIntensity: 0.3,
      metalness: 0.5,
      roughness: 0.5,
      transparent: true,
      opacity: 0.9
    });
    
    return new THREE.Mesh(geometry, material);
  }
  
  private createGlowMesh(config: CapsuleOverlayConfig): THREE.Mesh {
    const scale = (config.scale || 0.1) * 1.5;
    
    const geometry = new THREE.SphereGeometry(scale, 32, 32);
    const color = this.getColorByStatus(config.capsule.status);
    
    const material = new THREE.MeshBasicMaterial({
      color: color,
      transparent: true,
      opacity: 0.2,
      side: THREE.BackSide
    });
    
    return new THREE.Mesh(geometry, material);
  }
  
  private createLabel(text: string): THREE.Sprite {
    // Create canvas for text
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d')!;
    canvas.width = 512;
    canvas.height = 128;
    
    // Draw background
    context.fillStyle = 'rgba(0, 0, 0, 0.7)';
    context.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw text
    context.font = 'bold 48px Arial';
    context.fillStyle = 'white';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(text, canvas.width / 2, canvas.height / 2);
    
    // Create sprite
    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({ map: texture });
    const sprite = new THREE.Sprite(material);
    sprite.scale.set(1, 0.25, 1);
    
    return sprite;
  }
  
  private getColorByStatus(status: Capsule['status']): number {
    const statusColors = {
      critical: 0xff3333,    // Red
      warning: 0xffaa33,     // Amber
      active: 0x33ff33,      // Green
      resolved: 0x888888,    // Gray
      dismissed: 0x444444    // Dark gray
    };
    
    return statusColors[status];
  }
  
  private startPulseAnimation() {
    let scale = 1.0;
    let direction = 1;
    
    const animate = () => {
      scale += direction * 0.01;
      
      if (scale > 1.2) {
        direction = -1;
      } else if (scale < 1.0) {
        direction = 1;
      }
      
      this.mesh.scale.setScalar(scale);
      
      if (this.glowMesh) {
        this.glowMesh.scale.setScalar(scale * 1.5);
      }
      
      this.pulseAnimation = requestAnimationFrame(animate);
    };
    
    animate();
  }
  
  public dispose() {
    // Stop animation
    if (this.pulseAnimation) {
      cancelAnimationFrame(this.pulseAnimation);
    }
    
    // Dispose geometries and materials
    this.mesh.geometry.dispose();
    (this.mesh.material as THREE.Material).dispose();
    
    if (this.glowMesh) {
      this.glowMesh.geometry.dispose();
      (this.glowMesh.material as THREE.Material).dispose();
    }
    
    if (this.label.material.map) {
      this.label.material.map.dispose();
    }
    this.label.material.dispose();
  }
}

// ============================================================================
// Shadow Twin Viewer Class
// ============================================================================

export class ShadowTwinViewer {
  private config: Required<ShadowTwinViewerConfig>;
  private viewer: Reall3dViewer;
  private scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera;
  private renderer: THREE.WebGLRenderer;
  
  private capsuleOverlays: Map<string, CapsuleOverlay> = new Map();
  private websocket?: WebSocket;
  private raycaster: THREE.Raycaster = new THREE.Raycaster();
  
  private isInitialized: boolean = false;
  
  constructor(config: ShadowTwinViewerConfig) {
    this.config = {
      container: config.container,
      shadowTwinId: config.shadowTwinId,
      capsuleGatewayUrl: config.capsuleGatewayUrl,
      modelBaseUrl: config.modelBaseUrl || 'https://s3.industriverse.io/shadow-twins',
      qualityLevel: config.qualityLevel || 7,
      enableAR: config.enableAR || false,
      enableVR: config.enableVR || false,
      authToken: config.authToken || ''
    };
    
    // Initialize Three.js components
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(
      75,
      config.container.clientWidth / config.container.clientHeight,
      0.1,
      1000
    );
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    
    // Initialize Reall3DViewer
    this.viewer = new Reall3dViewer({
      root: config.container,
      qualityLevel: this.config.qualityLevel
    });
  }
  
  /**
   * Initialize viewer and load Shadow Twin model
   */
  public async initialize(): Promise<void> {
    if (this.isInitialized) {
      console.warn('ShadowTwinViewer already initialized');
      return;
    }
    
    console.log(`Initializing ShadowTwinViewer for ${this.config.shadowTwinId}`);
    
    // Load Shadow Twin .spx model
    const modelUrl = await this.getModelUrl();
    console.log(`Loading model from: ${modelUrl}`);
    
    await this.viewer.addModel(modelUrl);
    
    // Set up camera
    this.camera.position.set(5, 5, 5);
    this.camera.lookAt(0, 0, 0);
    
    // Set up renderer
    this.renderer.setSize(
      this.config.container.clientWidth,
      this.config.container.clientHeight
    );
    this.renderer.setPixelRatio(window.devicePixelRatio);
    
    // Add lights
    this.setupLights();
    
    // Connect to Capsule Gateway WebSocket
    await this.connectWebSocket();
    
    // Set up interaction handlers
    this.setupInteractionHandlers();
    
    // Start render loop
    this.startRenderLoop();
    
    this.isInitialized = true;
    console.log('ShadowTwinViewer initialized successfully');
  }
  
  /**
   * Get .spx model URL from S3
   */
  private async getModelUrl(): Promise<string> {
    const url = `${this.config.modelBaseUrl}/${this.config.shadowTwinId}/${this.config.shadowTwinId}.spx`;
    
    // Verify model exists
    const response = await fetch(url, { method: 'HEAD' });
    if (!response.ok) {
      throw new Error(`Model not found: ${url}`);
    }
    
    return url;
  }
  
  /**
   * Set up scene lights
   */
  private setupLights() {
    // Ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    this.scene.add(ambientLight);
    
    // Directional light
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 10, 10);
    this.scene.add(directionalLight);
    
    // Point light for capsule highlights
    const pointLight = new THREE.PointLight(0xffffff, 0.5);
    pointLight.position.set(0, 5, 0);
    this.scene.add(pointLight);
  }
  
  /**
   * Connect to Capsule Gateway WebSocket
   */
  private async connectWebSocket(): Promise<void> {
    return new Promise((resolve, reject) => {
      const url = `${this.config.capsuleGatewayUrl}?shadowTwinId=${this.config.shadowTwinId}`;
      
      this.websocket = new WebSocket(url);
      
      this.websocket.onopen = () => {
        console.log('WebSocket connected to Capsule Gateway');
        
        // Authenticate if token provided
        if (this.config.authToken) {
          this.websocket!.send(JSON.stringify({
            type: 'auth',
            token: this.config.authToken
          }));
        }
        
        resolve();
      };
      
      this.websocket.onmessage = (event) => {
        this.handleWebSocketMessage(event.data);
      };
      
      this.websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(error);
      };
      
      this.websocket.onclose = () => {
        console.log('WebSocket disconnected');
        // Attempt reconnection after 5 seconds
        setTimeout(() => this.connectWebSocket(), 5000);
      };
    });
  }
  
  /**
   * Handle WebSocket messages from Capsule Gateway
   */
  private handleWebSocketMessage(data: string) {
    try {
      const message = JSON.parse(data);
      
      switch (message.type) {
        case 'capsule_new':
          this.handleCapsuleNew(message.capsule);
          break;
        
        case 'capsule_update':
          this.handleCapsuleUpdate(message.capsule);
          break;
        
        case 'capsule_removed':
          this.handleCapsuleRemoved(message.capsuleId);
          break;
        
        default:
          console.warn('Unknown message type:', message.type);
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }
  
  /**
   * Handle new capsule from WebSocket
   */
  private handleCapsuleNew(capsule: Capsule) {
    console.log('New capsule:', capsule.id);
    
    // Get position from capsule metadata or component mapping
    const position = this.getCapsulePosition(capsule);
    
    if (position) {
      this.addCapsuleOverlay(capsule, position);
    }
  }
  
  /**
   * Handle capsule update from WebSocket
   */
  private handleCapsuleUpdate(capsule: Capsule) {
    console.log('Capsule updated:', capsule.id);
    
    // Remove old overlay
    this.removeCapsuleOverlay(capsule.id);
    
    // Add updated overlay
    const position = this.getCapsulePosition(capsule);
    if (position) {
      this.addCapsuleOverlay(capsule, position);
    }
  }
  
  /**
   * Handle capsule removal from WebSocket
   */
  private handleCapsuleRemoved(capsuleId: string) {
    console.log('Capsule removed:', capsuleId);
    this.removeCapsuleOverlay(capsuleId);
  }
  
  /**
   * Get 3D position for capsule
   */
  private getCapsulePosition(capsule: Capsule): THREE.Vector3 | null {
    // Option 1: Position from capsule metadata
    if (capsule.position) {
      return capsule.position;
    }
    
    // Option 2: Position from component mapping
    if (capsule.componentId) {
      return this.getComponentPosition(capsule.componentId);
    }
    
    // Option 3: Default position (center of model)
    console.warn(`No position found for capsule ${capsule.id}, using default`);
    return new THREE.Vector3(0, 0, 0);
  }
  
  /**
   * Get position of Shadow Twin component
   */
  private getComponentPosition(componentId: string): THREE.Vector3 | null {
    // TODO: Implement component position lookup from Shadow Twin metadata
    // This would query a database or metadata file mapping component IDs to 3D positions
    
    console.warn(`Component position lookup not implemented for ${componentId}`);
    return null;
  }
  
  /**
   * Add capsule overlay to scene
   */
  public addCapsuleOverlay(capsule: Capsule, position: THREE.Vector3) {
    // Remove existing overlay if present
    if (this.capsuleOverlays.has(capsule.id)) {
      this.removeCapsuleOverlay(capsule.id);
    }
    
    // Create overlay
    const overlay = new CapsuleOverlay({
      capsule,
      position,
      scale: 0.1,
      enablePulse: capsule.status === 'critical' || capsule.status === 'warning',
      enableGlow: true
    });
    
    // Add to scene
    this.scene.add(overlay.mesh);
    this.scene.add(overlay.label);
    
    if (overlay.glowMesh) {
      this.scene.add(overlay.glowMesh);
    }
    
    // Store overlay
    this.capsuleOverlays.set(capsule.id, overlay);
    
    console.log(`Added capsule overlay: ${capsule.id}`);
  }
  
  /**
   * Remove capsule overlay from scene
   */
  public removeCapsuleOverlay(capsuleId: string) {
    const overlay = this.capsuleOverlays.get(capsuleId);
    
    if (overlay) {
      // Remove from scene
      this.scene.remove(overlay.mesh);
      this.scene.remove(overlay.label);
      
      if (overlay.glowMesh) {
        this.scene.remove(overlay.glowMesh);
      }
      
      // Dispose resources
      overlay.dispose();
      
      // Remove from map
      this.capsuleOverlays.delete(capsuleId);
      
      console.log(`Removed capsule overlay: ${capsuleId}`);
    }
  }
  
  /**
   * Get capsule metrics
   */
  public getCapsuleMetrics(): CapsuleMetrics {
    const metrics: CapsuleMetrics = {
      total: 0,
      critical: 0,
      warning: 0,
      active: 0,
      resolved: 0,
      dismissed: 0
    };
    
    for (const overlay of this.capsuleOverlays.values()) {
      metrics.total++;
      metrics[overlay.capsule.status]++;
    }
    
    return metrics;
  }
  
  /**
   * Set up interaction handlers (mouse, touch, VR controller)
   */
  private setupInteractionHandlers() {
    // Mouse click
    this.config.container.addEventListener('click', (event) => {
      this.handleClick(event);
    });
    
    // Touch tap (mobile AR)
    this.config.container.addEventListener('touchend', (event) => {
      if (event.touches.length === 0) {
        this.handleClick(event.changedTouches[0]);
      }
    });
    
    // TODO: VR controller interaction
    // This would use WebXR API for VR headset controller input
  }
  
  /**
   * Handle click/tap on capsule
   */
  private handleClick(event: MouseEvent | Touch) {
    // Calculate normalized device coordinates
    const rect = this.config.container.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    const y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    
    // Raycast from camera
    this.raycaster.setFromCamera(new THREE.Vector2(x, y), this.camera);
    
    // Get all capsule meshes
    const capsuleMeshes = Array.from(this.capsuleOverlays.values()).map(o => o.mesh);
    
    // Check intersections
    const intersects = this.raycaster.intersectObjects(capsuleMeshes);
    
    if (intersects.length > 0) {
      const capsule = intersects[0].object.userData.capsule as Capsule;
      this.onCapsuleSelected(capsule);
    }
  }
  
  /**
   * Handle capsule selection
   */
  private onCapsuleSelected(capsule: Capsule) {
    console.log('Capsule selected:', capsule);
    
    // Emit custom event for application to handle
    const event = new CustomEvent('capsule-selected', { detail: capsule });
    this.config.container.dispatchEvent(event);
  }
  
  /**
   * Start render loop
   */
  private startRenderLoop() {
    const animate = () => {
      requestAnimationFrame(animate);
      
      // Render scene
      this.renderer.render(this.scene, this.camera);
    };
    
    animate();
  }
  
  /**
   * Dispose viewer and clean up resources
   */
  public dispose() {
    // Disconnect WebSocket
    if (this.websocket) {
      this.websocket.close();
    }
    
    // Remove all capsule overlays
    for (const capsuleId of this.capsuleOverlays.keys()) {
      this.removeCapsuleOverlay(capsuleId);
    }
    
    // Dispose renderer
    this.renderer.dispose();
    
    console.log('ShadowTwinViewer disposed');
  }
}

// ============================================================================
// Export
// ============================================================================

export default ShadowTwinViewer;
