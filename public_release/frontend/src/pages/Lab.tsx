import { GlassPanel } from '@/components/ui/GlassPanel';
import { Button } from '@/components/ui/button';
import { Link } from 'wouter';
import { ArrowLeft, Shield } from 'lucide-react';

export default function Lab() {
    return (
        <div className="min-h-screen bg-void-blue text-supernova-white p-8">
            <div className="container mx-auto">
                <div className="flex items-center gap-4 mb-8">
                    <Link href="/">
                        <Button variant="outline" size="icon">
                            <ArrowLeft className="h-4 w-4" />
                        </Button>
                    </Link>
                    <h1 className="text-3xl font-bold flex items-center gap-2">
                        <Shield className="h-8 w-8 text-plasma-pink" />
                        Simulation Lab
                    </h1>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-2">
                        <GlassPanel className="h-[600px] flex items-center justify-center bg-black/40">
                            <p className="text-muted-foreground">NVP Visualizer Placeholder (3D)</p>
                        </GlassPanel>
                    </div>
                    <div className="space-y-8">
                        <GlassPanel>
                            <h3 className="text-xl font-semibold mb-4">Entropy Monitor</h3>
                            <div className="space-y-4">
                                <div className="flex justify-between text-sm">
                                    <span>System Stability</span>
                                    <span className="text-quantum-teal">98.2%</span>
                                </div>
                                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                                    <div className="h-full bg-quantum-teal w-[98.2%]" />
                                </div>
                            </div>
                        </GlassPanel>

                        <GlassPanel>
                            <h3 className="text-xl font-semibold mb-4">Active Simulations</h3>
                            <p className="text-sm text-muted-foreground">No active simulations running.</p>
                            <Button className="w-full mt-4 bg-plasma-pink hover:bg-plasma-pink/80">
                                New Simulation
                            </Button>
                        </GlassPanel>
                    </div>
                </div>
            </div>
        </div>
    );
}
