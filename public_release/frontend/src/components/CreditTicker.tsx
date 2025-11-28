import React, { useEffect, useState } from 'react';
import { useSystemPulse } from '../hooks/useSystemPulse';
import { motion, AnimatePresence } from 'framer-motion';

interface CreditEvent {
    id: string;
    uri: string;
    utid: string;
    execution_cost: number;
    timestamp: number;
}

export default function CreditTicker() {
    const { lastEvent } = useSystemPulse();
    const [events, setEvents] = useState<CreditEvent[]>([]);

    useEffect(() => {
        if (lastEvent && lastEvent.type === 'capsule.credit_flow') {
            const newEvent: CreditEvent = {
                id: Math.random().toString(36).substr(2, 9),
                uri: lastEvent.uri || 'unknown',
                utid: lastEvent.utid || 'unknown',
                execution_cost: lastEvent.execution_cost || 0,
                timestamp: Date.now(),
            };
            setEvents(prev => [newEvent, ...prev].slice(0, 5)); // Keep last 5 events
        }
    }, [lastEvent]);

    return (
        <div className="fixed bottom-0 left-0 right-0 bg-gray-900/90 border-t border-gray-800 backdrop-blur-md z-40 h-10 flex items-center overflow-hidden">
            <div className="px-4 flex items-center gap-2 border-r border-gray-700 h-full bg-gray-900 z-50">
                <span className="text-teal-500 font-bold text-xs tracking-wider">PROOF ECONOMY</span>
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            </div>

            <div className="flex-1 flex items-center overflow-hidden relative">
                <AnimatePresence initial={false}>
                    {events.length === 0 && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 0.5 }}
                            className="absolute left-4 text-xs text-gray-500 font-mono"
                        >
                            Waiting for transaction blocks...
                        </motion.div>
                    )}
                    {events.map((event) => (
                        <motion.div
                            key={event.id}
                            initial={{ x: 50, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            exit={{ x: -50, opacity: 0 }}
                            className="flex items-center gap-3 px-6 border-r border-gray-800/50 min-w-max"
                        >
                            <span className="text-xs font-mono text-gray-400">{new Date(event.timestamp).toLocaleTimeString()}</span>
                            <span className="text-xs font-bold text-blue-400">{event.uri.split('/').pop()}</span>
                            <span className="text-xs font-mono text-gray-600 truncate max-w-[80px]">{event.utid.substring(0, 8)}...</span>
                            <span className="text-xs font-bold text-green-400">+{event.execution_cost.toFixed(2)} CR</span>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>
        </div>
    );
}
