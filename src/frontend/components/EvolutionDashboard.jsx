import React, { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text } from '@react-three/drei';

function ExperimentNode({ position, color, label }) {
    const mesh = useRef();
    useFrame((state, delta) => (mesh.current.rotation.x += delta * 0.2));

    return (
        <group position={position}>
            <mesh ref={mesh}>
                <sphereGeometry args={[0.5, 32, 32]} />
                <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.5} />
            </mesh>
            <Text position={[0, 0.8, 0]} fontSize={0.3} color="white">
                {label}
            </Text>
        </group>
    );
}

export default function EvolutionDashboard() {
    return (
        <div style={{ width: '100%', height: '100vh', background: '#000' }}>
            <div style={{ position: 'absolute', top: 20, left: 20, color: 'white', zIndex: 10 }}>
                <h1>🧬 Evolution Engine</h1>
                <p>Status: Evolving</p>
            </div>

            <Canvas camera={{ position: [0, 0, 10] }}>
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} />

                {/* Layer 1: Product (Blue) */}
                <ExperimentNode position={[-2, 2, 0]} color="#0088ff" label="Landing Page A/B" />
                <ExperimentNode position={[-3, 1, -2]} color="#0088ff" label="Pricing Model" />

                {/* Layer 2: AI (Purple) */}
                <ExperimentNode position={[0, 0, 0]} color="#aa00ff" label="EMM RL Agent" />
                <ExperimentNode position={[1, -1, 1]} color="#aa00ff" label="Drift Detection" />

                {/* Layer 3: Thermo (Orange) */}
                <ExperimentNode position={[2, 2, -1]} color="#ff8800" label="Model Compression" />
                <ExperimentNode position={[3, 1, 0]} color="#ff8800" label="Hydration Strategy" />

                {/* Layer 4: Narrative (Green) */}
                <ExperimentNode position={[0, -3, 2]} color="#00ff88" label="Narrative: Physics AGI" />

                <OrbitControls />
                <gridHelper args={[20, 20, 0x222222, 0x111111]} rotation={[Math.PI / 2, 0, 0]} />
            </Canvas>
        </div>
    );
}
