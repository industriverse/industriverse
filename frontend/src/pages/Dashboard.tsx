import React, { useState, useEffect } from 'react';
import CapsuleCard from '../components/CapsuleCard';
import CapsuleOmniBar from '../components/CapsuleOmniBar';
import CreditTicker from '../components/CreditTicker';
import DACRenderer from '../components/DACRenderer';
import { useSystemPulse } from '../hooks/useSystemPulse';
import { Capsule } from '../types'; // Assuming Capsule type is defined here or imported

// Mock initial capsules if not fetching from API immediately
const INITIAL_CAPSULES: Capsule[] = [
    {
        capsule_id: "fusion_v1",
        name: "Fusion Control Alpha",
        category: "Energy",
        status: "optimizing",
        entropy: 0.042,
        prin_score: 0.98,
        utid: "utid:fusion:001",
        version: "1.0.0"
    },
    {
        capsule_id: "grid_v1",
        name: "Grid Immunity Prime",
        category: "Network",
        status: "active",
        entropy: 0.156,
        prin_score: 0.92,
        utid: "utid:grid:001",
        version: "1.0.0"
    },
    {
        capsule_id: "robotics_v1",
        name: "Apparel Robotics",
        category: "Manufacturing",
        status: "active",
        entropy: 0.089,
        prin_score: 0.95,
        utid: "utid:robotics:001",
        version: "1.0.0"
    },
    {
        capsule_id: "lifecycle_v1",
        name: "Garment Ledger",
        category: "Sustainability",
        status: "standby",
        entropy: 0.012,
        prin_score: 0.99,
        utid: "utid:lifecycle:001",
        version: "1.0.0"
    }
];

const Dashboard: React.FC = () => {
    const pulse = useSystemPulse();
    const [capsules, setCapsules] = useState<Capsule[]>(INITIAL_CAPSULES);
    const [selectedDacId, setSelectedDacId] = useState<string | null>(null);
    const [dacSchema, setDacSchema] = useState<any>(null);
    const [isLoadingDac, setIsLoadingDac] = useState(false);

    const handleIgnite = async (id: string) => {
        console.log(`Igniting ${id}...`);
        // Mock ignition logic
        setCapsules(prev => prev.map(c =>
            c.capsule_id === id ? { ...c, status: 'active' } : c
        ));
    };

    const handleLaunch = async (id: string) => {
        console.log(`Launching DAC for ${id}...`);
        setSelectedDacId(id);
        setIsLoadingDac(true);
        setDacSchema(null);

        try {
            // Fetch DAC Schema from Backend
            const response = await fetch(`http://localhost:8000/capsules/${id}/dac`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error(`Failed to load DAC: ${response.statusText}`);
            }

            const data = await response.json();
            if (data.status === 'success' && data.dac) {
                setDacSchema(data.dac.ui_schema);
            }
        } catch (err) {
            console.error("DAC Launch Error:", err);
            // Fallback/Mock for demo if backend is unreachable
            setDacSchema({
                components: [
                    { type: "Header", props: { title: `${id} (Offline Mode)` } },
                    { type: "ReactorGauge", props: { metric: "entropy" } }
                ]
            });
        } finally {
            setIsLoadingDac(false);
        }
    };

    const closeDac = () => {
        setSelectedDacId(null);
        setDacSchema(null);
    };

    return (
        <div className="min-h-screen bg-black text-gray-100 font-sans selection:bg-blue-500/30">
            {/* Header */}
            <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-md sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center font-bold text-white">
                            I
                        </div>
                        <h1 className="text-xl font-bold tracking-tight text-gray-100">
                            INDUSTRI<span className="text-blue-500">VERSE</span>
                        </h1>
                    </div>

                    <div className="flex-1 max-w-2xl mx-8">
                        <CapsuleOmniBar onIgnite={handleIgnite} />
                    </div>

                    <div className="flex items-center space-x-4">
                        <CreditTicker balance={pulse.credits} flowRate={pulse.creditFlow} />
                        <div className="w-8 h-8 rounded-full bg-gray-800 border border-gray-700 flex items-center justify-center text-xs font-mono">
                            OP
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 py-8">
                {/* Stats Row */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                    <div className="p-4 rounded-xl bg-gray-900/50 border border-gray-800">
                        <div className="text-sm text-gray-500 mb-1">Global Entropy</div>
                        <div className="text-2xl font-mono text-white">{pulse.globalEntropy.toFixed(4)}</div>
                    </div>
                    <div className="p-4 rounded-xl bg-gray-900/50 border border-gray-800">
                        <div className="text-sm text-gray-500 mb-1">Active Capsules</div>
                        <div className="text-2xl font-mono text-blue-400">{pulse.activeCapsules}</div>
                    </div>
                    <div className="p-4 rounded-xl bg-gray-900/50 border border-gray-800">
                        <div className="text-sm text-gray-500 mb-1">System Status</div>
                        <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                            <span className="text-green-400 font-medium">NOMINAL</span>
                        </div>
                    </div>
                    <div className="p-4 rounded-xl bg-gray-900/50 border border-gray-800">
                        <div className="text-sm text-gray-500 mb-1">Grid Frequency</div>
                        <div className="text-2xl font-mono text-purple-400">60.00 Hz</div>
                    </div>
                </div>

                {/* Capsules Grid */}
                <h2 className="text-lg font-semibold text-gray-300 mb-4 flex items-center">
                    <span className="mr-2">⚡</span> Sovereign Capsules
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {capsules.map(capsule => (
                        <CapsuleCard
                            key={capsule.capsule_id}
                            capsule={capsule}
                            onIgnite={handleIgnite}
                            onLaunch={handleLaunch}
                        />
                    ))}
                </div>
            </main>

            {/* DAC Modal */}
            {selectedDacId && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
                    <div className="w-full max-w-4xl bg-gray-950 rounded-2xl shadow-2xl border border-gray-800 overflow-hidden flex flex-col max-h-[90vh]">
                        {/* Modal Header */}
                        <div className="p-4 border-b border-gray-800 flex justify-between items-center bg-gray-900">
                            <div className="flex items-center space-x-2">
                                <span className="text-blue-500">◈</span>
                                <h2 className="font-bold text-lg">DAC: {selectedDacId}</h2>
                            </div>
                            <button onClick={closeDac} className="text-gray-400 hover:text-white transition-colors">
                                ✕
                            </button>
                        </div>

                        {/* Modal Content */}
                        <div className="flex-1 overflow-y-auto p-6">
                            {isLoadingDac ? (
                                <div className="flex flex-col items-center justify-center h-64 space-y-4">
                                    <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                                    <div className="text-blue-400 font-mono animate-pulse">Materializing DAC...</div>
                                </div>
                            ) : (
                                <DACRenderer schema={dacSchema} />
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
