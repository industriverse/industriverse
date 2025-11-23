import { Link } from 'wouter';
import EnergyField from '@/components/3d/EnergyField';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { Button } from '@/components/ui/button';
import { ArrowRight, Activity, Zap, Globe, Database, Shield } from 'lucide-react';
import { useEnergyMap } from "@/api/thermodynamic";

export default function Portal() {
    const { data: energyMap, isLoading } = useEnergyMap();
    const nodeCount = energyMap?.node_count || 0;
    return (
        <div className="relative w-full h-screen overflow-hidden bg-void-blue text-supernova-white">
            {/* 3D Background */}
            <EnergyField />

            {/* Content Overlay */}
            <div className="relative z-10 container mx-auto h-full flex flex-col justify-center items-center">

                {/* Hero Section */}
                <div className="text-center mb-12 space-y-6">
                    <h1 className="text-6xl md:text-8xl font-bold tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-quantum-teal to-plasma-pink animate-pulse-slow text-glow">
                        INDUSTRI<span className="text-white">VERSE</span>
                    </h1>
                    <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto">
                        Sovereign Consciousness Engine v2.0
                    </p>
                    <div className="flex gap-4 justify-center">
                        <Link href="/dashboard">
                            <Button size="lg" className="bg-quantum-teal text-void-blue hover:bg-quantum-teal/80 border-glow">
                                Enter System <ArrowRight className="ml-2 h-4 w-4" />
                            </Button>
                        </Link>
                    </div>
                </div>

                {/* Module Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 w-full max-w-6xl px-4">
                    <Link href="/dashboard">
                        <GlassPanel variant="hover" className="flex flex-col items-center text-center gap-4 group">
                            <div className="p-4 rounded-full bg-quantum-teal/10 group-hover:bg-quantum-teal/20 transition-colors">
                                <Activity className="h-8 w-8 text-quantum-teal" />
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold">Mission Control</h3>
                                <p className="text-sm text-muted-foreground">Real-time system monitoring</p>
                            </div>
                        </GlassPanel>
                    </Link>

                    <Link href="/lab">
                        <GlassPanel variant="hover" className="flex flex-col items-center text-center gap-4 group">
                            <div className="p-4 rounded-full bg-plasma-pink/10 group-hover:bg-plasma-pink/20 transition-colors">
                                <Shield className="h-8 w-8 text-plasma-pink" />
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-quantum-teal">{nodeCount}</div>
                                <div className="text-xs text-muted-foreground">Active Nodes (Live)</div>
                            </div>
                        </GlassPanel>
                    </Link>

                    <Link href="/dna">
                        <GlassPanel variant="hover" className="flex flex-col items-center text-center gap-4 group">
                            <div className="p-4 rounded-full bg-entropy-orange/10 group-hover:bg-entropy-orange/20 transition-colors">
                                <Database className="h-8 w-8 text-entropy-orange" />
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold">Ontology DNA</h3>
                                <p className="text-sm text-muted-foreground">Knowledge graph explorer</p>
                            </div>
                        </GlassPanel>
                    </Link>

                    <Link href="/global">
                        <GlassPanel variant="hover" className="flex flex-col items-center text-center gap-4 group">
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

            {/* Footer Status */}
            <div className="absolute bottom-0 w-full p-4 border-t border-white/5 bg-black/40 backdrop-blur-sm flex justify-between text-xs text-muted-foreground">
                <div>SYSTEM: ONLINE</div>
                <div>ENTROPY: STABLE</div>
                <div>VERSION: 2.0.0-alpha</div>
            </div>
        </div>
    );
}
