import React from 'react';
import DysonLayout from '../layout/DysonLayout';
import { Globe, Radio, Satellite, ShieldAlert } from 'lucide-react';

const SpacePortal: React.FC = () => {
    const [currentMetrics, setCurrentMetrics] = React.useState<any>(null);

    React.useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/capsules/space_v1');
                const json = await res.json();
                setCurrentMetrics(json.data);
            } catch (e) {
                console.error("Failed to fetch space data", e);
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
                        <h2 className="text-3xl font-light text-white mb-1">Space Portal</h2>
                        <p className="text-gray-400 font-mono text-sm">SECTOR: ORBITAL DEFENSE</p>
                    </div>
                    <div className="text-right">
                        <div className="text-2xl font-mono text-blue-400">
                            {currentMetrics ? `LEO-${currentMetrics.altitude_km.toFixed(0)}` : 'LEO-4'}
                        </div>
                        <div className="text-xs text-gray-500 uppercase">Active Constellation</div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Orbital Map (Placeholder for 3D) */}
                    <div className="lg:col-span-2 bg-glass border border-glass-border rounded-xl p-6 backdrop-blur-md min-h-[400px] flex flex-col relative overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-b from-blue-900/10 to-transparent pointer-events-none" />
                        <h3 className="text-lg font-medium text-blue-400 mb-4 flex items-center gap-2 z-10">
                            <Globe className="w-5 h-5" />
                            Orbital Trajectory Map
                        </h3>

                        <div className="flex-1 flex items-center justify-center border border-dashed border-gray-700 rounded-lg bg-black/40 z-10 relative">
                            {/* Mock Orbit Lines */}
                            <div className="absolute w-64 h-64 border border-gray-700 rounded-full opacity-30" />
                            <div className="absolute w-96 h-96 border border-gray-700 rounded-full opacity-20" />
                            <div className="absolute w-32 h-32 bg-blue-500/10 rounded-full blur-xl" />

                            <div className="text-center z-20">
                                <Satellite className="w-12 h-12 text-blue-400 mx-auto mb-4" />
                                <p className="text-gray-500 font-mono text-sm">[ORBITAL TRACKING ACTIVE]</p>
                                <p className="text-xs text-blue-400 mt-2 animate-pulse">Scanning Sector 7G...</p>
                            </div>
                        </div>
                    </div>

                    {/* Telemetry & Security */}
                    <div className="space-y-6">
                        <div className="bg-glass border border-glass-border rounded-xl p-6 backdrop-blur-md">
                            <h3 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
                                <ShieldAlert className="w-5 h-5 text-red-400" />
                                Space Security (SatSec)
                            </h3>
                            <div className="space-y-4">
                                <div className="p-3 bg-red-900/10 border border-red-900/30 rounded-lg">
                                    <div className="flex justify-between items-center mb-1">
                                        <span className="text-red-400 text-xs font-bold uppercase">Jamming Detected</span>
                                        <span className="text-red-500 text-xs font-mono">RF-Band-X</span>
                                    </div>
                                    <div className="w-full bg-gray-800 h-1 rounded-full overflow-hidden">
                                        <div className="bg-red-500 h-full w-[70%] animate-pulse" />
                                    </div>
                                </div>

                                <div className="p-3 bg-green-900/10 border border-green-900/30 rounded-lg">
                                    <div className="flex justify-between items-center mb-1">
                                        <span className="text-green-400 text-xs font-bold uppercase">Camouflage</span>
                                        <span className="text-green-500 text-xs font-mono">ACTIVE</span>
                                    </div>
                                    <p className="text-xs text-gray-400">Spectral signature masked.</p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-glass border border-glass-border rounded-xl p-6 backdrop-blur-md">
                            <h3 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
                                <Radio className="w-5 h-5 text-yellow-400" />
                                Comms Link
                            </h3>
                            <div className="grid grid-cols-2 gap-4 text-center">
                                <div className="p-2 bg-gray-800/50 rounded-lg">
                                    <div className="text-xs text-gray-400">Velocity</div>
                                    <div className="text-lg font-mono text-white">
                                        {currentMetrics ? `${currentMetrics.velocity_kms.toFixed(2)}` : '---'} km/s
                                    </div>
                                </div>
                                <div className="p-2 bg-gray-800/50 rounded-lg">
                                    <div className="text-xs text-gray-400">Fuel</div>
                                    <div className="text-lg font-mono text-green-400">
                                        {currentMetrics ? `${currentMetrics.fuel_level.toFixed(1)}%` : '---'}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </DysonLayout>
    );
};

export default SpacePortal;
