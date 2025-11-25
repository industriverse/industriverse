import React from 'react';
import { ShieldCheck, AlertTriangle, Clock } from 'lucide-react';

interface ProofBadgeProps {
    status: 'verified' | 'pending' | 'failed';
    type: string;
    confidence?: number;
    onClick?: () => void;
}

export const ProofBadge: React.FC<ProofBadgeProps> = ({ status, type, confidence, onClick }) => {
    const config = {
        verified: {
            icon: ShieldCheck,
            color: 'text-green-400',
            bg: 'bg-green-900/20',
            border: 'border-green-500/30'
        },
        pending: {
            icon: Clock,
            color: 'text-yellow-400',
            bg: 'bg-yellow-900/20',
            border: 'border-yellow-500/30'
        },
        failed: {
            icon: AlertTriangle,
            color: 'text-red-400',
            bg: 'bg-red-900/20',
            border: 'border-red-500/30'
        }
    }[status];

    const Icon = config.icon;

    return (
        <div
            onClick={onClick}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${config.bg} ${config.border} cursor-pointer hover:bg-opacity-50 transition-all`}
        >
            <Icon size={14} className={config.color} />
            <span className={`text-xs font-medium ${config.color}`}>
                {type}
                {confidence && <span className="ml-1 opacity-75">({(confidence * 100).toFixed(1)}%)</span>}
            </span>
        </div>
    );
};
