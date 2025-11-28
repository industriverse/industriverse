import React from 'react';
import DysonLayout from '../layout/DysonLayout';
import { Sprout, HeartPulse, RefreshCw, Bug } from 'lucide-react';

const ALifePortal: React.FC = () => {
    return (
        <DysonLayout>
            <div className="space-y-8">
                <div className="flex items-end justify-between border-b border-glass-border pb-4">
                    <div>
                        <h2 className="text-3xl font-light text-white mb-1">Artificial Life Portal</h2>
                        <p className="text-gray-400 font-mono text-sm">SECTOR: DIGITAL EVOLUTION</p>
                    </div>
                    <div className="text-right">
                        <div className="text-2xl font-mono text-pink-400">Gen 429</div>
                        <div className="text-xs text-gray-500 uppercase">Evolutionary Epoch</div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* NCA Grid (Placeholder for Canvas) */}
                    <div className="lg:col-span-2 bg-glass border border-glass-border rounded-xl p-6 backdrop-blur-md min-h-[400px] flex flex-col relative overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-tr from-pink-900/10 to-transparent pointer-events-none" />
                        <h3 className="text-lg font-medium text-pink-400 mb-4 flex items-center gap-2 z-10">
                            <Sprout className="w-5 h-5" />
                            Neural Cellular Automata (NCA)
                        </h3>

                        <div className="flex-1 grid grid-cols-32 grid-rows-32 gap-px bg-black/40 border border-gray-800 p-1 z-10">
                            {/* Mock Grid Cells */}
                            {Array.from({ length: 256 }).map((_, i) => (
                                <div
                                    key={i}
                                    className={`
                      w-full h-full rounded-sm transition-colors duration-500
                      ${Math.random() > 0.8 ? 'bg-pink-500/50 animate-pulse' : 'bg-gray-900/50'}
                    `}
                                />
                            ))}
                        </div>
                        <div className="absolute bottom-4 right-4 z-20 bg-black/60 backdrop-blur px-3 py-1 rounded text-xs text-pink-400 font-mono border border-pink-900/30">
                            Growth Rule: Conway-Variant-B
                        </div>
                    </div>

                    {/* Ecosystem Stats */}
                    <div className="space-y-6">
                        <div className="bg-glass border border-glass-border rounded-xl p-6 backdrop-blur-md">
                            <h3 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
                                <HeartPulse className="w-5 h-5 text-red-400" />
                                Population Health
                            </h3>
                            <div className="space-y-4">
                                <div>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="text-gray-400">Agent Count</span>
                                        <span className="text-white font-mono">1,024</span>
                                    </div>
                                    <div className="w-full bg-gray-800 h-1.5 rounded-full overflow-hidden">
                                        <div className="bg-green-500 h-full w-[60%]" />
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="text-gray-400">Diversity Index</span>
                                        <span className="text-white font-mono">0.85</span>
                                    </div>
                                    <div className="w-full bg-gray-800 h-1.5 rounded-full overflow-hidden">
                                        <div className="bg-blue-500 h-full w-[85%]" />
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-glass border border-glass-border rounded-xl p-6 backdrop-blur-md">
                            <h3 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
                                <RefreshCw className="w-5 h-5 text-yellow-400" />
                                Self-Repair Log
                            </h3>
                            <ul className="space-y-3 text-sm">
                                <li className="flex items-center gap-3 text-gray-400">
                                    <Bug className="w-4 h-4 text-red-400" />
                                    <span>Damage detected at sector [12, 4]</span>
                                </li>
                                <li className="flex items-center gap-3 text-gray-300">
                                    <RefreshCw className="w-4 h-4 text-green-400 animate-spin-slow" />
                                    <span>Regenerating tissue...</span>
                                </li>
                                <li className="flex items-center gap-3 text-gray-500">
                                    <span className="w-4 h-4 flex items-center justify-center text-xs">✓</span>
                                    <span>Sector [8, 9] restored.</span>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </DysonLayout>
    );
};

export default ALifePortal;
