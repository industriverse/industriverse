import React, { useEffect, useRef } from 'react';

/**
 * Challenge #9: Ambient Intelligence for Factories.
 * The "Dyson Sphere" UI visualizes the factory as a living organism.
 * Note: In a real app, this would use Three.js / React-Three-Fiber.
 * Here we render a conceptual placeholder.
 */
const DysonSphere = ({ factoryState }) => {
    const canvasRef = useRef(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        let animationFrameId;

        const render = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Draw the "Core" (Factory Heart)
            ctx.beginPath();
            ctx.arc(canvas.width / 2, canvas.height / 2, 50, 0, 2 * Math.PI);
            ctx.fillStyle = factoryState.drift_status === 'nominal' ? '#00ffcc' : '#ff0000';
            ctx.fill();
            ctx.shadowBlur = 20;
            ctx.shadowColor = ctx.fillStyle;

            // Draw "Orbiting Capsules" (Tasks)
            const time = Date.now() * 0.001;
            for (let i = 0; i < 8; i++) {
                const angle = time + (i * Math.PI / 4);
                const radius = 120 + Math.sin(time * 2 + i) * 10;
                const x = canvas.width / 2 + Math.cos(angle) * radius;
                const y = canvas.height / 2 + Math.sin(angle) * radius;

                ctx.beginPath();
                ctx.arc(x, y, 10, 0, 2 * Math.PI);
                ctx.fillStyle = '#ffffff';
                ctx.fill();

                // Connection Line (Energy Flow)
                ctx.beginPath();
                ctx.moveTo(canvas.width / 2, canvas.height / 2);
                ctx.lineTo(x, y);
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
                ctx.stroke();
            }

            animationFrameId = requestAnimationFrame(render);
        };

        render();

        return () => cancelAnimationFrame(animationFrameId);
    }, [factoryState]);

    return (
        <div className="dyson-sphere-container" style={{ width: '100%', height: '400px', background: '#0a0a0a' }}>
            <h3 style={{ color: '#fff', textAlign: 'center', paddingTop: '10px' }}>
                🔮 Dyson Sphere: Ambient Intelligence
            </h3>
            <div style={{ color: '#aaa', textAlign: 'center', fontSize: '12px' }}>
                Thermodynamic Field Visualization
            </div>
            <canvas
                ref={canvasRef}
                width={600}
                height={350}
                style={{ display: 'block', margin: '0 auto' }}
            />
            <div style={{ padding: '20px', color: '#00ffcc', fontFamily: 'monospace' }}>
                <div>State: {JSON.stringify(factoryState)}</div>
            </div>
        </div>
    );
};

export default DysonSphere;
