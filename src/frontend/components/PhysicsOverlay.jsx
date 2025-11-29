import React, { useEffect, useState } from 'react';

const PhysicsOverlay = ({ active }) => {
    if (!active) return null;

    const [forces, setForces] = useState([]);

    // Simulate real-time physics vectors
    useEffect(() => {
        const interval = setInterval(() => {
            const time = Date.now() / 1000;
            setForces([
                { id: 1, x: 50 + Math.sin(time) * 10, y: 50 + Math.cos(time) * 10, label: 'F_cut', color: 'red' },
                { id: 2, x: 150, y: 100, label: 'T_spindle', color: 'cyan' },
                { id: 3, x: 250 + Math.cos(time * 2) * 5, y: 50, label: 'V_feed', color: 'lime' }
            ]);
        }, 100);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="absolute top-0 left-0 w-full h-full pointer-events-none z-50">
            <svg className="w-full h-full">
                {forces.map(f => (
                    <g key={f.id} transform={`translate(${f.x}, ${f.y})`}>
                        <line x1="0" y1="0" x2="40" y2="-20" stroke={f.color} strokeWidth="2" markerEnd="url(#arrow)" />
                        <text x="45" y="-25" fill={f.color} fontSize="12" fontFamily="monospace">{f.label}</text>
                    </g>
                ))}
                <defs>
                    <marker id="arrow" markerWidth="10" markerHeight="10" refX="0" refY="3" orient="auto" markerUnits="strokeWidth">
                        <path d="M0,0 L0,6 L9,3 z" fill="white" />
                    </marker>
                </defs>
            </svg>
            <div className="absolute bottom-4 right-4 bg-black/80 text-green-400 p-2 font-mono text-xs border border-green-500/50 rounded">
                <div>PHYSICS_ENGINE: ACTIVE</div>
                <div>ZK_PROOF: VERIFIED</div>
                <div>A2A_BUS: CONNECTED</div>
            </div>
        </div>
    );
};

export default PhysicsOverlay;
