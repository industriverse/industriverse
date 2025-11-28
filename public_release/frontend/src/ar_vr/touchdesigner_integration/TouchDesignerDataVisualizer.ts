/**
 * TouchDesigner Data Visualizer for Generative Capsule Art
 * 
 * Transforms factory metrics into real-time generative visualizations:
 * - Temperature → Color gradient (blue → red)
 * - Pressure → Particle density
 * - Vibration → Displacement noise
 * - Production rate → Animation speed
 * 
 * Based on production patterns from:
 * - https://github.com/benjaminben/td-threejs-tutorial
 * - https://derivative.ca/community-post/tutorial/enhanced-web-workflows-touchdesigner-threejs/63831
 */

import * as THREE from 'three';

// ============================================================================
// Types
// ============================================================================

export interface TouchDesignerConfig {
  scene: THREE.Scene;
  websocketUrl?: string;
  enableAudioReactive?: boolean;
  enableProceduralGeometry?: boolean;
  enableRealTimeTextures?: boolean;
}

export interface FactoryMetrics {
  temperature: number;      // Celsius (0-100)
  pressure: number;          // PSI (0-100)
  vibration: number;         // Hz (0-100)
  productionRate: number;    // Units/hour (0-100)
  noise: number;             // dB (0-100)
  timestamp: number;         // Unix timestamp
}

export interface GenerativeVisual {
  geometry: THREE.BufferGeometry;
  material: THREE.Material;
  texture?: THREE.Texture;
  animation?: GenerativeAnimation;
}

export interface GenerativeAnimation {
  type: 'pulse' | 'rotate' | 'morph' | 'flow' | 'particle_emit';
  speed: number;
  amplitude: number;
  frequency: number;
}

export interface CapsuleVisualization {
  capsuleId: string;
  status: 'critical' | 'warning' | 'active' | 'resolved' | 'dismissed';
  visual: GenerativeVisual;
  metrics: FactoryMetrics;
}

// ============================================================================
// TouchDesignerDataVisualizer
// ============================================================================

export default class TouchDesignerDataVisualizer {
  private config: Required<TouchDesignerConfig>;
  private websocket: WebSocket | null = null;
  private audioContext: AudioContext | null = null;
  private audioAnalyser: AnalyserNode | null = null;
  private audioData: Uint8Array | null = null;

  // Capsule visualizations
  private visualizations: Map<string, CapsuleVisualization> = new Map();

  // Procedural geometry generators
  private geometryGenerators: Map<string, () => THREE.BufferGeometry> = new Map();

  // Material generators
  private materialGenerators: Map<string, (metrics: FactoryMetrics) => THREE.Material> = new Map();

  // Texture cache
  private textureCache: Map<string, THREE.Texture> = new Map();

  // Animation clock
  private clock: THREE.Clock;

  constructor(config: TouchDesignerConfig) {
    this.config = {
      websocketUrl: config.websocketUrl ?? 'ws://localhost:9980',
      enableAudioReactive: config.enableAudioReactive ?? true,
      enableProceduralGeometry: config.enableProceduralGeometry ?? true,
      enableRealTimeTextures: config.enableRealTimeTextures ?? true,
      ...config
    };

    this.clock = new THREE.Clock();

    // Initialize geometry generators
    this.initGeometryGenerators();

    // Initialize material generators
    this.initMaterialGenerators();

    // Connect to TouchDesigner WebSocket
    if (this.config.websocketUrl) {
      this.connectWebSocket();
    }

    // Initialize audio reactive
    if (this.config.enableAudioReactive) {
      this.initAudioReactive();
    }
  }

  /**
   * Initialize procedural geometry generators
   */
  private initGeometryGenerators(): void {
    // Critical: Pulsing sphere with spikes
    this.geometryGenerators.set('critical', () => {
      const geometry = new THREE.IcosahedronGeometry(0.15, 2);
      const positions = geometry.attributes.position;

      // Add spikes
      for (let i = 0; i < positions.count; i++) {
        const vertex = new THREE.Vector3(
          positions.getX(i),
          positions.getY(i),
          positions.getZ(i)
        );

        vertex.normalize().multiplyScalar(0.15 + Math.random() * 0.05);

        positions.setXYZ(i, vertex.x, vertex.y, vertex.z);
      }

      geometry.computeVertexNormals();
      return geometry;
    });

    // Warning: Rotating cube with glow
    this.geometryGenerators.set('warning', () => {
      return new THREE.BoxGeometry(0.2, 0.2, 0.2);
    });

    // Active: Smooth torus with flow
    this.geometryGenerators.set('active', () => {
      return new THREE.TorusGeometry(0.12, 0.05, 16, 100);
    });

    // Resolved: Simple sphere
    this.geometryGenerators.set('resolved', () => {
      return new THREE.SphereGeometry(0.1, 32, 32);
    });

    // Dismissed: Fading octahedron
    this.geometryGenerators.set('dismissed', () => {
      return new THREE.OctahedronGeometry(0.1, 0);
    });
  }

  /**
   * Initialize material generators based on factory metrics
   */
  private initMaterialGenerators(): void {
    // Critical: Temperature-based color gradient
    this.materialGenerators.set('critical', (metrics: FactoryMetrics) => {
      // Map temperature to color (blue → red)
      const temperature = THREE.MathUtils.clamp(metrics.temperature, 0, 100);
      const hue = THREE.MathUtils.mapLinear(temperature, 0, 100, 0.6, 0); // Blue to red
      const color = new THREE.Color().setHSL(hue, 1, 0.5);

      return new THREE.MeshStandardMaterial({
        color,
        emissive: color,
        emissiveIntensity: 0.8,
        roughness: 0.3,
        metalness: 0.7
      });
    });

    // Warning: Pressure-based glow
    this.materialGenerators.set('warning', (metrics: FactoryMetrics) => {
      const pressure = THREE.MathUtils.clamp(metrics.pressure, 0, 100);
      const glowIntensity = THREE.MathUtils.mapLinear(pressure, 0, 100, 0.3, 1);

      return new THREE.MeshStandardMaterial({
        color: 0xffaa33,
        emissive: 0xffaa33,
        emissiveIntensity: glowIntensity,
        roughness: 0.4,
        metalness: 0.5
      });
    });

    // Active: Production rate-based flow
    this.materialGenerators.set('active', (metrics: FactoryMetrics) => {
      return new THREE.MeshStandardMaterial({
        color: 0x33ff33,
        emissive: 0x33ff33,
        emissiveIntensity: 0.5,
        roughness: 0.5,
        metalness: 0.3
      });
    });

    // Resolved: Gray material
    this.materialGenerators.set('resolved', (metrics: FactoryMetrics) => {
      return new THREE.MeshStandardMaterial({
        color: 0x888888,
        emissive: 0x888888,
        emissiveIntensity: 0.2,
        roughness: 0.7,
        metalness: 0.2
      });
    });

    // Dismissed: Dark gray material
    this.materialGenerators.set('dismissed', (metrics: FactoryMetrics) => {
      return new THREE.MeshStandardMaterial({
        color: 0x444444,
        emissive: 0x444444,
        emissiveIntensity: 0.1,
        roughness: 0.8,
        metalness: 0.1,
        transparent: true,
        opacity: 0.5
      });
    });
  }

  /**
   * Connect to TouchDesigner WebSocket server
   */
  private connectWebSocket(): void {
    this.websocket = new WebSocket(this.config.websocketUrl);

    this.websocket.onopen = () => {
      console.log('[TouchDesigner] WebSocket connected');
    };

    this.websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'metrics_update') {
        this.updateMetrics(data.capsuleId, data.metrics);
      } else if (data.type === 'texture_update') {
        this.updateTexture(data.capsuleId, data.textureUrl);
      } else if (data.type === 'geometry_update') {
        this.updateGeometry(data.capsuleId, data.geometryUrl);
      }
    };

    this.websocket.onerror = (error) => {
      console.error('[TouchDesigner] WebSocket error:', error);
    };

    this.websocket.onclose = () => {
      console.log('[TouchDesigner] WebSocket closed, reconnecting...');
      setTimeout(() => this.connectWebSocket(), 5000);
    };
  }

  /**
   * Initialize audio reactive visualization
   */
  private initAudioReactive(): void {
    // Request microphone access for factory noise
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then((stream) => {
        this.audioContext = new AudioContext();
        const source = this.audioContext.createMediaStreamSource(stream);

        this.audioAnalyser = this.audioContext.createAnalyser();
        this.audioAnalyser.fftSize = 256;

        source.connect(this.audioAnalyser);

        this.audioData = new Uint8Array(this.audioAnalyser.frequencyBinCount);

        console.log('[TouchDesigner] Audio reactive initialized');
      })
      .catch((error) => {
        console.warn('[TouchDesigner] Audio access denied:', error);
      });
  }

  /**
   * Create generative visualization for capsule
   */
  createVisualization(
    capsuleId: string,
    status: 'critical' | 'warning' | 'active' | 'resolved' | 'dismissed',
    metrics: FactoryMetrics,
    position: THREE.Vector3
  ): THREE.Mesh {
    // Generate geometry
    const geometryGenerator = this.geometryGenerators.get(status);
    const geometry = geometryGenerator ? geometryGenerator() : new THREE.SphereGeometry(0.1, 32, 32);

    // Generate material
    const materialGenerator = this.materialGenerators.get(status);
    const material = materialGenerator ? materialGenerator(metrics) : new THREE.MeshStandardMaterial({ color: 0xffffff });

    // Create mesh
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.copy(position);
    mesh.userData.type = 'capsule_overlay';
    mesh.userData.capsuleId = capsuleId;
    mesh.userData.status = status;

    // Add to scene
    this.config.scene.add(mesh);

    // Create animation
    const animation = this.createAnimation(status, metrics);

    // Store visualization
    this.visualizations.set(capsuleId, {
      capsuleId,
      status,
      visual: {
        geometry,
        material,
        animation
      },
      metrics
    });

    return mesh;
  }

  /**
   * Create animation based on status and metrics
   */
  private createAnimation(
    status: string,
    metrics: FactoryMetrics
  ): GenerativeAnimation {
    switch (status) {
      case 'critical':
        // Pulse animation (vibration-based)
        return {
          type: 'pulse',
          speed: THREE.MathUtils.mapLinear(metrics.vibration, 0, 100, 1, 5),
          amplitude: THREE.MathUtils.mapLinear(metrics.vibration, 0, 100, 0.1, 0.3),
          frequency: THREE.MathUtils.mapLinear(metrics.vibration, 0, 100, 1, 3)
        };

      case 'warning':
        // Rotate animation (production rate-based)
        return {
          type: 'rotate',
          speed: THREE.MathUtils.mapLinear(metrics.productionRate, 0, 100, 30, 120),
          amplitude: 1,
          frequency: 1
        };

      case 'active':
        // Flow animation (smooth rotation)
        return {
          type: 'flow',
          speed: THREE.MathUtils.mapLinear(metrics.productionRate, 0, 100, 20, 60),
          amplitude: 1,
          frequency: 1
        };

      case 'resolved':
        // Slow pulse
        return {
          type: 'pulse',
          speed: 0.5,
          amplitude: 0.05,
          frequency: 0.5
        };

      case 'dismissed':
        // Fade out
        return {
          type: 'pulse',
          speed: 0.3,
          amplitude: 0.02,
          frequency: 0.3
        };

      default:
        return {
          type: 'pulse',
          speed: 1,
          amplitude: 0.1,
          frequency: 1
        };
    }
  }

  /**
   * Update capsule visualization based on new metrics
   */
  updateMetrics(capsuleId: string, metrics: FactoryMetrics): void {
    const visualization = this.visualizations.get(capsuleId);
    if (!visualization) return;

    // Update metrics
    visualization.metrics = metrics;

    // Regenerate material
    const materialGenerator = this.materialGenerators.get(visualization.status);
    if (materialGenerator) {
      const newMaterial = materialGenerator(metrics);

      // Find mesh in scene
      this.config.scene.traverse((object) => {
        if (object.userData.capsuleId === capsuleId && object instanceof THREE.Mesh) {
          object.material.dispose();
          object.material = newMaterial;
        }
      });

      visualization.visual.material = newMaterial;
    }

    // Update animation
    visualization.visual.animation = this.createAnimation(visualization.status, metrics);
  }

  /**
   * Update capsule texture from TouchDesigner
   */
  private async updateTexture(capsuleId: string, textureUrl: string): Promise<void> {
    const visualization = this.visualizations.get(capsuleId);
    if (!visualization) return;

    // Load texture
    const loader = new THREE.TextureLoader();
    const texture = await loader.loadAsync(textureUrl);

    // Cache texture
    this.textureCache.set(capsuleId, texture);

    // Update material
    this.config.scene.traverse((object) => {
      if (object.userData.capsuleId === capsuleId && object instanceof THREE.Mesh) {
        if (object.material instanceof THREE.MeshStandardMaterial) {
          object.material.map = texture;
          object.material.needsUpdate = true;
        }
      }
    });

    visualization.visual.texture = texture;
  }

  /**
   * Update capsule geometry from TouchDesigner
   */
  private async updateGeometry(capsuleId: string, geometryUrl: string): Promise<void> {
    const visualization = this.visualizations.get(capsuleId);
    if (!visualization) return;

    // Load geometry (OBJ format)
    const response = await fetch(geometryUrl);
    const objText = await response.text();

    // Parse OBJ (simplified, in production use OBJLoader)
    const geometry = this.parseOBJ(objText);

    // Update mesh
    this.config.scene.traverse((object) => {
      if (object.userData.capsuleId === capsuleId && object instanceof THREE.Mesh) {
        object.geometry.dispose();
        object.geometry = geometry;
      }
    });

    visualization.visual.geometry = geometry;
  }

  /**
   * Parse OBJ file (simplified)
   */
  private parseOBJ(objText: string): THREE.BufferGeometry {
    // In production, use THREE.OBJLoader
    // This is a simplified placeholder
    return new THREE.SphereGeometry(0.1, 32, 32);
  }

  /**
   * Update all visualizations (call in render loop)
   */
  update(): void {
    const elapsedTime = this.clock.getElapsedTime();

    // Update audio reactive
    if (this.audioAnalyser && this.audioData) {
      this.audioAnalyser.getByteFrequencyData(this.audioData as any);
    }

    // Update each visualization
    this.visualizations.forEach((visualization, capsuleId) => {
      this.config.scene.traverse((object) => {
        if (object.userData.capsuleId === capsuleId && object instanceof THREE.Mesh) {
          this.updateAnimation(object, visualization.visual.animation, elapsedTime);

          // Audio reactive modulation
          if (this.audioData && visualization.status === 'critical') {
            this.applyAudioReactive(object, this.audioData);
          }
        }
      });
    });
  }

  /**
   * Update animation for mesh
   */
  private updateAnimation(
    mesh: THREE.Mesh,
    animation: GenerativeAnimation | undefined,
    elapsedTime: number
  ): void {
    if (!animation) return;

    switch (animation.type) {
      case 'pulse':
        // Scale pulse
        const scale = 1 + Math.sin(elapsedTime * animation.frequency * Math.PI * 2) * animation.amplitude;
        mesh.scale.set(scale, scale, scale);
        break;

      case 'rotate':
        // Rotation
        mesh.rotation.y = elapsedTime * animation.speed * Math.PI / 180;
        break;

      case 'flow':
        // Smooth rotation
        mesh.rotation.y = elapsedTime * animation.speed * Math.PI / 180;
        mesh.rotation.x = Math.sin(elapsedTime * 0.5) * 0.2;
        break;

      case 'morph':
        // Geometry morphing (placeholder)
        break;

      case 'particle_emit':
        // Particle emission (placeholder)
        break;
    }
  }

  /**
   * Apply audio reactive modulation
   */
  private applyAudioReactive(mesh: THREE.Mesh, audioData: Uint8Array): void {
    // Calculate average frequency
    let sum = 0;
    for (let i = 0; i < audioData.length; i++) {
      sum += audioData[i];
    }
    const average = sum / audioData.length;

    // Map to scale
    const audioScale = THREE.MathUtils.mapLinear(average, 0, 255, 1, 1.3);
    mesh.scale.multiplyScalar(audioScale);

    // Map to emissive intensity
    if (mesh.material instanceof THREE.MeshStandardMaterial) {
      const audioEmissive = THREE.MathUtils.mapLinear(average, 0, 255, 0.5, 1);
      mesh.material.emissiveIntensity = audioEmissive;
    }
  }

  /**
   * Remove visualization
   */
  removeVisualization(capsuleId: string): void {
    const visualization = this.visualizations.get(capsuleId);
    if (!visualization) return;

    // Remove from scene
    this.config.scene.traverse((object) => {
      if (object.userData.capsuleId === capsuleId) {
        this.config.scene.remove(object);

        if (object instanceof THREE.Mesh) {
          object.geometry.dispose();
          if (object.material instanceof THREE.Material) {
            object.material.dispose();
          }
        }
      }
    });

    // Remove from cache
    this.visualizations.delete(capsuleId);
    this.textureCache.delete(capsuleId);
  }

  /**
   * Dispose visualizer
   */
  dispose(): void {
    // Close WebSocket
    if (this.websocket) {
      this.websocket.close();
    }

    // Close audio context
    if (this.audioContext) {
      this.audioContext.close();
    }

    // Remove all visualizations
    this.visualizations.forEach((_, capsuleId) => {
      this.removeVisualization(capsuleId);
    });

    // Clear caches
    this.visualizations.clear();
    this.textureCache.forEach((texture) => texture.dispose());
    this.textureCache.clear();
  }
}
