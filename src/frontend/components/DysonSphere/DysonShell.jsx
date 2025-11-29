import React, { useState, useEffect } from 'react';
import '../styles/dyson_sphere.css';
import IntentionStar from './IntentionStar';
import CapsulePortal from './CapsulePortal';

const DysonShell = () => {
    const [intent, setIntent] = useState("System Idle");

    // Mock Capsules for Demo
    const capsules = [
        { id: "TGE", name: "Thermo Gen", orbit: "inner", angle: 0, status: "active" },
        { id: "PSSM", name: "Skill Sov", orbit: "inner", angle: 90, status: "optimizing" },
        { id: "ZKMM", name: "Zero Know", orbit: "inner", angle: 180, status: "secure" },
        { id: "PEM", name: "Entropy", orbit: "inner", angle: 270, status: "predicting" },

        { id: "EAPM", name: "Ego Action", orbit: "middle", angle: 45, status: "active" },
        { id: "DCE", name: "Cap Econ", orbit: "middle", angle: 135, status: "bidding" },
        { id: "MFEM", name: "Fusion", orbit: "middle", angle: 225, status: "fusing" },
        { id: "HRAE", name: "Autopilot", orbit: "middle", angle: 315, status: "executing" },

        { id: "POP", name: "Phys Overlay", orbit: "outer", angle: 60, status: "scanning" },
    ];

    return (
        <div className="dyson-shell">
            <div className="star-field"></div>

            {/* Orbits */}
            <div className="orbit-ring orbit-inner"></div>
            <div className="orbit-ring orbit-middle"></div>
            <div className="orbit-ring orbit-outer"></div>

            {/* The Core */}
            <IntentionStar intent={intent} />

            {/* Capsules */}
            {capsules.map((cap) => (
                <CapsulePortal key={cap.id} data={cap} />
            ))}

            {/* HUD Overlay (Bottom Left) */}
            <div style={{ position: 'absolute', bottom: 20, left: 20, fontFamily: 'monospace', fontSize: 12, opacity: 0.7 }}>
                <div>DYSON SPHERE OS v1.0</div>
                <div>ENTROPY: 0.42 J/K</div>
                <div>STATUS: NOMINAL</div>
            </div>
        </div>
    );
};

export default DysonShell;
