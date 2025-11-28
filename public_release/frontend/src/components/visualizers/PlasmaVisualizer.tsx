import React, { useEffect, useRef } from 'react';

interface PlasmaVisualizerProps {
    topology?: string;
    intensity?: number;
}

const PlasmaVisualizer: React.FC<PlasmaVisualizerProps> = ({ topology = 'toroidal', intensity = 1.0 }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let animationFrameId: number;
        let time = 0;

        const render = () => {
            time += 0.05 * intensity;
            ctx.fillStyle = '#000000';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;
            const radius = 80;

            // Draw "Plasma" (glowing particles/lines)
            ctx.globalCompositeOperation = 'screen';

            for (let i = 0; i < 360; i += 5) {
                const angle = (i * Math.PI) / 180 + time * 0.1;
                const x = centerX + Math.cos(angle) * radius;
                const y = centerY + Math.sin(angle) * (radius * 0.6); // Elliptical for torus perspective

                const gradient = ctx.createRadialGradient(x, y, 2, x, y, 20);
                gradient.addColorStop(0, `hsla(${280 + Math.sin(time) * 40}, 100%, 70%, 0.8)`);
                gradient.addColorStop(1, 'transparent');

                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(x, y, 20, 0, Math.PI * 2);
                ctx.fill();
            }

            // Core glow
            const coreGrad = ctx.createRadialGradient(centerX, centerY, 10, centerX, centerY, 100);
            coreGrad.addColorStop(0, 'rgba(100, 200, 255, 0.2)');
            coreGrad.addColorStop(1, 'transparent');
            ctx.fillStyle = coreGrad;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            animationFrameId = requestAnimationFrame(render);
        };

        render();

        return () => cancelAnimationFrame(animationFrameId);
    }, [intensity]);

    return (
        <div className="p-4 bg-gray-900 rounded-lg border border-purple-500/30">
            <h3 className="text-purple-400 text-sm mb-2 font-mono">PLASMA TOPOLOGY: {topology.toUpperCase()}</h3>
            <canvas ref={canvasRef} width={400} height={300} className="w-full h-48 rounded bg-black" />
        </div>
    );
};

export default PlasmaVisualizer;
