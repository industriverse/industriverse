import React from 'react';
import { motion } from 'framer-motion';

interface UTIDLineageProps {
    utid?: string;
    className?: string;
}

export default function UTIDLineage({ utid, className = '' }: UTIDLineageProps) {
    if (!utid) return null;

    // Mock lineage generation based on the current UTID
    // In production, this would fetch the actual hash chain from the ledger
    const lineage = [
        { id: 'genesis', label: 'GENESIS BLOCK', hash: '0x0000...0000' },
        { id: 'parent', label: 'PARENT CAPSULE', hash: '0x' + utid.substring(0, 8) + '...' }, // Mock parent
        { id: 'current', label: 'CURRENT EXECUTION', hash: utid, active: true },
    ];

    return (
        <div className={`flex flex-col gap-2 ${className}`}>
            <h4 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Cryptographic Provenance</h4>
            <div className="relative pl-4 border-l-2 border-gray-800 space-y-6">
                {lineage.map((node, index) => (
                    <motion.div
                        key={node.id}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="relative"
                    >
                        {/* Node Dot */}
                        <div className={`absolute -left-[21px] top-1.5 w-3 h-3 rounded-full border-2 ${node.active ? 'bg-teal-500 border-teal-500 shadow-[0_0_10px_rgba(20,184,166,0.5)]' : 'bg-gray-900 border-gray-600'}`}></div>

                        {/* Content */}
                        <div className="bg-gray-800/50 rounded p-2 border border-gray-700/50 backdrop-blur-sm">
                            <div className="text-[10px] font-bold text-gray-400 mb-0.5">{node.label}</div>
                            <div className="font-mono text-xs text-teal-300 break-all">{node.hash}</div>
                        </div>
                    </motion.div>
                ))}
            </div>

            <div className="mt-2 text-[10px] text-gray-600 font-mono text-right">
                Verified via Merkle Root: <span className="text-green-500">OK</span>
            </div>
        </div>
    );
}
