// @ts-nocheck
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { useSystemPulse } from "@/hooks/useSystemPulse";

type Proof = {
    proof_id: string;
    utid: string;
    domain: string;
    metadata: Record<string, any>;
    anchors?: { chain?: string; tx?: string }[];
};

const fallbackProofs: Proof[] = [
    { proof_id: "proof-mock-1", utid: "UTID:REAL:mock", domain: "general", metadata: { energy_joules: 12.3, status: "verified", proof_score: 0.95 } },
    { proof_id: "proof-mock-2", utid: "UTID:REAL:mock2", domain: "general", metadata: { energy_joules: 5.1, status: "pending", proof_score: 0.4 } },
];

export function TruthSigil() {
    const [proofs, setProofs] = useState<Proof[]>(fallbackProofs);
    const [loading, setLoading] = useState(true);
    const { lastEvent } = useSystemPulse();

    useEffect(() => {
        if (lastEvent && lastEvent.type === 'proof_generated' && lastEvent.proof) {
            setProofs(prev => [lastEvent.proof, ...prev].slice(0, 50)); // Keep last 50
        }
    }, [lastEvent]);

    useEffect(() => {
        const fetchProofs = async () => {
            try {
                const resp = await fetch("/v1/proofs?limit=5");
                if (resp.ok) {
                    const data = await resp.json();
                    setProofs(data);
                }
            } catch (e) {
                console.warn("Using fallback proofs");
            } finally {
                setLoading(false);
            }
        };
        fetchProofs();
    }, []);

    return (
        <div className="relative group">
            {/* The Sigil Container */}
            <div className="absolute -inset-0.5 bg-gradient-to-r from-dyson-plasma to-dyson-amber rounded-lg blur opacity-30 group-hover:opacity-75 transition duration-1000 group-hover:duration-200 animate-tilt"></div>
            <div className="relative bg-black border border-border rounded-lg p-4 shadow-2xl backdrop-blur-xl">

                {/* Header: The Rune */}
                <div className="flex items-center justify-between mb-4 border-b border-border/50 pb-2">
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-dyson-plasma animate-pulse" />
                        <h3 className="text-sm font-mono tracking-widest text-dyson-gold uppercase">Truth Stream</h3>
                    </div>
                    <span className="text-xs text-muted-foreground font-mono">LIVE</span>
                </div>

                {/* The Stream */}
                <div className="space-y-3 max-h-[300px] overflow-y-auto scrollbar-thin scrollbar-thumb-dyson-plasma/20">
                    {proofs.map((p) => (
                        <div key={p.proof_id} className="relative p-3 rounded bg-white/5 hover:bg-white/10 transition-colors border-l-2 border-transparent hover:border-dyson-plasma group/item">

                            {/* Proof ID & Score */}
                            <div className="flex justify-between items-start mb-1">
                                <span className="font-mono text-[10px] text-muted-foreground truncate max-w-[120px] group-hover/item:text-dyson-plasma transition-colors">
                                    {p.proof_id}
                                </span>
                                <div className="flex items-center gap-1">
                                    {p.metadata?.proof_score && (
                                        <span className={cn(
                                            "text-[10px] font-bold px-1.5 py-0.5 rounded",
                                            p.metadata.proof_score > 0.8 ? "bg-dyson-teal/20 text-dyson-teal" : "bg-dyson-amber/20 text-dyson-amber"
                                        )}>
                                            {(p.metadata.proof_score * 100).toFixed(0)}%
                                        </span>
                                    )}
                                </div>
                            </div>

                            {/* Metadata Grid */}
                            <div className="grid grid-cols-2 gap-2 text-[10px] text-muted-foreground mt-2">
                                <div className="flex flex-col">
                                    <span className="uppercase tracking-wider opacity-50">Energy</span>
                                    <span className="text-white font-mono">{p.metadata?.energy_joules || 0} J</span>
                                </div>
                                <div className="flex flex-col">
                                    <span className="uppercase tracking-wider opacity-50">Status</span>
                                    <span className={cn(
                                        "uppercase font-bold",
                                        p.metadata?.status === 'verified' ? "text-dyson-teal" : "text-dyson-amber"
                                    )}>{p.metadata?.status || 'Unknown'}</span>
                                </div>
                            </div>

                            {/* Anchors (if any) */}
                            {p.metadata?.anchors && p.metadata.anchors.length > 0 && (
                                <div className="mt-2 pt-2 border-t border-white/5">
                                    <div className="text-[9px] uppercase tracking-widest text-muted-foreground mb-1">Anchors</div>
                                    {p.metadata.anchors.map((a: any, idx: number) => (
                                        <div key={idx} className="font-mono text-[9px] text-dyson-gold truncate">
                                            {a.chain}::{a.tx}
                                        </div>
                                    ))}
                                </div>
                            )}

                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
