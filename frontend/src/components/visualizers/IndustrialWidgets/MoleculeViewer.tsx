import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

interface Atom {
    element: string;
    position: [number, number, number];
}

interface Bond {
    source: number; // Index of source atom
    target: number; // Index of target atom
}

interface MoleculeViewerProps {
    atoms: Atom[];
    bonds: Bond[];
    width?: number;
    height?: number;
}

const ELEMENT_COLORS: Record<string, number> = {
    H: 0xffffff,
    C: 0x333333,
    O: 0xff0000,
    N: 0x0000ff,
    Fe: 0xffa500, // Iron
    Nd: 0x8a2be2, // Neodymium (Rare Earth)
    Dy: 0x00ced1  // Dysprosium (Rare Earth)
};

const ELEMENT_SIZES: Record<string, number> = {
    H: 0.3,
    C: 0.5,
    O: 0.5,
    N: 0.5,
    Fe: 0.7,
    Nd: 0.8,
    Dy: 0.8
};

export const MoleculeViewer: React.FC<MoleculeViewerProps> = ({ atoms, bonds, width = 400, height = 300 }) => {
    const mountRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!mountRef.current) return;

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0f172a); // Slate-900

        const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000);
        camera.position.set(0, 0, 10);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(width, height);
        mountRef.current.appendChild(renderer.domElement);

        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;

        // Create Atoms
        atoms.forEach((atom) => {
            const color = ELEMENT_COLORS[atom.element] || 0xcccccc;
            const size = ELEMENT_SIZES[atom.element] || 0.5;

            const geometry = new THREE.SphereGeometry(size, 32, 32);
            const material = new THREE.MeshPhysicalMaterial({
                color: color,
                metalness: 0.2,
                roughness: 0.3,
                clearcoat: 0.8
            });
            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.set(...atom.position);
            scene.add(mesh);
        });

        // Create Bonds
        bonds.forEach((bond) => {
            const start = new THREE.Vector3(...atoms[bond.source].position);
            const end = new THREE.Vector3(...atoms[bond.target].position);

            const direction = new THREE.Vector3().subVectors(end, start);
            const length = direction.length();

            const geometry = new THREE.CylinderGeometry(0.1, 0.1, length, 8);
            const material = new THREE.MeshStandardMaterial({ color: 0x888888 });

            const cylinder = new THREE.Mesh(geometry, material);

            // Position and Orient Cylinder
            const midPoint = new THREE.Vector3().addVectors(start, end).multiplyScalar(0.5);
            cylinder.position.copy(midPoint);
            cylinder.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), direction.clone().normalize());

            scene.add(cylinder);
        });

        // Lights
        const ambientLight = new THREE.AmbientLight(0x404040);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffffff, 1);
        dirLight.position.set(5, 5, 5);
        scene.add(dirLight);

        const backLight = new THREE.DirectionalLight(0x445566, 0.5);
        backLight.position.set(-5, -5, -10);
        scene.add(backLight);

        const animate = () => {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        };
        animate();

        return () => {
            if (mountRef.current) {
                mountRef.current.removeChild(renderer.domElement);
            }
            renderer.dispose();
        };
    }, [atoms, bonds, width, height]);

    return <div ref={mountRef} className="rounded-lg overflow-hidden border border-slate-700 shadow-lg" />;
};
