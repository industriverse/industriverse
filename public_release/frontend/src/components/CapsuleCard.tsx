import React from 'react';
import { Capsule } from '../types/capsule';
import UTIDLineage from './UTIDLineage';

interface CapsuleCardProps {
    capsule: Capsule;
    onIgnite: (id: string) => void;
    onLaunch?: (id: string) => void;
}

const CapsuleCard: React.FC<CapsuleCardProps> = ({ capsule, onIgnite, onLaunch }) => {
    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active': return 'bg-green-500';
            case 'error': return 'bg-red-500';
            default: return 'bg-gray-500';
        }
    };

    return (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 shadow-lg hover:shadow-xl transition-shadow duration-300">
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h3 className="text-lg font-bold text-white">{capsule.name}</h3>
                    <p className="text-xs text-gray-400">{capsule.capsule_id}</p>
                </div>
                <div className={`w-3 h-3 rounded-full ${getStatusColor(capsule.status)} animate-pulse`} />
            </div>

            <div className="space-y-3">
                <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Category</span>
                    <span className="text-blue-400 font-mono">{capsule.category}</span>
                </div>

                {capsule.utid && (
                    <div className="mt-4 flex justify-between items-center">
                        <div className="text-xs text-gray-500 font-mono">
                            <UTIDLineage utid={capsule.utid} />
                        </div>
                        {onLaunch && (
                            <button
                                onClick={() => onLaunch(capsule.capsule_id)}
                                className="px-3 py-1 bg-blue-600 hover:bg-blue-500 text-white text-xs rounded font-medium transition-colors"
                            >
                                LAUNCH DAC
                            </button>
                        )}
                    </div>
                )}

                <div className="flex justify-between text-sm">
                    <span className="text-gray-400">PRIN Score</span>
                    <span className={`font-mono ${capsule.prin_score >= 0.75 ? 'text-green-400' : 'text-yellow-400'}`}>
                        {capsule.prin_score.toFixed(3)}
                    </span>
                </div>

                <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Energy</span>
                    <span className="text-orange-400 font-mono">{capsule.energy_usage} J</span>
                </div>

                {capsule.utid && (
                    <div className="mt-4 pt-4 border-t border-gray-700">
                        <UTIDLineage utid={capsule.utid} />
                    </div>
                )}
            </div>

            <button
                onClick={() => onIgnite(capsule.capsule_id)}
                className="mt-4 w-full py-2 px-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded font-medium transition-colors duration-200 flex items-center justify-center gap-2"
            >
                <span>⚡ Ignite Capsule</span>
            </button>
        </div>
    );
};

export default CapsuleCard;
