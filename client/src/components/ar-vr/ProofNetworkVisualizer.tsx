/**
 * Proof Network Visualizer
 * 
 * 3D visualization of Shadow Twin Consensus Network
 * Shows real-time predictor status and consensus flow
 */

import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { getShadowTwinConsensusClient } from '@/services/ShadowTwinConsensusClient';

export interface ProofNetworkVisualizerProps {
  enabled?: boolean;
  showMetrics?: boolean;
}

interface NodeData {
  id: string;
  name: string;
  position: [number, number, number];
  status: 'online' | 'offline' | 'syncing';
  latency?: number;
}

export function ProofNetworkVisualizer({
  enabled = true,
  showMetrics = true,
}: ProofNetworkVisualizerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const nodesRef = useRef<Map<string, THREE.Mesh>>(new Map());
  const linesRef = useRef<THREE.Line[]>([]);
  const animationFrameRef = useRef<number | null>(null);

  const [isInitialized, setIsInitialized] = useState(false);
  const [nodes, setNodes] = useState<NodeData[]>([
    { id: 'primary', name: 'Integration Bridge', position: [0, 0, 0], status: 'online' },
    { id: 'controller', name: 'Controller', position: [0, -2, 0], status: 'online' },
  ]);
  const [pct, setPct] = useState<number>(0.0);
  const [consensusStatus, setConsensusStatus] = useState<'idle' | 'processing' | 'approved' | 'rejected'>('idle');

  useEffect(() => {
    if (!enabled || !containerRef.current) {
      return;
    }

    initializeThreeJS();
    updatePredictorStatus();

    // Poll predictor status every 5 seconds
    const statusInterval = setInterval(updatePredictorStatus, 5000);

    return () => {
      cleanup();
      clearInterval(statusInterval);
    };
  }, [enabled]);

  useEffect(() => {
    if (isInitialized) {
      updateNodeVisuals();
    }
  }, [nodes, isInitialized]);

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
    camera.position.set(3, 3, 5);
    cameraRef.current = camera;

    // Create renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Add orbit controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controlsRef.current = controls;

    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0xffffff, 1);
    pointLight.position.set(5, 5, 5);
    scene.add(pointLight);

    // Create nodes
    createNodes();

    // Start animation loop
    animate();

    setIsInitialized(true);
    console.log('[ProofNetworkVisualizer] Initialized');
  };

  /**
   * Create network nodes
   */
  const createNodes = () => {
    if (!sceneRef.current) return;

    const geometry = new THREE.SphereGeometry(0.3, 32, 32);

    nodes.forEach((node) => {
      const material = new THREE.MeshPhongMaterial({
        color: getNodeColor(node.status),
        emissive: getNodeColor(node.status),
        emissiveIntensity: 0.5,
        shininess: 100,
      });

      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.set(...node.position);
      sceneRef.current!.add(mesh);
      nodesRef.current.set(node.id, mesh);

      // Add label
      createLabel(node.name, node.position);
    });

    // Create connections
    createConnections();
  };

  /**
   * Create label for node
   */
  const createLabel = (text: string, position: [number, number, number]) => {
    // Create canvas for text
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d')!;
    canvas.width = 256;
    canvas.height = 64;

    context.fillStyle = '#ffffff';
    context.font = 'bold 24px Arial';
    context.textAlign = 'center';
    context.fillText(text, 128, 40);

    // Create texture from canvas
    const texture = new THREE.CanvasTexture(canvas);

    // Create sprite
    const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
    const sprite = new THREE.Sprite(spriteMaterial);
    sprite.position.set(position[0], position[1] + 0.6, position[2]);
    sprite.scale.set(1, 0.25, 1);

    sceneRef.current!.add(sprite);
  };

  /**
   * Create connections between nodes
   */
  const createConnections = () => {
    if (!sceneRef.current || nodes.length < 2) return;

    const lineMaterial = new THREE.LineBasicMaterial({ color: 0x00ffff });

    // Connect all secondary nodes to primary
    const primaryNode = nodes[0];

    nodes.slice(1).forEach((node) => {
      const points = [
        new THREE.Vector3(...primaryNode.position),
        new THREE.Vector3(...node.position),
      ];

      const geometry = new THREE.BufferGeometry().setFromPoints(points);
      const line = new THREE.Line(geometry, lineMaterial);

      sceneRef.current!.add(line);
      linesRef.current.push(line);
    });
  };

  /**
   * Update node visuals based on status
   */
  const updateNodeVisuals = () => {
    nodes.forEach((node) => {
      const mesh = nodesRef.current.get(node.id);
      if (mesh) {
        const material = mesh.material as THREE.MeshPhongMaterial;
        const color = getNodeColor(node.status);
        material.color.setHex(color);
        material.emissive.setHex(color);
      }
    });
  };

  /**
   * Get node color based on status
   */
  const getNodeColor = (status: string): number => {
    switch (status) {
      case 'online':
        return 0x00ff00; // Green
      case 'syncing':
        return 0xffaa00; // Amber
      case 'offline':
        return 0xff0000; // Red
      default:
        return 0x888888; // Gray
    }
  };

  /**
   * Update predictor status from consensus client
   */
  const updatePredictorStatus = async () => {
    try {
      const client = getShadowTwinConsensusClient();
      const status = await client.getPredictorStatus();

      setNodes((prevNodes) =>
        prevNodes.map((node) => ({
          ...node,
          status: status[node.id]?.status || 'offline',
          latency: status[node.id]?.latency,
        }))
      );
    } catch (error) {
      console.error('[ProofNetworkVisualizer] Failed to update status:', error);
    }
  };

  /**
   * Animation loop
   */
  const animate = () => {
    if (!sceneRef.current || !cameraRef.current || !rendererRef.current) {
      return;
    }

    animationFrameRef.current = requestAnimationFrame(animate);

    // Update controls
    if (controlsRef.current) {
      controlsRef.current.update();
    }

    // Rotate nodes slowly
    nodesRef.current.forEach((mesh) => {
      mesh.rotation.y += 0.01;
    });

    // Pulse effect based on consensus status
    if (consensusStatus === 'processing') {
      const scale = 1.0 + Math.sin(Date.now() * 0.005) * 0.1;
      nodesRef.current.forEach((mesh) => {
        mesh.scale.set(scale, scale, scale);
      });
    } else {
      nodesRef.current.forEach((mesh) => {
        mesh.scale.set(1, 1, 1);
      });
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

    nodesRef.current.forEach((mesh) => {
      mesh.geometry.dispose();
      (mesh.material as THREE.Material).dispose();
    });
    nodesRef.current.clear();

    linesRef.current.forEach((line) => {
      line.geometry.dispose();
      (line.material as THREE.Material).dispose();
    });
    linesRef.current = [];

    if (rendererRef.current && containerRef.current) {
      containerRef.current.removeChild(rendererRef.current.domElement);
      rendererRef.current.dispose();
      rendererRef.current = null;
    }

    if (controlsRef.current) {
      controlsRef.current.dispose();
      controlsRef.current = null;
    }

    sceneRef.current = null;
    cameraRef.current = null;
    setIsInitialized(false);
  };

  return (
    <div className="relative w-full h-full">
      {/* 3D Container */}
      <div
        ref={containerRef}
        className="w-full h-full rounded-lg border border-border overflow-hidden"
        style={{ minHeight: '400px' }}
      >
        {!isInitialized && (
          <div className="flex items-center justify-center h-full bg-muted">
            <span className="text-muted-foreground text-sm">Loading network visualization...</span>
          </div>
        )}
      </div>

      {/* Metrics Overlay */}
      {showMetrics && isInitialized && (
        <div className="absolute top-4 left-4 bg-background/90 backdrop-blur-sm border border-border rounded-lg p-4 max-w-xs">
          <h3 className="font-semibold text-sm mb-2">🔮 Proof Economy Network</h3>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Status:</span>
              <span className="font-medium capitalize">{consensusStatus}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">PCT:</span>
              <span className="font-medium">{(pct * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Threshold:</span>
              <span className="font-medium">≥90%</span>
            </div>
          </div>
          <hr className="my-2 border-border" />
          <div className="space-y-1">
            {nodes.map((node) => (
              <div key={node.id} className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground">{node.name}:</span>
                <div className="flex items-center gap-2">
                  <div
                    className={`h-2 w-2 rounded-full ${
                      node.status === 'online'
                        ? 'bg-green-400'
                        : node.status === 'syncing'
                        ? 'bg-amber-400'
                        : 'bg-red-400'
                    }`}
                  />
                  {node.latency && <span className="text-muted-foreground">{node.latency}ms</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
