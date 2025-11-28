import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Stars, Sphere } from '@react-three/drei';
import * as THREE from 'three';

const DysonShell = () => {
    const meshRef = useRef<THREE.Mesh>(null);

    useFrame((state, delta) => {
        if (meshRef.current) {
            meshRef.current.rotation.y += delta * 0.05;
            meshRef.current.rotation.x += delta * 0.02;
        }
    });

    return (
        <Sphere args={[12, 32, 32]} ref={meshRef}>
            <meshStandardMaterial
                color="#BC13FE" // Nebula Purple
                wireframe
                transparent
                opacity={0.1}
                emissive="#BC13FE"
                emissiveIntensity={0.2}
            />
        </Sphere>
    );
};

const RotatingStars = () => {
    const starsRef = useRef<THREE.Group>(null);
    useFrame((state, delta) => {
        if (starsRef.current) {
            starsRef.current.rotation.y -= delta * 0.01;
        }
    });
    return (
        <group ref={starsRef}>
            <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
        </group>
    );
}

const SphereBackground: React.FC = () => {
    return (
        <div className="fixed inset-0 -z-10 bg-void">
            <Canvas camera={{ position: [0, 0, 20], fov: 60 }}>
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} intensity={1} color="#FFD700" /> {/* Solar Gold */}
                <RotatingStars />
                <DysonShell />
                <fog attach="fog" args={['#050505', 10, 50]} />
            </Canvas>
            {/* Overlay Gradient for readability */}
            <div className="absolute inset-0 bg-gradient-to-t from-void via-transparent to-void opacity-80 pointer-events-none" />
        </div>
    );
};

export default SphereBackground;
