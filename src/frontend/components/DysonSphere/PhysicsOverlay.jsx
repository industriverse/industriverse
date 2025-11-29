import React, { useEffect, useRef } from 'react';

const PhysicsOverlay = ({ type, data }) => {
    const canvasRef = useRef(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw Overlay based on type
        if (type === 'vector_field') {
            drawVectorField(ctx, data);
        } else if (type === 'thermal') {
            drawThermalGradient(ctx);
        } else {
            drawGenericHUD(ctx);
        }

    }, [type, data]);

    const drawVectorField = (ctx, vectors) => {
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
        ctx.lineWidth = 1;

        // Mock Grid
        for (let i = 0; i < 10; i++) {
            for (let j = 0; j < 10; j++) {
                const x = i * 20 + 10;
                const y = j * 20 + 10;

                // Draw Arrow
                ctx.beginPath();
                ctx.moveTo(x, y);
                ctx.lineTo(x + 10, y - 5);
                ctx.stroke();
            }
        }
    };

    const drawThermalGradient = (ctx) => {
        const gradient = ctx.createLinearGradient(0, 0, 200, 200);
        gradient.addColorStop(0, 'rgba(255, 0, 0, 0.2)');
        gradient.addColorStop(1, 'rgba(0, 0, 255, 0.2)');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, 200, 200);
    };

    const drawGenericHUD = (ctx) => {
        ctx.strokeStyle = '#F7E399'; // Stellar Gold
        ctx.lineWidth = 1;
        ctx.strokeRect(10, 10, 180, 180);

        ctx.font = '10px monospace';
        ctx.fillStyle = '#F7E399';
        ctx.fillText("PHYSICS_ENGINE: ACTIVE", 20, 30);
        ctx.fillText("ENTROPY_FLUX: -0.04", 20, 45);
    };

    return (
        <canvas
            ref={canvasRef}
            width={200}
            height={200}
            style={{
                position: 'absolute',
                top: 0,
                left: 0,
                pointerEvents: 'none',
                opacity: 0.8
            }}
        />
    );
};

export default PhysicsOverlay;
