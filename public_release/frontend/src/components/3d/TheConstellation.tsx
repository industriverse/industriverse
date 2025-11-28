// @ts-nocheck
import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { useSystemPulse } from '@/hooks/useSystemPulse';

interface Node {
    id: string;
    utid: string;
    status?: string;
    proof_score?: number;
    position: THREE.Vector3;
    isRoot?: boolean;
}

interface GraphData {
    nodes: any[];
    edges: any[];
}

export function TheConstellation() {
    const containerRef = useRef<HTMLDivElement>(null);
    const [data, setData] = useState<GraphData | null>(null);
    const [hoveredNode, setHoveredNode] = useState<Node | null>(null);
    const { lastEvent } = useSystemPulse();

    // Three.js refs
    const sceneRef = useRef<THREE.Scene | null>(null);
    const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
    const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
    const nodesRef = useRef<Map<string, THREE.Mesh>>(new Map());
    const edgesRef = useRef<THREE.LineSegments | null>(null);
    const frameRef = useRef<number>(0);

    // Listen for new proofs and add to graph
    useEffect(() => {
        if (lastEvent && lastEvent.type === 'proof_generated' && lastEvent.proof && sceneRef.current) {
            const proof = lastEvent.proof;
            const newNode: Node = {
                id: proof.proof_id,
                utid: proof.utid,
                status: proof.metadata.status,
                proof_score: proof.metadata.proof_score,
                position: new THREE.Vector3(
                    (Math.random() - 0.5) * 10,
                    (Math.random() - 0.5) * 10,
                    (Math.random() - 0.5) * 10
                )
            };

            // Add mesh
            const geometry = new THREE.IcosahedronGeometry(1, 1);
            const material = new THREE.MeshStandardMaterial({
                color: 0x00f0ff,
                emissive: 0x008080,
                emissiveIntensity: 0.8,
                roughness: 0.2,
                metalness: 0.8
            });
            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.copy(newNode.position);
            const scale = 0.5 + (newNode.proof_score || 0.5);
            mesh.scale.set(scale, scale, scale);
            mesh.userData = { node: newNode };

            sceneRef.current.add(mesh);
            nodesRef.current.set(newNode.id, mesh);

            // Connect to a random existing node (simulate DAG)
            const existingNodes = Array.from(nodesRef.current.keys());
            if (existingNodes.length > 1) { // > 1 because we just added one
                const targetId = existingNodes[Math.floor(Math.random() * (existingNodes.length - 1))];
                // Note: Updating edges geometry dynamically is complex, skipping for this iteration
                // Ideally we'd rebuild the line geometry or use a dynamic line buffer
            }
        }
    }, [lastEvent]);

    // Fetch Data
    useEffect(() => {
        const fetchData = async () => {
            try {
                // Using the graph endpoint we saw in the backend controller
                const res = await fetch('/v1/proofs/graph?limit=50');
                if (res.ok) {
                    const json = await res.json();
                    setData(json);
                } else {
                    // Fallback mock data if endpoint fails or is empty
                    generateMockGalaxy();
                }
            } catch (e) {
                generateMockGalaxy();
            }
        };
        fetchData();
    }, []);

    const generateMockGalaxy = () => {
        const nodes = [];
        const edges = [];
        const count = 30;

        // Create a root
        nodes.push({ id: 'genesis', utid: 'UTID:GENESIS', status: 'verified', proof_score: 1.0, anchors: [] });

        for (let i = 1; i < count; i++) {
            const parentId = i === 1 ? 'genesis' : nodes[Math.floor(Math.random() * i)].id;
            nodes.push({
                id: `proof-${i}`,
                utid: `UTID:NODE:${Math.floor(Math.random() * 5)}`,
                status: Math.random() > 0.8 ? 'pending' : 'verified',
                proof_score: 0.5 + Math.random() * 0.5,
            });
            edges.push({ from: parentId, to: `proof-${i}` });
        }
        setData({ nodes, edges });
    };

    // Initialize Three.js
    useEffect(() => {
        if (!containerRef.current || !data) return;

        const width = containerRef.current.clientWidth;
        const height = containerRef.current.clientHeight;

        // Scene Setup
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x050505, 0.02);
        sceneRef.current = scene;

        const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
        camera.position.set(0, 20, 40);
        cameraRef.current = camera;

        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        containerRef.current.innerHTML = '';
        containerRef.current.appendChild(renderer.domElement);
        rendererRef.current = renderer;

        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.autoRotate = true;
        controls.autoRotateSpeed = 0.5;

        // Lighting
        const ambient = new THREE.AmbientLight(0x404040);
        scene.add(ambient);
        const point = new THREE.PointLight(0xffaa00, 2, 100);
        point.position.set(0, 0, 0);
        scene.add(point);

        // Process Data into 3D positions (Simple Force Layout or Spiral)
        const nodeMap = new Map<string, Node>();
        const processedNodes: Node[] = data.nodes.map((n, i) => {
            // Spiral layout
            const angle = i * 0.5;
            const radius = 2 + i * 0.5;
            const x = Math.cos(angle) * radius;
            const z = Math.sin(angle) * radius;
            const y = (Math.random() - 0.5) * 5;

            const node = {
                ...n,
                position: new THREE.Vector3(x, y, z),
                isRoot: i === 0
            };
            nodeMap.set(n.id, node);
            return node;
        });

        // Create Node Meshes
        const geometry = new THREE.IcosahedronGeometry(1, 1); // Low poly crystal look
        const materialVerified = new THREE.MeshStandardMaterial({
            color: 0x00f0ff,
            emissive: 0x008080,
            emissiveIntensity: 0.5,
            roughness: 0.2,
            metalness: 0.8
        });
        const materialPending = new THREE.MeshStandardMaterial({
            color: 0xffaa00,
            emissive: 0xff4400,
            emissiveIntensity: 0.5,
            roughness: 0.5,
            metalness: 0.5
        });

        processedNodes.forEach(node => {
            const mesh = new THREE.Mesh(geometry, node.status === 'verified' ? materialVerified : materialPending);
            mesh.position.copy(node.position);

            // Scale based on score
            const scale = 0.5 + (node.proof_score || 0.5);
            mesh.scale.set(scale, scale, scale);

            mesh.userData = { node }; // Store data for raycasting
            scene.add(mesh);
            nodesRef.current.set(node.id, mesh);
        });

        // Create Edges
        const lineGeometry = new THREE.BufferGeometry();
        const points: number[] = [];
        data.edges.forEach((e: any) => {
            const source = nodeMap.get(e.from);
            const target = nodeMap.get(e.to);
            if (source && target) {
                points.push(source.position.x, source.position.y, source.position.z);
                points.push(target.position.x, target.position.y, target.position.z);
            }
        });
        lineGeometry.setAttribute('position', new THREE.Float32BufferAttribute(points, 3));
        const lineMaterial = new THREE.LineBasicMaterial({
            color: 0xffffff,
            transparent: true,
            opacity: 0.1,
            blending: THREE.AdditiveBlending
        });
        const lines = new THREE.LineSegments(lineGeometry, lineMaterial);
        scene.add(lines);
        edgesRef.current = lines;

        // Animation Loop
        const animate = () => {
            frameRef.current = requestAnimationFrame(animate);
            controls.update();

            // Gentle float animation
            const time = Date.now() * 0.001;
            nodesRef.current.forEach((mesh, _) => {
                mesh.rotation.x += 0.005;
                mesh.rotation.y += 0.01;
                mesh.position.y += Math.sin(time + mesh.position.x) * 0.002;
            });

            renderer.render(scene, camera);
        };
        animate();

        // Raycaster for hover
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        const onMouseMove = (event: MouseEvent) => {
            const rect = containerRef.current?.getBoundingClientRect();
            if (!rect) return;
            mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(Array.from(nodesRef.current.values()));

            if (intersects.length > 0) {
                const node = intersects[0].object.userData.node;
                setHoveredNode(node);
                document.body.style.cursor = 'pointer';
            } else {
                setHoveredNode(null);
                document.body.style.cursor = 'default';
            }
        };

        containerRef.current.addEventListener('mousemove', onMouseMove);

        return () => {
            cancelAnimationFrame(frameRef.current);
            containerRef.current?.removeEventListener('mousemove', onMouseMove);
            renderer.dispose();
            controls.dispose();
        };
    }, [data]);

    return (
        <div className="relative w-full h-[400px] group">
            {/* 3D Canvas Container */}
            <div ref={containerRef} className="w-full h-full rounded-lg border border-white/10 bg-black/40 backdrop-blur-sm overflow-hidden" />

            {/* Overlay Title */}
            <div className="absolute top-4 left-4 pointer-events-none">
                <h3 className="text-dyson-amber font-mono text-xs tracking-widest uppercase">The Constellation</h3>
                <p className="text-[10px] text-muted-foreground">Proof Lineage DAG</p>
            </div>

            {/* Hover Tooltip */}
            {hoveredNode && (
                <div className="absolute bottom-4 left-4 bg-black/80 border border-dyson-plasma/50 p-3 rounded backdrop-blur-md max-w-xs animate-in fade-in slide-in-from-bottom-2 pointer-events-none">
                    <div className="text-dyson-plasma font-mono text-xs mb-1">{hoveredNode.id}</div>
                    <div className="text-[10px] text-muted-foreground mb-2">{hoveredNode.utid}</div>
                    <div className="flex gap-2 text-[10px]">
                        <span className="text-dyson-teal">SCORE: {(hoveredNode.proof_score || 0).toFixed(2)}</span>
                        <span className="text-white/50">{hoveredNode.status?.toUpperCase()}</span>
                    </div>
                </div>
            )}
        </div>
    );
}
