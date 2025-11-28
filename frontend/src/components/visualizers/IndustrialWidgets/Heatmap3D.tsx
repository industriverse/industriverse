import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

interface Heatmap3DProps {
    data: number[][]; // 2D array of values
    width?: number;
    height?: number;
    colorScale?: string[]; // Simple gradient colors
}

export const Heatmap3D: React.FC<Heatmap3DProps> = ({ data, width = 400, height = 300 }) => {
    const mountRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!mountRef.current) return;

        // Scene setup
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x1a1a1a); // Dark industrial background

        // Camera
        const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000);
        camera.position.set(20, 20, 20);
        camera.lookAt(0, 0, 0);

        // Renderer
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(width, height);
        mountRef.current.appendChild(renderer.domElement);

        // Controls
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;

        // Geometry generation from data
        const rows = data.length;
        const cols = data[0].length;
        const geometry = new THREE.PlaneGeometry(20, 20, cols - 1, rows - 1);

        // Manipulate vertices based on data
        const count = geometry.attributes.position.count;
        for (let i = 0; i < count; i++) {
            const x = i % cols;
            const y = Math.floor(i / cols);
            const value = data[y] ? data[y][x] : 0;

            // Set Z height based on value
            geometry.attributes.position.setZ(i, value * 5); // Scale factor
        }

        geometry.computeVertexNormals();

        // Material (Wireframe + Solid for "Cyber" look)
        const material = new THREE.MeshPhongMaterial({
            color: 0x00ffcc,
            side: THREE.DoubleSide,
            wireframe: false,
            flatShading: true,
            shininess: 80
        });

        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        // Wireframe overlay
        const wireframe = new THREE.WireframeGeometry(geometry);
        const line = new THREE.LineSegments(wireframe);
        (line.material as THREE.LineBasicMaterial).color.setHex(0x004433);
        scene.add(line);

        // Lights
        const light = new THREE.PointLight(0xffffff, 1, 100);
        light.position.set(10, 10, 10);
        scene.add(light);
        const ambientLight = new THREE.AmbientLight(0x404040);
        scene.add(ambientLight);

        // Animation Loop
        const animate = () => {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        };
        animate();

        // Cleanup
        return () => {
            if (mountRef.current) {
                mountRef.current.removeChild(renderer.domElement);
            }
            geometry.dispose();
            material.dispose();
            renderer.dispose();
        };
    }, [data, width, height]);

    return <div ref={mountRef} className="rounded-lg overflow-hidden border border-slate-700 shadow-lg" />;
};
