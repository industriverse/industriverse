/**
 * TouchDesigner Data Visualizer
 * 
 * Generative art visualization of capsule metrics
 * Transforms factory data into living, breathing visuals
 */

import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';

export interface CapsuleMetrics {
  temperature?: number; // 0-100°C
  pressure?: number; // 0-100 PSI
  vibration?: number; // 0-100 Hz
  humidity?: number; // 0-100%
  power?: number; // 0-100 kW
  speed?: number; // 0-100 RPM
}

export interface TouchDesignerVisualizerProps {
  capsuleId: string;
  metrics: CapsuleMetrics;
  status: 'active' | 'warning' | 'critical' | 'resolved' | 'dismissed';
  enabled?: boolean;
}

export function TouchDesignerVisualizer({
  capsuleId,
  metrics,
  status,
  enabled = true,
}: TouchDesignerVisualizerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const meshRef = useRef<THREE.Mesh | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    if (!enabled || !containerRef.current) {
      return;
    }

    initializeThreeJS();

    return () => {
      cleanup();
    };
  }, [enabled]);

  useEffect(() => {
    if (isInitialized && meshRef.current) {
      updateVisualization();
    }
  }, [metrics, status, isInitialized]);

  /**
   * Initialize Three.js scene
   */
  const initializeThreeJS = () => {
    if (!containerRef.current) return;

    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight;

    // Create scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0a);
    sceneRef.current = scene;

    // Create camera
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.z = 3;
    cameraRef.current = camera;

    // Create renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Create initial geometry based on status
    createGeometry();

    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0xffffff, 1);
    pointLight.position.set(5, 5, 5);
    scene.add(pointLight);

    // Start animation loop
    animate();

    setIsInitialized(true);
    console.log('[TouchDesigner] Initialized for capsule:', capsuleId);
  };

  /**
   * Create geometry based on capsule status
   */
  const createGeometry = () => {
    if (!sceneRef.current) return;

    // Remove existing mesh
    if (meshRef.current) {
      sceneRef.current.remove(meshRef.current);
      meshRef.current.geometry.dispose();
      (meshRef.current.material as THREE.Material).dispose();
    }

    let geometry: THREE.BufferGeometry;

    switch (status) {
      case 'critical':
        // Icosphere with spikes (vibration-based)
        geometry = new THREE.IcosahedronGeometry(1, 2);
        break;

      case 'warning':
        // Rotating cube (pressure-based)
        geometry = new THREE.BoxGeometry(1, 1, 1);
        break;

      case 'active':
        // Smooth torus (production rate flow)
        geometry = new THREE.TorusGeometry(0.7, 0.3, 16, 100);
        break;

      case 'resolved':
        // Simple sphere (slow pulse)
        geometry = new THREE.SphereGeometry(1, 32, 32);
        break;

      case 'dismissed':
        // Fading octahedron
        geometry = new THREE.OctahedronGeometry(1, 0);
        break;

      default:
        geometry = new THREE.SphereGeometry(1, 32, 32);
    }

    // Create material with metrics-driven properties
    const material = new THREE.MeshPhongMaterial({
      color: getStatusColor(status),
      emissive: getStatusColor(status),
      emissiveIntensity: 0.3,
      shininess: 100,
      transparent: status === 'dismissed',
      opacity: status === 'dismissed' ? 0.3 : 1.0,
    });

    const mesh = new THREE.Mesh(geometry, material);
    sceneRef.current.add(mesh);
    meshRef.current = mesh;
  };

  /**
   * Get color based on status
   */
  const getStatusColor = (status: string): number => {
    switch (status) {
      case 'critical':
        return 0xff3333; // Red
      case 'warning':
        return 0xffaa33; // Amber
      case 'active':
        return 0x33ff33; // Green
      case 'resolved':
        return 0x888888; // Gray
      case 'dismissed':
        return 0x444444; // Dark gray
      default:
        return 0xffffff; // White
    }
  };

  /**
   * Update visualization based on metrics
   */
  const updateVisualization = () => {
    if (!meshRef.current) return;

    const mesh = meshRef.current;
    const material = mesh.material as THREE.MeshPhongMaterial;

    // Temperature → Color gradient (blue to red)
    if (metrics.temperature !== undefined) {
      const temp = metrics.temperature / 100; // Normalize to 0-1
      const color = new THREE.Color();
      color.setHSL(0.6 - temp * 0.6, 1.0, 0.5); // Blue (0.6) to Red (0.0)
      material.color = color;
      material.emissive = color;
    }

    // Pressure → Glow intensity
    if (metrics.pressure !== undefined) {
      const pressure = metrics.pressure / 100; // Normalize to 0-1
      material.emissiveIntensity = 0.3 + pressure * 0.7; // 0.3-1.0
    }

    // Vibration → Pulse amplitude (handled in animate loop)
    // Speed → Rotation speed (handled in animate loop)
  };

  /**
   * Animation loop
   */
  const animate = () => {
    if (!sceneRef.current || !cameraRef.current || !rendererRef.current) {
      return;
    }

    animationFrameRef.current = requestAnimationFrame(animate);

    // Rotate mesh
    if (meshRef.current) {
      const baseRotationSpeed = 0.01;
      const speedMultiplier = metrics.speed ? metrics.speed / 50 : 1; // 0-2x speed
      meshRef.current.rotation.x += baseRotationSpeed * speedMultiplier;
      meshRef.current.rotation.y += baseRotationSpeed * speedMultiplier;

      // Pulse effect based on vibration
      if (metrics.vibration !== undefined) {
        const vibrationIntensity = metrics.vibration / 100; // 0-1
        const pulseAmplitude = 0.1 + vibrationIntensity * 0.2; // 0.1-0.3
        const scale = 1.0 + Math.sin(Date.now() * 0.003) * pulseAmplitude;
        meshRef.current.scale.set(scale, scale, scale);
      }

      // Critical status: Add shaking effect
      if (status === 'critical') {
        const shake = 0.05;
        meshRef.current.position.x = (Math.random() - 0.5) * shake;
        meshRef.current.position.y = (Math.random() - 0.5) * shake;
      } else {
        meshRef.current.position.set(0, 0, 0);
      }
    }

    // Render scene
    rendererRef.current.render(sceneRef.current, cameraRef.current);
  };

  /**
   * Cleanup Three.js resources
   */
  const cleanup = () => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }

    if (meshRef.current) {
      meshRef.current.geometry.dispose();
      (meshRef.current.material as THREE.Material).dispose();
    }

    if (rendererRef.current && containerRef.current) {
      containerRef.current.removeChild(rendererRef.current.domElement);
      rendererRef.current.dispose();
      rendererRef.current = null;
    }

    sceneRef.current = null;
    cameraRef.current = null;
    setIsInitialized(false);
  };

  return (
    <div
      ref={containerRef}
      className="w-full h-64 rounded-lg border border-border overflow-hidden"
      style={{ minHeight: '256px' }}
    >
      {!isInitialized && (
        <div className="flex items-center justify-center h-full bg-muted">
          <span className="text-muted-foreground text-sm">Loading visualization...</span>
        </div>
      )}
    </div>
  );
}
