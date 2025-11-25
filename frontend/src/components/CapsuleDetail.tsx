import React, { useState, useEffect } from 'react';

interface CapsuleDetailProps {
    capsule: {
        id: string;
        name: string;
        category: string;
        status: string;
        utid: string;
    };
    onClose: () => void;
}

const CapsuleDetail: React.FC<CapsuleDetailProps> = ({ capsule, onClose }) => {
    const [topology, setTopology] = useState<any>(null);
    const [loadingTopology, setLoadingTopology] = useState(true);
    const [executionStatus, setExecutionStatus] = useState<'IDLE' | 'RUNNING' | 'SUCCESS' | 'ERROR'>('IDLE');
    const [executionResult, setExecutionResult] = useState<any>(null);

    useEffect(() => {
        const fetchTopology = async () => {
            try {
                const response = await fetch(`http://localhost:8000/v1/capsules/${capsule.id}/topology`, {
                    headers: {
                        'X-UTID': 'UTID:REAL:BROWSER:DASHBOARD:20251124:nonce'
                    }
                });
                if (response.ok) {
                    const data = await response.json();
                    setTopology(data);
                }
            } catch (error) {
                console.error("Failed to fetch topology", error);
            } finally {
                setLoadingTopology(false);
            }
        };

        fetchTopology();
    }, [capsule.id]);

    const handleIgnite = async () => {
        setExecutionStatus('RUNNING');
        try {
            const response = await fetch('http://localhost:8000/v1/capsules/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-UTID': 'UTID:REAL:BROWSER:DASHBOARD:20251124:nonce'
                },
                body: JSON.stringify({
                    capsule_id: capsule.id,
                    payload: { trigger: "manual_override" },
                    priority: "high"
                })
            });

            if (response.ok) {
                const data = await response.json();
                setExecutionResult(data);
                setExecutionStatus('SUCCESS');
            } else {
                setExecutionStatus('ERROR');
            }
        } catch (error) {
            console.error("Execution failed", error);
            setExecutionStatus('ERROR');
        }
    };

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 border border-gray-700 rounded-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl flex flex-col">
                {/* Header */}
                <div className="p-6 border-b border-gray-800 flex justify-between items-start">
                    <div>
                        <h2 className="text-2xl font-bold text-white mb-1">{capsule.name}</h2>
                        <div className="flex items-center space-x-3 text-sm">
                            <span className="text-gray-400 font-mono">{capsule.id}</span>
                            <span className="px-2 py-0.5 rounded bg-gray-800 text-gray-300 border border-gray-700 text-xs">
                                {capsule.category}
                            </span>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-500 hover:text-white transition-colors"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <div className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Left Column: Topology & Physics */}
                    <div className="space-y-6">
                        <div>
                            <h3 className="text-lg font-semibold text-blue-400 mb-3 flex items-center">
                                <span className="w-2 h-2 bg-blue-400 rounded-full mr-2"></span>
                                Physics Topology
                            </h3>
                            <div className="bg-black/50 rounded-lg p-4 border border-gray-800 font-mono text-sm text-gray-300 h-48 overflow-y-auto">
                                {loadingTopology ? (
                                    <div className="animate-pulse">Loading topology signature...</div>
                                ) : topology ? (
                                    <pre className="whitespace-pre-wrap">{JSON.stringify(topology.physics_topology, null, 2)}</pre>
                                ) : (
                                    <span className="text-red-400">Failed to load topology data.</span>
                                )}
                            </div>
                        </div>

                        <div>
                            <h3 className="text-lg font-semibold text-purple-400 mb-3 flex items-center">
                                <span className="w-2 h-2 bg-purple-400 rounded-full mr-2"></span>
                                Governing Equations
                            </h3>
                            <div className="bg-black/50 rounded-lg p-4 border border-gray-800 font-mono text-sm text-gray-300">
                                {loadingTopology ? (
                                    <div className="animate-pulse">Loading equations...</div>
                                ) : topology ? (
                                    <ul className="list-disc list-inside space-y-1">
                                        {topology.domain_equations.map((eq: string, i: number) => (
                                            <li key={i}>{eq}</li>
                                        ))}
                                    </ul>
                                ) : (
                                    <span className="text-red-400">No equations found.</span>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Right Column: Control & Status */}
                    <div className="space-y-6 flex flex-col">
                        <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700 flex-1 flex flex-col">
                            <h3 className="text-lg font-semibold text-green-400 mb-4 flex items-center">
                                <span className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></span>
                                Command Center
                            </h3>

                            <div className="flex-1 space-y-4">
                                <div className="flex justify-between items-center py-2 border-b border-gray-700">
                                    <span className="text-gray-400">Current Status</span>
                                    <span className="text-white font-mono">{capsule.status}</span>
                                </div>
                                <div className="flex justify-between items-center py-2 border-b border-gray-700">
                                    <span className="text-gray-400">Active UTID</span>
                                    <span className="text-white font-mono text-xs truncate max-w-[200px]" title={capsule.utid}>
                                        {capsule.utid}
                                    </span>
                                </div>
                            </div>

                            <div className="mt-8">
                                <button
                                    onClick={handleIgnite}
                                    disabled={executionStatus === 'RUNNING'}
                                    className={`w-full py-4 rounded-lg font-bold text-lg tracking-wider transition-all duration-300 flex items-center justify-center space-x-2
                                        ${executionStatus === 'RUNNING'
                                            ? 'bg-gray-700 cursor-not-allowed text-gray-400'
                                            : 'bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500 text-white shadow-lg shadow-orange-900/20'
                                        }`}
                                >
                                    {executionStatus === 'RUNNING' ? (
                                        <>
                                            <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                            </svg>
                                            IGNITING...
                                        </>
                                    ) : (
                                        <>
                                            <span>IGNITE CAPSULE</span>
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                            </svg>
                                        </>
                                    )}
                                </button>
                            </div>

                            {/* Execution Result */}
                            {executionResult && (
                                <div className="mt-6 p-4 bg-black/40 rounded border border-green-900/50 animate-in fade-in slide-in-from-bottom-4">
                                    <div className="text-green-400 font-mono text-sm mb-2">Build Successful</div>
                                    <div className="text-gray-400 text-xs font-mono break-all">
                                        New UTID: <span className="text-white">{executionResult.utid}</span>
                                    </div>
                                    <div className="text-gray-400 text-xs font-mono mt-1">
                                        Status: <span className="text-white">{executionResult.status}</span>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CapsuleDetail;
