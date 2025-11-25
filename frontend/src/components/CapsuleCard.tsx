import React from 'react';

interface CapsuleCardProps {
    capsule: {
        capsule_id: string;
        name: string;
        category: string;
        status: 'active' | 'idle' | 'error';
        prin_score: number;
        energy_usage: number;
        utid?: string;
    };
    onIgnite: (id: string) => void;
}

const CapsuleCard: React.FC<CapsuleCardProps> = ({ capsule, onIgnite }) => {
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
                    <div className="mt-2 p-2 bg-gray-900 rounded text-xs font-mono text-gray-500 break-all">
                        {capsule.utid}
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
