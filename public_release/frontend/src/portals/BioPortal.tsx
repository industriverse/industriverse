import React from 'react';
import DysonLayout from '../layout/DysonLayout';
import { Activity, Dna, FlaskConical } from 'lucide-react';

const BioPortal: React.FC = () => {
    const [currentMetrics, setCurrentMetrics] = React.useState<any>(null);

    React.useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/capsules/bio_v1');
                const json = await res.json();
                setCurrentMetrics(json.data);
            } catch (e) {
                console.error("Failed to fetch bio data", e);
            }
        };

        const interval = setInterval(fetchData, 1000);
        return () => clearInterval(interval);
    }, []);

    return (
        <DysonLayout>
            <div className="space-y-8">
                <div className="flex items-end justify-between border-b border-glass-border pb-4">
                    <div>
                        <h2 className="text-3xl font-light text-white mb-1">Bio / Chem Portal</h2>
                        <p className="text-gray-400 font-mono text-sm">SECTOR: MOLECULAR FORGE</p>
                    </div>
                    <div className="text-right">
                        <div className="text-2xl font-mono text-green-400">
                            {currentMetrics ? `${currentMetrics.rmsd_accuracy.toFixed(3)} Å` : '---'}
                        </div>
                        <div className="text-xs text-gray-500 uppercase">RMSD Accuracy</div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Protein Folding Viewer (Placeholder for 3D) */}
                    <div className="lg:col-span-2 bg-glass border border-glass-border rounded-xl p-6 backdrop-blur-md min-h-[400px] flex flex-col relative overflow-hidden group">
                        <div className="absolute inset-0 bg-gradient-to-br from-green-500/5 to-transparent pointer-events-none" />
                        <h3 className="text-lg font-medium text-green-400 mb-4 flex items-center gap-2 z-10">
                            <Dna className="w-5 h-5" />
                            Protein Folding Simulation
                        </h3>

                        <div className="flex-1 flex items-center justify-center border border-dashed border-gray-700 rounded-lg bg-black/20 z-10">
                            <div className="text-center">
                                <Dna className="w-16 h-16 text-green-500/20 mx-auto mb-4 animate-spin-slow" />
                                <p className="text-gray-500 font-mono text-sm">[MOLECULAR RENDERER INITIALIZING...]</p>
                                <p className="text-xs text-gray-600 mt-2">Target: Cas9-Variant-Delta</p>
                            </div>
                        </div>
                    </div>

                    {/* Stats Panel */}
                    <div className="space-y-6">
                        <div className="bg-glass border border-glass-border rounded-xl p-6 backdrop-blur-md">
                            <h3 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
                                <FlaskConical className="w-5 h-5 text-purple-400" />
                                Reaction Kinetics
                            </h3>
                            <div className="space-y-4">
                                <div>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="text-gray-400">Catalysis Rate</span>
                                        <span className="text-purple-400 font-mono">
                                            {currentMetrics ? `${(currentMetrics.reaction_rate / 1e6).toFixed(1)}M /s` : '---'}
                                        </span>
                                    </div>
                                    <div className="w-full bg-gray-800 h-1.5 rounded-full overflow-hidden">
                                        <div className="bg-purple-500 h-full w-[85%]" />
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="text-gray-400">Yield</span>
                                        <span className="text-purple-400 font-mono">
                                            {currentMetrics ? `${currentMetrics.folding_progress}%` : '---'}
                                        </span>
                                    </div>
                                    <div className="w-full bg-gray-800 h-1.5 rounded-full overflow-hidden">
                                        <div className="bg-purple-500 h-full w-[99%]" />
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-glass border border-glass-border rounded-xl p-6 backdrop-blur-md">
                            <h3 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
                                <Activity className="w-5 h-5 text-blue-400" />
                                Active Experiments
                            </h3>
                            <ul className="space-y-3 text-sm">
                                <li className="flex items-center justify-between border-b border-gray-800 pb-2">
                                    <span className="text-gray-300">Ligand Binding V4</span>
                                    <span className="text-green-400 text-xs px-2 py-0.5 bg-green-900/20 rounded">RUNNING</span>
                                </li>
                                <li className="flex items-center justify-between border-b border-gray-800 pb-2">
                                    <span className="text-gray-300">Toxicity Screen</span>
                                    <span className="text-yellow-400 text-xs px-2 py-0.5 bg-yellow-900/20 rounded">QUEUED</span>
                                </li>
                                <li className="flex items-center justify-between">
                                    <span className="text-gray-300">CRISPR Off-target</span>
                                    <span className="text-blue-400 text-xs px-2 py-0.5 bg-blue-900/20 rounded">ANALYZING</span>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </DysonLayout>
    );
};

export default BioPortal;
