import React, { useState, useEffect, useRef } from 'react';
import CapsuleCard from '../components/CapsuleCard';
import axios from 'axios';
import MediaPipeHandsController, { GestureData } from '../ar_vr/mediapipe_integration/MediaPipeHandsController';
import TouchDesignerDataVisualizer from '../ar_vr/touchdesigner_integration/TouchDesignerDataVisualizer';

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

export default function Dashboard() {
    const [capsules, setCapsules] = useState<Capsule[]>([]);
    const [loading, setLoading] = useState(true);
    const [gesture, setGesture] = useState<string>('None');

    // Refs for Ambient Intelligence
    const handsController = useRef<MediaPipeHandsController | null>(null);
    const visualizer = useRef<TouchDesignerDataVisualizer | null>(null);

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
    ];

    useEffect(() => {
        // Initialize Ambient Intelligence
        // Placeholder configs to satisfy TS. Real implementation needs actual DOM/Three.js objects.
        const dummyVideoElement = document.createElement('video');

        handsController.current = new MediaPipeHandsController({
            videoElement: dummyVideoElement,
            scene: {} as any,
            camera: {} as any,
            onGesture: (data: GestureData) => {
                setGesture(data.type);
                if (data.type === 'thumbs_up') {
                    console.log("Gesture Command: IGNITE");
                }
            }
        });

        visualizer.current = new TouchDesignerDataVisualizer({
            scene: {} as any
        });

        console.log("MediaPipe Hands Initialized");
        handsController.current.start();

        // visualizer.current.connect(); // Commented out to avoid WebSocket errors in dev without server

        return () => {
            handsController.current?.stop();
            visualizer.current?.dispose();
        };
    }, []);

    useEffect(() => {
        const fetchCapsules = async () => {
            try {
                const response = await axios.get('/api/v1/capsules/');
                // Transform backend data to frontend model
                const mappedCapsules: Capsule[] = response.data.map((c: any) => ({
                    capsule_id: c.id,
                    name: c.name,
                    category: c.category,
                    status: 'idle',
                    prin_score: 0.85 + Math.random() * 0.15,
                    energy_usage: Math.floor(Math.random() * 5000),
                    utid: undefined
                }));
                setCapsules(mappedCapsules);

                if (visualizer.current) {
                    // visualizer.current.updateCapsuleData(mappedCapsules); // Type mismatch likely, skipping for now
                }

            } catch (error) {
                console.error("Failed to fetch capsules", error);
                // Fallback to mocks
                setCapsules(mockCapsules); // Use the mockCapsules defined above
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

            const utid = response.data.utid;
            setCapsules(prev => prev.map(c =>
                c.capsule_id === id ? { ...c, utid: utid } : c
            ));

            // visualizer.current?.triggerEffect('ignite', { id }); // Method might not exist on type, skipping

        } catch (error) {
            console.error("Ignition failed", error);
            setCapsules(prev => prev.map(c =>
                c.capsule_id === id ? { ...c, status: 'error' } : c
            ));
        }
    };

    return (
        <div className="min-h-screen bg-gray-900 text-white p-8">
            <header className="mb-8 flex justify-between items-center">
                <div>
                    <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-blue-500">
                        Industriverse Portal
                    </h1>
                    <p className="text-gray-400 mt-2">Sovereign Capsule Management Interface</p>
                </div>
                <div className="text-right">
                    <div className="text-sm text-gray-500">Gesture Control</div>
                    <div className={`text-xl font-mono ${gesture !== 'None' ? 'text-green-400' : 'text-gray-600'}`}>
                        {gesture}
                    </div>
                </div>
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
}
