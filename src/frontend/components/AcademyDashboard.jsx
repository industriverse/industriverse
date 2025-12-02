import React, { useState } from 'react';

const AcademyDashboard = () => {
    // Mock Data from UnifiedBridge
    const [profile] = useState({
        userId: 'USER_ADMIN',
        tier: 'LITHOGRAPHER',
        certs: ['ICDE', 'ICCD', 'ICSS']
    });

    const tiers = ['NOVICE', 'OPERATOR', 'ARCHITECT', 'LITHOGRAPHER'];
    const currentTierIndex = tiers.indexOf(profile.tier);

    return (
        <div className="p-6 bg-slate-900 text-white font-sans rounded-lg shadow-xl">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
                        Industriverse Academy
                    </h1>
                    <p className="text-gray-400">Identity & Certification</p>
                </div>
                <div className="text-right">
                    <span className="block text-sm text-gray-500">CURRENT TIER</span>
                    <span className="text-2xl font-bold text-purple-400">{profile.tier}</span>
                </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-gray-700 h-2 rounded-full mb-8 relative">
                <div
                    className="bg-purple-500 h-2 rounded-full transition-all duration-1000"
                    style={{ width: `${((currentTierIndex + 1) / tiers.length) * 100}%` }}
                ></div>
                {/* Nodes */}
                {tiers.map((t, i) => (
                    <div
                        key={t}
                        className={`absolute top-1/2 -translate-y-1/2 w-4 h-4 rounded-full border-2 border-gray-900 ${i <= currentTierIndex ? 'bg-purple-500' : 'bg-gray-600'
                            }`}
                        style={{ left: `${((i + 1) / tiers.length) * 100 - 10}%` }}
                    ></div>
                ))}
            </div>

            {/* Certifications */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {['ICDE', 'ICCD', 'ICSS'].map((cert) => (
                    <div
                        key={cert}
                        className={`p-4 border rounded-lg ${profile.certs.includes(cert)
                                ? 'border-green-500 bg-green-900/20'
                                : 'border-gray-700 opacity-50'
                            }`}
                    >
                        <div className="flex justify-between items-center mb-2">
                            <span className="font-bold text-lg">{cert}</span>
                            {profile.certs.includes(cert) && <span>✅</span>}
                        </div>
                        <p className="text-sm text-gray-300">
                            {cert === 'ICDE' ? 'Capsule Design & Engineering' :
                                cert === 'ICCD' ? 'DeploymentOps' : 'Simulation Strategy'}
                        </p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default AcademyDashboard;
