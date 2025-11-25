import { Link } from 'wouter';
import EnergyField from '@/components/3d/EnergyField';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { ArrowRight, Activity, Globe, Database, Shield } from 'lucide-react';
import { useState } from 'react';
import { useEnergyMap } from "@/hooks/useEnergyMap";
import { TruthSigil } from "@/components/ui/TruthSigil";
import { TheGauntlet } from "@/components/ui/TheGauntlet";
import { ReactorGauge } from "@/components/ui/ReactorGauge";
import { DysonLayout } from "@/layouts/DysonLayout";
import { TheConstellation } from "@/components/3d/TheConstellation";

export default function Portal() {
    const { data: energyMap } = useEnergyMap();
    const [selectedDataset, setSelectedDataset] = useState<string | null>(null);
    const datasets = ["turbulent_radiative_layer_2D", "active_matter", "supernova_explosion"];

    const handleDatasetChange = async (dataset: string) => {
        setSelectedDataset(dataset);
        // Trigger backend to use this dataset (mock call for now, or real if endpoint exists)
        try {
            await fetch("/api/v1/thermodynamic/thermal/sample", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    problem_type: "sampling",
                    dataset_id: dataset,
                    variables: { "x": [0, 1], "y": [0, 1] },
                    num_samples: 100
                })
            });
        } catch (e) {
            console.error("Failed to trigger sampling", e);
        }
    };
    const nodeCount = energyMap?.node_count || 0;
    return (
        <DysonLayout>
            <div className="relative z-10 flex flex-col items-center justify-center min-h-screen text-center px-4 pointer-events-none">
                <div className="pointer-events-auto">
                    <EnergyField />
                </div>

                <h1 className="text-6xl md:text-8xl font-bold tracking-tighter mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white to-white/50 pointer-events-auto select-none">
                    INDUSTRI<span className="text-dyson-plasma">VERSE</span>
                </h1>

                <p className="text-xl md:text-2xl text-dyson-glass max-w-2xl mb-12 pointer-events-auto font-light tracking-wide">
                    Thermodynamic Intelligence Engine
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 max-w-6xl w-full pointer-events-auto">
                    <Link href="/proofs">
                        <GlassPanel className="h-48 flex flex-col items-center justify-center gap-4 hover:border-dyson-plasma/50 transition-colors group cursor-pointer">
                            <Activity className="w-8 h-8 text-dyson-plasma group-hover:scale-110 transition-transform" />
                            <span className="font-mono text-sm tracking-widest uppercase">Proof DAG</span>
                        </GlassPanel>
                    </Link>

                    <Link href="/network">
                        <GlassPanel className="h-48 flex flex-col items-center justify-center gap-4 hover:border-dyson-gold/50 transition-colors group cursor-pointer">
                            <Globe className="w-8 h-8 text-dyson-gold group-hover:scale-110 transition-transform" />
                            <span className="font-mono text-sm tracking-widest uppercase">Network</span>
                        </GlassPanel>
                    </Link>

                    <Link href="/storage">
                        <GlassPanel className="h-48 flex flex-col items-center justify-center gap-4 hover:border-dyson-teal/50 transition-colors group cursor-pointer">
                            <Database className="w-8 h-8 text-dyson-teal group-hover:scale-110 transition-transform" />
                            <span className="font-mono text-sm tracking-widest uppercase">Storage</span>
                        </GlassPanel>
                    </Link>

                    <Link href="/shield">
                        <GlassPanel className="h-48 flex flex-col items-center justify-center gap-4 hover:border-red-500/50 transition-colors group cursor-pointer">
                            <Shield className="w-8 h-8 text-red-500 group-hover:scale-110 transition-transform" />
                            <span className="font-mono text-sm tracking-widest uppercase">AI Shield</span>
                        </GlassPanel>
                    </Link>
                </div>

                <div className="mt-12 pointer-events-auto">
                    <Link href="/console">
                        <button className="group relative px-8 py-4 bg-dyson-plasma/10 hover:bg-dyson-plasma/20 border border-dyson-plasma/50 rounded-full transition-all duration-300">
                            <span className="flex items-center gap-2 font-mono text-sm tracking-widest uppercase text-dyson-plasma">
                                Enter System <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                            </span>
                            <div className="absolute inset-0 rounded-full ring-1 ring-white/20 group-hover:ring-white/40 animate-pulse" />
                        </button>
                    </Link>
                </div>
            </div>
            {/* Right Sidebar - HUD & Tools */}
            <div className="fixed right-8 top-24 bottom-8 w-80 flex flex-col gap-6 z-20 pointer-events-none">
                <div className="pointer-events-auto space-y-6">
                    <TheGauntlet />
                    <ReactorGauge />

                    {/* Dataset Selector */}
                    <div className="bg-dyson-void/80 backdrop-blur-md border border-dyson-glass/30 p-4 rounded-lg pointer-events-auto">
                        <h3 className="text-dyson-gold text-sm font-mono mb-2 uppercase tracking-wider">Physics Prior</h3>
                        <div className="space-y-2">
                            {datasets.map(ds => (
                                <button
                                    key={ds}
                                    onClick={() => handleDatasetChange(ds)}
                                    className={`w-full text-left text-xs px-3 py-2 rounded border transition-all ${selectedDataset === ds
                                            ? "border-dyson-plasma text-dyson-plasma bg-dyson-plasma/10"
                                            : "border-dyson-glass/20 text-dyson-glass hover:border-dyson-gold/50 hover:text-dyson-gold"
                                        }`}
                                >
                                    {ds.replace(/_/g, " ")}
                                </button>
                            ))}
                        </div>
                    </div>

                    <TruthSigil />
                </div>

                <div className="pointer-events-auto h-48 w-64 opacity-80 hover:opacity-100 transition-opacity border border-dyson-teal/20 rounded-lg overflow-hidden bg-black/20 backdrop-blur-sm">
                    {/* ProofDAG Visualization */}
                    <div className="w-full h-full">
                        <TheConstellation />
                    </div>
                </div>
            </div>

            {/* Footer Status */}
            <div className="fixed bottom-0 left-0 right-0 h-8 bg-black/80 backdrop-blur border-t border-white/10 flex items-center justify-between px-4 text-[10px] font-mono text-dyson-glass z-20">
                <div className="flex gap-4">
                    <span className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-dyson-teal animate-pulse" />
                        SYSTEM ONLINE
                    </span>
                    <span>NODES: {nodeCount}</span>
                </div>
                <div className="flex gap-4">
                    <span>LATENCY: 12ms</span>
                    <span>VERSION: v2.0.4-DYSON</span>
                </div>
            </div>
        </DysonLayout>
    );
}
