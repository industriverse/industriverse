import React, { useState, useEffect } from 'react';
import CapsuleCard from '../components/CapsuleCard';
import axios from 'axios';

// Define types locally for now, should be shared
interface Capsule {
    capsule_id: string;
    name: string;
    category: string;
    status: 'active' | 'idle' | 'error';
    prin_score: number;
    energy_usage: number;
    utid?: string;
}

const Dashboard: React.FC = () => {
    const [capsules, setCapsules] = useState<Capsule[]>([]);
    const [loading, setLoading] = useState(true);

    // Mock data for initial render until backend connection is fully verified
    const mockCapsules: Capsule[] = [
        {
            capsule_id: 'capsule:fusion:v1',
            name: 'Fusion Reactor Control',
            category: 'Category A',
            status: 'active',
            prin_score: 0.92,
            energy_usage: 4500,
            utid: 'UTID:REAL:HOST:FUSION:20251124:A1B2'
        },
        {
            capsule_id: 'capsule:motor:v1',
            name: 'Electric Motor Mfg',
            category: 'Category A',
            status: 'idle',
            prin_score: 0.88,
            energy_usage: 1200
        },
        // Add more mocks or fetch from API
    ];

    useEffect(() => {
        const fetchCapsules = async () => {
            try {
                const response = await axios.get('/api/v1/capsules/');
                // Transform backend data to frontend model
                const mappedCapsules: Capsule[] = response.data.map((c: any) => ({
                    capsule_id: c.id,
                    name: c.name,
                    category: c.category,
                    status: 'idle', // Default status as backend doesn't return it yet
                    prin_score: 0.85 + Math.random() * 0.15, // Mock score for now
                    energy_usage: Math.floor(Math.random() * 5000), // Mock energy
                    utid: undefined
                }));
                setCapsules(mappedCapsules);
            } catch (error) {
                console.error("Failed to fetch capsules", error);
                // Fallback to mocks if backend fails
                const generatedCapsules = Array.from({ length: 27 }, (_, i) => ({
                    capsule_id: `capsule:generic:${i + 1}`,
                    name: `Sovereign Capsule ${i + 1}`,
                    category: i < 7 ? 'Category A' : i < 15 ? 'Category B' : i < 22 ? 'Category C' : 'Category D',
                    status: Math.random() > 0.8 ? 'active' : 'idle',
                    prin_score: 0.75 + Math.random() * 0.25,
                    energy_usage: Math.floor(Math.random() * 5000),
                })) as Capsule[];
                setCapsules(generatedCapsules);
            } finally {
                setLoading(false);
            }
        };

        fetchCapsules();
    }, []);

    const handleIgnite = async (id: string) => {
        console.log(`Igniting capsule ${id}...`);
        // Optimistic update
        setCapsules(prev => prev.map(c =>
            c.capsule_id === id ? { ...c, status: 'active', energy_usage: c.energy_usage + 100 } : c
        ));

        try {
            const response = await axios.post(`/api/v1/capsules/execute`, {
                capsule_id: id,
                payload: { action: "ignite" },
                priority: "high"
            });

            // Update with real UTID from response
            const utid = response.data.utid;
            setCapsules(prev => prev.map(c =>
                c.capsule_id === id ? { ...c, utid: utid } : c
            ));

        } catch (error) {
            console.error("Ignition failed", error);
            setCapsules(prev => prev.map(c =>
                c.capsule_id === id ? { ...c, status: 'error' } : c
            ));
        }
    };

    return (
        <div className="min-h-screen bg-gray-900 text-white p-8">
            <header className="mb-8">
                <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-teal-400">
                    Mission Control: 27 Sovereign Capsules
                </h1>
                <p className="text-gray-400 mt-2">Thermodynamic Discovery Loop V16 Status</p>
            </header>

            {loading ? (
                <div className="flex justify-center items-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {capsules.map(capsule => (
                        <CapsuleCard
                            key={capsule.capsule_id}
                            capsule={capsule}
                            onIgnite={handleIgnite}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

export default Dashboard;
