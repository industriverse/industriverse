import React, { useEffect, useRef } from 'react';

interface NetworkGraphProps {
    nodes?: number;
    stability?: number;
}

const NetworkGraph: React.FC<NetworkGraphProps> = ({ nodes = 50, stability = 0.95 }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Generate random nodes
        const nodeList = Array.from({ length: 20 }).map(() => ({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 2,
            vy: (Math.random() - 0.5) * 2,
        }));

        let animationFrameId: number;

        const render = () => {
            ctx.fillStyle = '#050505';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Update and draw nodes
            ctx.strokeStyle = stability > 0.9 ? '#4ade80' : '#ef4444'; // Green if stable, red if not
            ctx.lineWidth = 1;

            nodeList.forEach((node, i) => {
                node.x += node.vx;
                node.y += node.vy;

                // Bounce
                if (node.x < 0 || node.x > canvas.width) node.vx *= -1;
                if (node.y < 0 || node.y > canvas.height) node.vy *= -1;

                // Draw connections
                nodeList.slice(i + 1).forEach((other) => {
                    const dx = node.x - other.x;
                    const dy = node.y - other.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < 100) {
                        ctx.globalAlpha = 1 - dist / 100;
                        ctx.beginPath();
                        ctx.moveTo(node.x, node.y);
                        ctx.lineTo(other.x, other.y);
                        ctx.stroke();
                    }
                });
                ctx.globalAlpha = 1;

                // Draw node
                ctx.fillStyle = '#fff';
                ctx.beginPath();
                ctx.arc(node.x, node.y, 3, 0, Math.PI * 2);
                ctx.fill();
            });

            animationFrameId = requestAnimationFrame(render);
        };

        render();

        return () => cancelAnimationFrame(animationFrameId);
    }, [stability]);

    return (
        <div className="p-4 bg-gray-900 rounded-lg border border-green-500/30">
            <h3 className="text-green-400 text-sm mb-2 font-mono">GRID NETWORK STATUS</h3>
            <canvas ref={canvasRef} width={400} height={300} className="w-full h-48 rounded bg-black" />
        </div>
    );
};

export default NetworkGraph;
