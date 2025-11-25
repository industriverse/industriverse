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
    const [isLoading, setIsLoading] = useState(false); // Added general loading state
    const [viewMode, setViewMode] = useState<'grid' | 'grouped'>('grouped');

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
        <div className="min-h-screen bg-black text-white font-sans selection:bg-cyan-500/30">
            {/* Header */}
            <header className="border-b border-slate-800 bg-slate-950/50 backdrop-blur-md sticky top-0 z-10">
                <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-cyan-500/20">
                            <span className="font-bold text-lg">I</span>
                        </div>
                        <h1 className="text-xl font-bold tracking-tight">
                            INDUSTRI<span className="text-cyan-400">VERSE</span>
                        </h1>
                    </div>

                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-900 rounded-full border border-slate-800">
                            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                            <span className="text-xs font-mono text-slate-400">SYSTEM ONLINE</span>
                        </div>
                        <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700" />
                    </div>
                </div>
            </header>

            <main className="container mx-auto px-4 py-8">
                <div className="flex justify-between items-center mb-8">
                    <h2 className="text-2xl font-light tracking-wide text-slate-400">
                        Sovereign Capsules <span className="text-cyan-500">({capsules.length})</span>
                    </h2>
                </div>

                {/* OmniBar */}
                <div className="mb-8">
                    <CapsuleOmniBar onIgnite={handleIgnite} />
                </div>

                {/* Credit Ticker */}
                <div className="mb-8">
                    <CreditTicker />
                </div>

                {isLoading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {[...Array(8)].map((_, i) => (
                            <div key={i} className="h-64 bg-slate-900/50 rounded-xl animate-pulse border border-slate-800" />
                        ))}
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {capsules.map((capsule) => (
                            <CapsuleCard
                                key={capsule.capsule_id}
                                capsule={capsule}
                                onIgnite={handleIgnite}
                                onLaunch={handleLaunch}
                            />
                        ))}
                    </div>
                )}
            </main>

            {/* DAC Modal */}
            {selectedDacId && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
                    <div className="w-full max-w-6xl bg-gray-950 rounded-2xl shadow-2xl border border-gray-800 overflow-hidden flex flex-col h-[90vh]">
                        {/* Modal Header */}
                        <div className="p-4 border-b border-gray-800 flex justify-between items-center bg-gray-900">
                            <div className="flex items-center space-x-2">
                                <span className="text-cyan-500">◈</span>
                                <h2 className="font-bold text-lg text-white">DAC: {selectedDacId}</h2>
                            </div>
                            <button onClick={closeDac} className="text-gray-400 hover:text-white transition-colors">
                                ✕
                            </button>
                        </div>

                        {/* Modal Content */}
                        <div className="flex-1 overflow-y-auto p-6 bg-black">
                            {isLoadingDac ? (
                                <div className="flex flex-col items-center justify-center h-64 space-y-4">
                                    <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
                                    <div className="text-cyan-400 font-mono animate-pulse">Materializing DAC...</div>
                                </div>
                            ) : dacSchema ? (
                                <DACRenderer schema={dacSchema} />
                            ) : (
                                <div className="text-red-500">Failed to load DAC schema</div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
