import React from 'react';

const AuraRing = ({ status }) => {
    const getColor = (s) => {
        switch (s) {
            case 'active': return 'var(--stellar-gold)';
            case 'optimizing': return 'var(--uv-indigo)';
            case 'secure': return 'var(--nebula-teal)';
            case 'predicting': return 'var(--plasma-orange)';
            case 'bidding': return 'var(--photonic-violet)';
            default: return 'var(--cosmic-blue)';
        }
    };

    return (
        <div
            className="aura-ring"
            style={{
                borderTopColor: getColor(status),
                boxShadow: `0 0 10px ${getColor(status)}`
            }}
        ></div>
    );
};

export default AuraRing;
