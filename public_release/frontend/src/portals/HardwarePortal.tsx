import React from 'react';
import DysonLayout from '../layout/DysonLayout';

const HardwarePortal: React.FC = () => {
    return (
        <DysonLayout>
            <div className="space-y-8">
                <div className="flex items-end justify-between border-b border-glass-border pb-4">
                    <div>
                        <h2 className="text-3xl font-light text-white mb-1">Hardware Portal</h2>
                        <p className="text-gray-400 font-mono text-sm">SECTOR: SILICON FORGE</p>
                    </div>
                    <div className="text-right">
                        <div className="text-2xl font-mono text-redshift">4.2 THz</div>
                        <div className="text-xs text-gray-500 uppercase">Clock Speed</div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* FPGA Synthesis Log */}
                    <div className="lg:col-span-2 bg-glass border border-glass-border rounded-xl p-6 backdrop-blur-md font-mono text-xs">
                        <h3 className="text-lg font-medium text-solar mb-4 font-sans">FPGA Synthesis Stream</h3>
                        <div className="h-64 overflow-y-auto space-y-1 text-gray-400 scrollbar-thin scrollbar-thumb-gray-700">
                            <div className="text-green-400">{">"} Initializing Yosys synthesis...</div>
                            <div>[INFO] Reading module 'blinky'...</div>
                            <div>[INFO] Optimizing logic gates...</div>
                            <div className="text-yellow-400">[WARN] Timing constraint tight on net clk_100mhz</div>
                            <div>[INFO] Place and route complete.</div>
                            <div className="text-plasma">{">"} Bitstream generated: bitstream_8f9a2b.bit</div>
                            <div className="animate-pulse">_</div>
                        </div>
                    </div>

                    {/* ASM Stats */}
                    <div className="bg-glass border border-glass-border rounded-xl p-6 backdrop-blur-md">
                        <h3 className="text-lg font-medium text-nebula mb-4">ASM Optimization</h3>
                        <div className="space-y-4">
                            <div className="flex justify-between items-center">
                                <span className="text-gray-400 text-sm">Throughput</span>
                                <span className="text-white font-mono">10x</span>
                            </div>
                            <div className="w-full bg-gray-800 h-2 rounded-full overflow-hidden">
                                <div className="bg-nebula h-full w-[90%]" />
                            </div>

                            <div className="flex justify-between items-center">
                                <span className="text-gray-400 text-sm">Latency</span>
                                <span className="text-white font-mono">0.1ms</span>
                            </div>
                            <div className="w-full bg-gray-800 h-2 rounded-full overflow-hidden">
                                <div className="bg-plasma h-full w-[10%]" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </DysonLayout>
    );
};

export default HardwarePortal;
