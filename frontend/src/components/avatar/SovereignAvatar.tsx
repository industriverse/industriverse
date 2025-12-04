import React, { useState, useEffect } from 'react';
import { Activity, Mic, X } from 'lucide-react';
import { GlassPanel } from '@/components/ui/GlassPanel';

interface SovereignAvatarProps {
    onClose?: () => void;
    script?: string;
}

export const SovereignAvatar: React.FC<SovereignAvatarProps> = ({ onClose, script = "System initialized. Waiting for query." }) => {
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [displayText, setDisplayText] = useState("");

    // Simulate typing effect / speech
    useEffect(() => {
        setIsSpeaking(true);
        let i = 0;
        const interval = setInterval(() => {
            setDisplayText(script.substring(0, i));
            i++;
            if (i > script.length) {
                clearInterval(interval);
                setIsSpeaking(false);
            }
        }, 30); // Typing speed

        return () => clearInterval(interval);
    }, [script]);

    return (
        <div className="fixed bottom-8 left-8 z-50 w-96 animate-in slide-in-from-bottom-10 fade-in duration-500">
            <GlassPanel className="relative overflow-hidden border-dyson-plasma/50 shadow-[0_0_30px_rgba(0,255,255,0.2)]">
                {/* Header */}
                <div className="flex justify-between items-center p-3 border-b border-white/10 bg-black/40">
                    <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${isSpeaking ? 'bg-dyson-plasma animate-pulse' : 'bg-dyson-teal'}`} />
                        <span className="text-xs font-mono tracking-widest text-dyson-plasma uppercase">Sovereign CSO</span>
                    </div>
                    <button onClick={onClose} className="text-white/50 hover:text-white transition-colors">
                        <X className="w-4 h-4" />
                    </button>
                </div>

                {/* Avatar Visual (Mock) */}
                <div className="relative h-64 bg-black/80 flex items-center justify-center overflow-hidden group">
                    {/* Placeholder for Video/WebGL Avatar */}
                    <div className="absolute inset-0 bg-gradient-to-t from-dyson-plasma/20 to-transparent opacity-50" />

                    {/* Audio Waveform Visualization Mock */}
                    <div className="flex gap-1 items-end h-12">
                        {[...Array(8)].map((_, i) => (
                            <div
                                key={i}
                                className={`w-2 bg-dyson-plasma/80 rounded-t-sm transition-all duration-100 ${isSpeaking ? 'animate-bounce' : 'h-2'}`}
                                style={{ height: isSpeaking ? `${Math.random() * 100}%` : '10%' }}
                            />
                        ))}
                    </div>

                    <div className="absolute bottom-2 right-2">
                        <Activity className="w-4 h-4 text-dyson-plasma opacity-50" />
                    </div>
                </div>

                {/* Subtitles / Script */}
                <div className="p-4 bg-black/60 min-h-[100px] border-t border-white/5">
                    <p className="font-mono text-sm text-dyson-glass leading-relaxed">
                        {displayText}
                        <span className="animate-pulse">_</span>
                    </p>
                </div>

                {/* Interaction Bar */}
                <div className="p-2 bg-black/80 border-t border-white/10 flex gap-2">
                    <button className="flex-1 bg-white/5 hover:bg-white/10 border border-white/10 rounded px-3 py-2 text-xs font-mono text-white/70 transition-colors text-left">
                        Explain "Negentropy"
                    </button>
                    <button className="p-2 bg-dyson-plasma/20 hover:bg-dyson-plasma/30 border border-dyson-plasma/50 rounded text-dyson-plasma">
                        <Mic className="w-4 h-4" />
                    </button>
                </div>
            </GlassPanel>
        </div>
    );
};
