import { Link } from 'wouter';
import EnergyField from '@/components/3d/EnergyField';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { Button } from '@/components/ui/button';
import { ArrowRight, Activity, Globe, Database, Shield } from 'lucide-react';
import { useEnergyMap } from "@/api/thermodynamic";
import { TruthSigil } from "@/components/ui/TruthSigil";
import { TheGauntlet } from "@/components/ui/TheGauntlet";
import { ReactorGauge } from "@/components/ui/ReactorGauge";
import { ProofDAG } from "@/components/ProofDAG";
import { DysonLayout } from "@/layouts/DysonLayout";

export default function Portal() {
    const { data: energyMap } = useEnergyMap();
    const nodeCount = energyMap?.node_count || 0;
    return (
        <DysonLayout>
            {/* 3D Background - Kept for depth, assuming it handles its own positioning */}
            <div className="absolute inset-0 z-0 opacity-50 pointer-events-none">
                <EnergyField />
            </div>

            {/* Content Overlay */}
            <div className="relative z-10 flex flex-col justify-center items-center min-h-[80vh]">

                {/* Hero Section */}
                <div className="text-center mb-12 space-y-6">
                    <h1 className="text-6xl md:text-8xl font-bold tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-dyson-plasma to-dyson-amber animate-pulse-slow text-glow font-mono">
                        INDUSTRI<span className="text-white">VERSE</span>
                    </h1>
                    <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto font-light tracking-wide">
                        Thermodynamic Dyson Sphere Control Interface
                    </p>
                    <div className="flex gap-4 justify-center">
                        <Link href="/dashboard">
                            <Button size="lg" className="bg-dyson-plasma text-white hover:bg-dyson-plasma/80 border-glow rounded-none clip-path-polygon">
                                Ignite Core <ArrowRight className="ml-2 h-4 w-4" />
                            </Button>
                        </Link>
                    </div>
                </div>

                {/* Module Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 w-full max-w-6xl px-4">
                    <Link href="/dashboard">
                        <GlassPanel variant="hover" className="flex flex-col items-center text-center gap-4 group border-dyson-teal/30 hover:border-dyson-teal">
                            <div className="p-4 rounded-full bg-dyson-teal/10 group-hover:bg-dyson-teal/20 transition-colors">
                                <Activity className="h-8 w-8 text-dyson-teal" />
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold text-dyson-teal">Mission Control</h3>
                                <p className="text-sm text-muted-foreground">Real-time system monitoring</p>
                            </div>
                        </GlassPanel>
                    </Link>

                    <Link href="/lab">
                        <GlassPanel variant="hover" className="flex flex-col items-center text-center gap-4 group border-dyson-plasma/30 hover:border-dyson-plasma">
                            <div className="p-4 rounded-full bg-dyson-plasma/10 group-hover:bg-dyson-plasma/20 transition-colors">
                                <Shield className="h-8 w-8 text-dyson-plasma" />
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-dyson-plasma">{nodeCount}</div>
                                <div className="text-xs text-muted-foreground">Active Nodes (Live)</div>
                            </div>
                        </GlassPanel>
                    </Link>

                    <Link href="/dna">
                        <GlassPanel variant="hover" className="flex flex-col items-center text-center gap-4 group border-dyson-amber/30 hover:border-dyson-amber">
                            <div className="p-4 rounded-full bg-dyson-amber/10 group-hover:bg-dyson-amber/20 transition-colors">
                                <Database className="h-8 w-8 text-dyson-amber" />
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold text-dyson-amber">Ontology DNA</h3>
                                <p className="text-sm text-muted-foreground">Knowledge graph explorer</p>
                            </div>
                        </GlassPanel>
                    </Link>

                    <Link href="/global">
                        <GlassPanel variant="hover" className="flex flex-col items-center text-center gap-4 group border-white/10 hover:border-white/30">
                            <div className="p-4 rounded-full bg-white/10 group-hover:bg-white/20 transition-colors">
                                <Globe className="h-8 w-8 text-white" />
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold">Global State</h3>
                                <p className="text-sm text-muted-foreground">Planetary threat map</p>
                            </div>
                        </GlassPanel>
                    </Link>
                </div>
            </div>

            {/* Proofs & UTID (The Gauntlet) */}
            <div className="fixed right-8 top-8 z-20 flex flex-col items-end gap-6 pointer-events-none">
                <div className="pointer-events-auto">
                    <TheGauntlet />
                </div>

                <div className="flex gap-4 items-start">
                    <div className="pointer-events-auto">
                        <TruthSigil />
                    </div>
                    <div className="pointer-events-auto pt-4">
                        <ReactorGauge />
                    </div>
                </div>

                <div className="pointer-events-auto h-48 w-64 opacity-80 hover:opacity-100 transition-opacity border border-dyson-teal/20 rounded-lg overflow-hidden bg-black/20 backdrop-blur-sm">
                    <ProofDAG />
                </div>
            </div>

            {/* Footer Status */}
            <div className="fixed bottom-0 left-0 w-full p-2 border-t border-dyson-amber/20 bg-black/60 backdrop-blur-md flex justify-between text-[10px] text-dyson-amber/60 font-mono uppercase tracking-widest z-30">
                <div>SYSTEM: ONLINE</div>
                <div>ENTROPY: STABLE</div>
                <div>DYSON SPHERE: ACTIVE</div>
            </div>
        </DysonLayout>
    );
}
