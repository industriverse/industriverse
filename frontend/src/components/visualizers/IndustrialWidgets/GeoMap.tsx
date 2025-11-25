import React from 'react';

interface GeoPoint {
    lat: number;
    lng: number;
    label: string;
    status: 'active' | 'warning' | 'error';
}

interface GeoMapProps {
    points: GeoPoint[];
    width?: number;
    height?: number;
}

export const GeoMap: React.FC<GeoMapProps> = ({ points, width = 400, height = 300 }) => {
    // Simple Equirectangular projection for demo
    const project = (lat: number, lng: number) => {
        const x = (lng + 180) * (width / 360);
        const y = (height / 2) - (lat * (height / 180));
        return { x, y };
    };

    return (
        <div className="relative bg-slate-900 rounded-lg border border-slate-700 overflow-hidden" style={{ width, height }}>
            <svg width={width} height={height} className="absolute top-0 left-0">
                {/* Abstract World Map Background (Simplified Grid) */}
                <defs>
                    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                        <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
                    </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#grid)" />

                {/* World Outline (Simplified) - In a real app, use GeoJSON path */}
                <path d={`M${width * 0.1},${height * 0.2} Q${width * 0.5},${height * 0.1} ${width * 0.9},${height * 0.2} T${width * 0.9},${height * 0.8} T${width * 0.1},${height * 0.8} Z`}
                    fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="2" strokeDasharray="5,5" />

                {/* Points */}
                {points.map((point, i) => {
                    const { x, y } = project(point.lat, point.lng);
                    const color = point.status === 'active' ? '#10b981' : point.status === 'warning' ? '#f59e0b' : '#ef4444';

                    return (
                        <g key={i}>
                            <circle cx={x} cy={y} r="4" fill={color} className="animate-pulse" />
                            <circle cx={x} cy={y} r="8" fill="none" stroke={color} strokeOpacity="0.5" />
                            <text x={x + 10} y={y + 4} fill="white" fontSize="10" className="font-mono">{point.label}</text>
                        </g>
                    );
                })}
            </svg>
            <div className="absolute bottom-2 right-2 text-xs text-slate-500 font-mono">
                Global Asset Tracking
            </div>
        </div>
    );
};
