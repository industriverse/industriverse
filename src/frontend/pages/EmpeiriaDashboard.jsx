import React, { useState, useEffect } from 'react';
import '../styles/dyson_sphere.css'; // Reuse cosmic styles

const EmpeiriaDashboard = () => {
    const [snapshots, setSnapshots] = useState([]);
    const [stats, setStats] = useState({ entropy_events: 0, anomalies: 0 });

    // Mock Data Loader (In real app, this would fetch from an API serving data/research/raw)
    useEffect(() => {
        const interval = setInterval(() => {
            // Simulate fetching new snapshots
            const newSnapshot = generateMockSnapshot();
            setSnapshots(prev => [newSnapshot, ...prev].slice(0, 20)); // Keep last 20

            setStats(prev => ({
                entropy_events: prev.entropy_events + (newSnapshot.event_type === "ENTROPY_MINIMIZATION" ? 1 : 0),
                anomalies: prev.anomalies + (newSnapshot.event_type === "ANOMALY_DETECTED" ? 1 : 0)
            }));
        }, 2000);
        return () => clearInterval(interval);
    }, []);

    const generateMockSnapshot = () => {
        const types = ["ENTROPY_MINIMIZATION", "ANOMALY_DETECTED"];
        const type = types[Math.floor(Math.random() * types.length)];
        return {
            id: `res-${Date.now()}`,
            timestamp: new Date().toLocaleTimeString(),
            event_type: type,
            hypothesis: type === "ENTROPY_MINIMIZATION"
                ? "Thermal drift correlates with efficiency gain."
                : "Safety degradation detected in robotic arm.",
            metrics: {
                entropy: Math.random().toFixed(4),
                safety: Math.random().toFixed(4)
            }
        };
    };

    return (
        <div className="dyson-shell" style={{ flexDirection: 'column', justifyContent: 'flex-start', padding: '40px' }}>
            <div className="star-field"></div>

            {/* Header */}
            <div style={{ zIndex: 10, textAlign: 'center', marginBottom: '40px' }}>
                <h1 style={{ color: 'var(--stellar-gold)', letterSpacing: '4px', textTransform: 'uppercase' }}>
                    Empeiria Haus Observatory
                </h1>
                <div style={{ color: 'var(--quantum-white)', fontSize: '14px', opacity: 0.7 }}>
                    AUTONOMOUS RESEARCH ENGINE // LIVE FEED
                </div>
            </div>

            {/* Stats Row */}
            <div style={{ display: 'flex', gap: '40px', zIndex: 10, marginBottom: '40px' }}>
                <StatBox label="ENTROPY DISCOVERIES" value={stats.entropy_events} color="var(--stellar-gold)" />
                <StatBox label="ANOMALIES DETECTED" value={stats.anomalies} color="var(--infrared-red)" />
                <StatBox label="PAPERS GENERATED" value={Math.floor((stats.entropy_events + stats.anomalies) / 5)} color="var(--cosmic-blue)" />
            </div>

            {/* Discovery Feed */}
            <div style={{
                zIndex: 10,
                width: '80%',
                maxWidth: '1000px',
                background: 'rgba(10, 10, 20, 0.8)',
                border: '1px solid var(--cosmic-blue)',
                borderRadius: '8px',
                padding: '20px',
                maxHeight: '500px',
                overflowY: 'auto',
                backdropFilter: 'blur(10px)'
            }}>
                {snapshots.map(snap => (
                    <div key={snap.id} style={{
                        borderBottom: '1px solid rgba(255,255,255,0.1)',
                        padding: '15px 0',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                    }}>
                        <div>
                            <div style={{
                                color: snap.event_type === "ENTROPY_MINIMIZATION" ? 'var(--stellar-gold)' : 'var(--infrared-red)',
                                fontSize: '12px',
                                fontWeight: 'bold',
                                marginBottom: '5px'
                            }}>
                                {snap.event_type}
                            </div>
                            <div style={{ color: 'var(--quantum-white)', fontSize: '16px' }}>
                                {snap.hypothesis}
                            </div>
                        </div>
                        <div style={{ textAlign: 'right', fontSize: '12px', opacity: 0.6 }}>
                            <div>{snap.timestamp}</div>
                            <div>E: {snap.metrics.entropy} | S: {snap.metrics.safety}</div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

const StatBox = ({ label, value, color }) => (
    <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: '32px', fontWeight: 'bold', color: color }}>{value}</div>
        <div style={{ fontSize: '10px', letterSpacing: '1px', opacity: 0.7 }}>{label}</div>
    </div>
);

export default EmpeiriaDashboard;
