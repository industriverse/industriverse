import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import MediaPipeHandsController, { GestureData } from '../ar_vr/mediapipe_integration/MediaPipeHandsController';
import TouchDesignerDataVisualizer from '../ar_vr/touchdesigner_integration/TouchDesignerDataVisualizer';
import { useSystemPulse } from '../hooks/useSystemPulse';

interface AmbientCanvasProps {
    onGesture?: (gesture: string) => void;
}

export default function AmbientCanvas({ onGesture }: AmbientCanvasProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const { lastEvent } = useSystemPulse();

    // Refs for systems
    const handsController = useRef<MediaPipeHandsController | null>(null);
    const visualizer = useRef<TouchDesignerDataVisualizer | null>(null);
    const sceneRef = useRef<THREE.Scene | null>(null);
    const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
    const rendererRef = useRef<THREE.WebGLRenderer | null>(null);

    useEffect(() => {
        if (!containerRef.current) return;

        // 1. Setup Three.js Scene
        const scene = new THREE.Scene();
        sceneRef.current = scene;

        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 2; // Position camera to see the "screen" plane
        cameraRef.current = camera;

        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.domElement.style.position = 'absolute';
        renderer.domElement.style.top = '0';
        renderer.domElement.style.left = '0';
        renderer.domElement.style.pointerEvents = 'none'; // Let clicks pass through
        containerRef.current.appendChild(renderer.domElement);
        rendererRef.current = renderer;

        // Lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);
        const pointLight = new THREE.PointLight(0xffffff, 1);
        pointLight.position.set(5, 5, 5);
        scene.add(pointLight);

        // 2. Initialize Ambient Intelligence Systems
        const videoElement = document.createElement('video'); // Hidden video for MediaPipe
        videoElement.style.display = 'none';
        document.body.appendChild(videoElement);

        try {
            handsController.current = new MediaPipeHandsController({
                videoElement: videoElement,
                scene: scene,
                camera: camera,
                onGesture: (data: GestureData) => {
                    if (onGesture) onGesture(data.type);
                },
                enableDepthControl: false // Simplify for 2D overlay feel
            });

            visualizer.current = new TouchDesignerDataVisualizer({
                scene: scene,
                enableAudioReactive: false // Disable audio for now to avoid permission prompts on load
            });

            handsController.current.start();
            console.log("Ambient Intelligence Systems Active");

        } catch (e) {
            console.warn("Failed to init Ambient Intelligence:", e);
        }

        // 3. Animation Loop
        let animationFrameId: number;
        const animate = () => {
            animationFrameId = requestAnimationFrame(animate);

            if (visualizer.current) visualizer.current.update();

            renderer.render(scene, camera);
        };
        animate();

        // Handle Resize
        const handleResize = () => {
            if (cameraRef.current && rendererRef.current) {
                cameraRef.current.aspect = window.innerWidth / window.innerHeight;
                cameraRef.current.updateProjectionMatrix();
                rendererRef.current.setSize(window.innerWidth, window.innerHeight);
            }
        };
        window.addEventListener('resize', handleResize);

        // Cleanup
        return () => {
            cancelAnimationFrame(animationFrameId);
            window.removeEventListener('resize', handleResize);
            handsController.current?.stop();
            visualizer.current?.dispose();

            if (rendererRef.current && containerRef.current) {
                containerRef.current.removeChild(rendererRef.current.domElement);
            }
            if (videoElement.parentNode) {
                videoElement.parentNode.removeChild(videoElement);
            }
        };
    }, []);

    // React to system pulse events for visualizer
    useEffect(() => {
        if (lastEvent && lastEvent.type === 'capsule_update' && visualizer.current) {
            // Create a visual effect at a random position for now
            // In a real app, we'd map capsule ID to a specific 3D position
            const position = new THREE.Vector3(
                (Math.random() - 0.5) * 4,
                (Math.random() - 0.5) * 2,
                0
            );

            visualizer.current.createVisualization(
                lastEvent.capsule_id,
                lastEvent.status as any,
                {
                    temperature: 50,
                    pressure: 50,
                    vibration: 50,
                    productionRate: 50,
                    noise: 50,
                    timestamp: Date.now()
                },
                position
            );
        }
    }, [lastEvent]);

    return <div ref={containerRef} className="fixed inset-0 z-50 pointer-events-none" />;
}
