// @ts-nocheck
import { useSystemPulse } from "@/hooks/useSystemPulse";
import { cn } from "@/lib/utils";
import { AlertTriangle } from "lucide-react";

export function ReactorGauge() {
    const { metrics, isConnected } = useSystemPulse();

    // Map system_entropy (0.0-1.0) to percentage (0-100)
    // Default to 45 if not connected
    const entropy = isConnected ? Math.min(100, metrics.system_entropy * 100) : 45;
    const isOverheating = entropy > 80;
    const stability = entropy < 60 ? "STABLE" : (entropy < 85 ? "UNSTABLE" : "CRITICAL");

    const state = {
        entropy,
        stability,
        threat_level: isOverheating ? 4 : 1,
        is_overheating: isOverheating
    };

    return (
        <div className="relative w-32 h-32 flex items-center justify-center group">
            {/* Outer Ring */}
            <div className="absolute inset-0 rounded-full border-4 border-white/5 border-t-dyson-plasma/20 rotate-45"></div>

            {/* Gauge Track */}
            <svg className="absolute inset-0 w-full h-full -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="6" strokeDasharray="251.2" strokeDashoffset="62.8" strokeLinecap="round" />
                <circle
                    cx="50" cy="50" r="40"
                    fill="none"
                    stroke={state.is_overheating ? "var(--dyson-plasma)" : "var(--dyson-teal)"}
                    strokeWidth="6"
                    strokeDasharray="251.2"
                    strokeDashoffset={251.2 - (251.2 * 0.75 * (state.entropy / 100))}
                    strokeLinecap="round"
                    className="transition-all duration-1000 ease-out"
                />
            </svg>

            {/* Center Display */}
            <div className="relative z-10 flex flex-col items-center text-center">
                <div className={cn(
                    "text-2xl font-bold font-mono tracking-tighter transition-colors",
                    state.is_overheating ? "text-dyson-plasma animate-pulse" : "text-white"
                )}>
                    {state.entropy.toFixed(0)}°
                </div>
                <div className="text-[8px] text-muted-foreground font-mono tracking-widest uppercase mt-1">
                    {state.stability}
                </div>
            </div>

            {/* Warning Indicator */}
            {state.is_overheating && (
                <div className="absolute -top-2 animate-bounce">
                    <AlertTriangle className="w-4 h-4 text-dyson-plasma" />
                </div>
            )}

            {/* Decorative Ticks */}
            <div className="absolute inset-0 w-full h-full">
                {[0, 45, 90, 135, 180, 225, 270].map((deg) => (
                    <div key={deg}
                        className="absolute top-0 left-1/2 w-0.5 h-2 bg-white/20 origin-bottom"
                        style={{ transform: `rotate(${deg - 135}deg) translateY(4px) translateX(-50%)`, transformOrigin: '50% 64px' }}
                    />
                ))}
            </div>
        </div>
    );
}
