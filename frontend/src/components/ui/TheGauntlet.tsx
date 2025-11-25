import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { Fingerprint, Zap, Activity } from "lucide-react";

interface WalletState {
    utid: string;
    credits: number; // Energy Credits
    reputation: number; // 0-100
    trust_level: 'gold' | 'silver' | 'bronze';
}

export function TheGauntlet() {
    const [wallet, setWallet] = useState<WalletState>({
        utid: "LOADING...",
        credits: 0,
        reputation: 0,
        trust_level: 'bronze'
    });

    useEffect(() => {
        const fetchWallet = async () => {
            try {
                // In a real app, we'd get the user's UTID from auth context.
                // For this demo, we'll use a hardcoded "current user" UTID or fetch one.
                const demoUtid = "UTID:USER:DEMO_001";
                const res = await fetch(`/v1/utid/wallet/${demoUtid}`);
                if (res.ok) {
                    const data = await res.json();
                    setWallet({
                        utid: data.utid,
                        credits: data.credits,
                        reputation: data.reputation,
                        trust_level: data.trust_level as any
                    });
                }
            } catch (e) {
                console.error("Failed to fetch wallet", e);
            }
        };
        fetchWallet();
        // Poll for updates
        const interval = setInterval(fetchWallet, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="relative group select-none">
            {/* Glass Container */}
            <div className="absolute inset-0 bg-dyson-void/80 backdrop-blur-md border border-dyson-amber/30 rounded-lg skew-x-[-10deg] shadow-[0_0_15px_rgba(255,179,0,0.1)] group-hover:shadow-[0_0_25px_rgba(255,179,0,0.3)] transition-all duration-500"></div>

            <div className="relative p-4 flex items-center gap-6 skew-x-[-10deg]">
                {/* Identity Totem */}
                <div className="flex flex-col items-center skew-x-[10deg]">
                    <div className={cn(
                        "w-10 h-10 rounded-full border-2 flex items-center justify-center relative",
                        wallet.trust_level === 'gold' ? "border-dyson-gold shadow-[0_0_10px_var(--dyson-gold)]" : "border-white/20"
                    )}>
                        <Fingerprint className={cn("w-6 h-6", wallet.trust_level === 'gold' ? "text-dyson-gold" : "text-white/50")} />
                        {/* Pulse Ring */}
                        <div className="absolute inset-0 rounded-full border border-dyson-gold/50 animate-ping opacity-20"></div>
                    </div>
                    <span className="text-[9px] font-mono text-muted-foreground mt-1 tracking-widest">IDENTITY</span>
                </div>

                {/* Energy Credits */}
                <div className="flex flex-col skew-x-[10deg]">
                    <div className="flex items-baseline gap-1">
                        <span className="text-2xl font-bold font-mono text-white tracking-tight">{wallet.credits.toLocaleString()}</span>
                        <span className="text-[10px] text-dyson-plasma font-bold">JOULES</span>
                    </div>
                    <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden mt-1">
                        <div className="h-full bg-gradient-to-r from-dyson-plasma to-dyson-amber w-[75%] animate-pulse"></div>
                    </div>
                    <span className="text-[9px] font-mono text-muted-foreground mt-1 tracking-widest flex items-center gap-1">
                        <Zap className="w-3 h-3 text-dyson-plasma" /> FUEL RESERVES
                    </span>
                </div>

                {/* Reputation Waveform */}
                <div className="flex flex-col items-end skew-x-[10deg] min-w-[80px]">
                    <div className="flex items-center gap-2 text-dyson-teal font-mono font-bold text-lg">
                        {wallet.reputation}%
                        <Activity className="w-4 h-4 animate-pulse" />
                    </div>
                    <div className="flex gap-0.5 items-end h-4 mt-1">
                        {[...Array(10)].map((_, i) => (
                            <div key={i}
                                className="w-1 bg-dyson-teal/50 rounded-sm transition-all duration-300"
                                style={{
                                    height: `${Math.random() * 100}%`,
                                    opacity: i < (wallet.reputation / 10) ? 1 : 0.2
                                }}
                            />
                        ))}
                    </div>
                    <span className="text-[9px] font-mono text-muted-foreground mt-1 tracking-widest">RESONANCE</span>
                </div>
            </div>

            {/* Decorative Corner Accents */}
            <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-dyson-amber opacity-50"></div>
            <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-dyson-amber opacity-50"></div>
        </div>
    );
}
