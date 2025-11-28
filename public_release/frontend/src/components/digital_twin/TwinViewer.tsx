import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { Play, Pause, FastForward, Activity, AlertTriangle } from 'lucide-react';

interface TwinState {
    timestamp: string;
    metrics: Record<string, number>;
    status: 'NOMINAL' | 'WARNING' | 'CRITICAL';
}

interface TwinViewerProps {
    twinId: string;
    twinType: string;
}

export const TwinViewer: React.FC<TwinViewerProps> = ({ twinId, twinType }) => {
    const [isPlaying, setIsPlaying] = useState(false);
    const [timeIndex, setTimeIndex] = useState(0);
    const [projections, setProjections] = useState<TwinState[]>([]);

    // Mock data loading
    useEffect(() => {
        // In a real app, fetch from API
        const mockProjections: TwinState[] = Array.from({ length: 61 }, (_, i) => ({
            timestamp: new Date(Date.now() + i * 60000).toISOString(),
            metrics: {
                stability: Math.max(0, 1.0 - (i * 0.01)),
                temp: 150 + (i * 2),
            },
            status: i > 40 ? 'CRITICAL' : (i > 20 ? 'WARNING' : 'NOMINAL')
        }));
        setProjections(mockProjections);
    }, [twinId]);

    useEffect(() => {
        let interval: NodeJS.Timeout;
        if (isPlaying && timeIndex < projections.length - 1) {
            interval = setInterval(() => {
                setTimeIndex(prev => prev + 1);
            }, 100); // Fast playback
        } else if (timeIndex >= projections.length - 1) {
            setIsPlaying(false);
        }
        return () => clearInterval(interval);
    }, [isPlaying, timeIndex, projections.length]);

    const currentState = projections[timeIndex];

    if (!currentState) return <div>Loading Twin Data...</div>;

    return (
        <Card className="w-full max-w-4xl bg-black/90 border-cyan-500/30 text-cyan-50">
            <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-xl font-mono flex items-center gap-2">
                    <Activity className="w-5 h-5 text-cyan-400" />
                    DIGITAL TWIN: {twinType.toUpperCase()}
                </CardTitle>
                <Badge variant={currentState.status === 'NOMINAL' ? 'default' : 'destructive'}
                    className="font-mono text-lg">
                    {currentState.status}
                </Badge>
            </CardHeader>

            <CardContent className="space-y-6">
                {/* 3D Viewport Placeholder */}
                <div className="relative w-full h-64 bg-slate-900 rounded-lg border border-cyan-900/50 overflow-hidden flex items-center justify-center">
                    <div className="absolute inset-0 bg-[url('/grid.png')] opacity-20"></div>

                    {/* Mock 3D Object */}
                    <div className={`w-32 h-32 rounded-full blur-xl transition-all duration-300
            ${currentState.status === 'CRITICAL' ? 'bg-red-500' : 'bg-cyan-500'}
            animate-pulse`}
                    ></div>
                    <div className="z-10 text-center">
                        <h3 className="text-2xl font-bold">{twinId}</h3>
                        <p className="text-sm text-cyan-300/70">Gaussian Splat Visualization</p>
                    </div>

                    {/* Ghost Overlay */}
                    {timeIndex > 0 && (
                        <div className="absolute top-4 right-4 text-right">
                            <p className="text-xs text-cyan-400">SHADOW PROJECTION</p>
                            <p className="text-xl font-mono">T+{timeIndex}m</p>
                        </div>
                    )}
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-2 gap-4">
                    {Object.entries(currentState.metrics).map(([key, value]) => (
                        <div key={key} className="bg-cyan-950/30 p-3 rounded border border-cyan-900/50">
                            <p className="text-xs text-cyan-400 uppercase">{key}</p>
                            <p className="text-2xl font-mono">{value.toFixed(2)}</p>
                        </div>
                    ))}
                </div>

                {/* Timeline Control */}
                <div className="space-y-2">
                    <div className="flex justify-between text-xs text-cyan-500 font-mono">
                        <span>NOW</span>
                        <span>+30m</span>
                        <span>+60m</span>
                    </div>
                    <Slider
                        value={[timeIndex]}
                        max={60}
                        step={1}
                        onValueChange={(val) => setTimeIndex(val[0])}
                        className="cursor-pointer"
                    />
                </div>

                {/* Playback Controls */}
                <div className="flex justify-center gap-4">
                    <button
                        onClick={() => setIsPlaying(!isPlaying)}
                        className="p-2 rounded-full bg-cyan-500/20 hover:bg-cyan-500/40 transition-colors"
                    >
                        {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
                    </button>
                    <button
                        onClick={() => setTimeIndex(0)}
                        className="p-2 rounded-full bg-cyan-500/20 hover:bg-cyan-500/40 transition-colors"
                    >
                        <FastForward className="w-6 h-6 rotate-180" />
                    </button>
                </div>
            </CardContent>
        </Card>
    );
};
