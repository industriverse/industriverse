import React, { useState, KeyboardEvent } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

interface ResolutionResult {
    status: number;
    message: string;
    uri: string;
    utid?: string;
    payload_location?: string;
    telemetry?: any;
}

interface CapsuleOmniBarProps {
    onIgnite: (id: string) => void;
}

export default function CapsuleOmniBar({ onIgnite }: CapsuleOmniBarProps) {
    const [input, setInput] = useState('');
    const [resolving, setResolving] = useState(false);
    const [result, setResult] = useState<ResolutionResult | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleResolve = async () => {
        if (!input.trim()) return;

        // Basic validation for capsule:// scheme
        let uri = input.trim();
        if (!uri.startsWith('capsule://')) {
            // Allow shorthand for better UX? For now enforce protocol
            setError("URI must start with capsule://");
            return;
        }

        setResolving(true);
        setError(null);
        setResult(null);

        try {
            const response = await axios.post('/api/v1/capsules/resolve', { uri });
            const data = response.data;
            setResult(data);

            if (data.status !== 200) {
                setError(data.message || "Resolution failed");
            }
        } catch (err: any) {
            console.error("Resolution error", err);
            setError(err.response?.data?.detail || "Failed to resolve URI");
        } finally {
            setResolving(false);
        }
    };

    const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            handleResolve();
        }
    };

    const handleIgniteClick = () => {
        if (result && result.utid) {
            // Extract capsule ID from URI or use UTID if appropriate. 
            // The Dashboard handleIgnite expects a capsule ID.
            // Our mock resolver returns a UTID. 
            // For the prototype, we might need to parse the ID from the URI again 
            // or assume the backend returns the ID in telemetry or we can derive it.
            // URI: capsule://authority/domain/operation/version
            // We mapped operation to capsule name in the backend adapter.
            // Let's try to find the capsule ID from the URI or just pass the UTID if the dashboard supports it.
            // Dashboard expects capsule_id.
            // Let's parse the URI here to get the operation name which we mapped to capsule name.
            // Actually, let's just pass the full URI or UTID and let the dashboard handle it?
            // Dashboard.tsx: handleIgnite(id: string) -> axios.post(..., { capsule_id: id })
            // We need the capsule_id.
            // The backend resolve response doesn't explicitly return capsule_id, but it returns UTID.
            // Let's assume for now we can extract the "operation" part as the ID or name.

            // Hack for prototype: extract operation from URI string
            const parts = result.uri.replace('capsule://', '').split('/');
            // authority/domain/operation
            if (parts.length >= 3) {
                // We need the actual capsule_id (e.g. "fusion_control").
                // The backend adapter mapped `capsule.name == uri.operation`.
                // But `capsule_id` might be different.
                // Let's update the backend to return capsule_id in telemetry or metadata.
                // For now, let's assume operation IS the capsule_id for simplicity in testing.
                onIgnite(parts[2]);
            } else {
                console.warn("Could not extract capsule ID from URI", result.uri);
            }
        }
    };

    return (
        <div className="w-full max-w-4xl mx-auto mb-8 relative z-50">
            <div className="relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-teal-500 to-blue-600 rounded-lg blur opacity-25 group-hover:opacity-75 transition duration-1000 group-hover:duration-200"></div>
                <div className="relative flex items-center bg-gray-900 rounded-lg border border-gray-700 shadow-2xl overflow-hidden">
                    <div className="pl-4 text-gray-400">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                    </div>
                    <input
                        type="text"
                        className="w-full bg-transparent text-white px-4 py-4 focus:outline-none font-mono text-lg placeholder-gray-600"
                        placeholder="capsule://authority/domain/operation..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        disabled={resolving}
                    />
                    <div className="pr-2 flex items-center gap-2">
                        {resolving && (
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-teal-500 mr-2"></div>
                        )}
                        <button
                            onClick={handleResolve}
                            disabled={resolving || !input}
                            className="bg-gray-800 hover:bg-gray-700 text-gray-300 px-4 py-2 rounded-md text-sm font-medium transition-colors border border-gray-600"
                        >
                            RESOLVE
                        </button>
                    </div>
                </div>
            </div>

            <AnimatePresence>
                {(result || error) && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="absolute top-full left-0 right-0 mt-2 bg-gray-900/95 backdrop-blur-md border border-gray-700 rounded-lg shadow-xl p-4 overflow-hidden"
                    >
                        {error ? (
                            <div className="flex items-center text-red-400 gap-2">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                <span>{error}</span>
                            </div>
                        ) : result && (
                            <div className="flex justify-between items-center">
                                <div>
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className={`inline-block w-2 h-2 rounded-full ${result.status === 200 ? 'bg-green-500' : 'bg-yellow-500'}`}></span>
                                        <span className="font-mono text-sm text-teal-400">{result.uri}</span>
                                    </div>
                                    <div className="text-xs text-gray-500 font-mono">
                                        UTID: <span className="text-gray-300">{result.utid || 'Pending...'}</span>
                                    </div>
                                    {result.telemetry && (
                                        <div className="text-xs text-gray-600 mt-1">
                                            Source: {result.telemetry.resolution_source} | Latency: {result.telemetry.latency_ms}ms
                                        </div>
                                    )}
                                </div>
                                {result.status === 200 && (
                                    <button
                                        onClick={handleIgniteClick}
                                        className="bg-teal-600 hover:bg-teal-500 text-white px-6 py-2 rounded shadow-lg shadow-teal-500/20 font-bold tracking-wide transition-all transform hover:scale-105"
                                    >
                                        IGNITE
                                    </button>
                                )}
                            </div>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
