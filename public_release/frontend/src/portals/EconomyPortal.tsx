import React from 'react';
import DysonLayout from '../layout/DysonLayout';
import { Database, TrendingUp, Coins, Network } from 'lucide-react';

const EconomyPortal: React.FC = () => {
    const [currentMetrics, setCurrentMetrics] = React.useState<any>(null);

    React.useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/capsules/token_v1');
                const json = await res.json();
                setCurrentMetrics(json.data);
            } catch (e) {
                console.error("Failed to fetch economy data", e);
            }
        };

        const interval = setInterval(fetchData, 1000);
        return () => clearInterval(interval);
    }, []);

    return (
        <DysonLayout>
            <div className="space-y-8">
                <div className="flex items-end justify-between border-b border-glass-border pb-4">
                    <div>
                        <h2 className="text-3xl font-light text-white mb-1">Economy Portal</h2>
                        <p className="text-gray-400 font-mono text-sm">SECTOR: THERMODYNAMIC LEDGER</p>
                    </div>
                    <div className="text-right">
                        <div className="text-2xl font-mono text-solar">
                            {currentMetrics ? `${(currentMetrics.market_cap / 10000).toFixed(0)} XEX` : '---'}
                        </div>
                        <div className="text-xs text-gray-500 uppercase">Total Exergy Staked</div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Ledger Stream */}
                    <div className="lg:col-span-2 bg-glass border border-glass-border rounded-xl p-6 backdrop-blur-md min-h-[400px] flex flex-col">
                        <h3 className="text-lg font-medium text-solar mb-4 flex items-center gap-2">
                            <Database className="w-5 h-5" />
                            XRPL Transaction Stream
                        </h3>

                        <div className="flex-1 overflow-hidden relative">
                            <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black/50 pointer-events-none z-10" />
                            <div className="space-y-2 font-mono text-xs">
                                {Array.from({ length: 8 }).map((_, i) => (
                                    <div key={i} className="flex items-center justify-between p-2 border-b border-gray-800/50 hover:bg-white/5 transition-colors">
                                        <div className="flex items-center gap-2">
                                            <span className="text-gray-500">{new Date().toLocaleTimeString()}</span>
                                            <span className="text-blue-400">TX_HASH_{Math.random().toString(36).substring(7)}</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <span className="text-gray-400">Mint Capsule</span>
                                            <span className="text-solar">+{Math.floor(Math.random() * 100)} XEX</span>
                                        </div>
                                    </div>
                                ))}
                                <div className="flex items-center justify-between p-2 border-b border-gray-800/50 animate-pulse bg-solar/10">
                                    <div className="flex items-center gap-2">
                                        <span className="text-gray-500">NOW</span>
                                        <span className="text-blue-400">PENDING...</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <span className="text-gray-400">Atomic Swap</span>
                                        <span className="text-solar">...</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Market Stats */}
                    <div className="space-y-6">
                        <div className="bg-glass border border-glass-border rounded-xl p-6 backdrop-blur-md">
                            <h3 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
                                <TrendingUp className="w-5 h-5 text-green-400" />
                                Market Dynamics
                            </h3>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-3 bg-gray-800/50 rounded-lg text-center">
                                    <div className="text-xs text-gray-400 mb-1">Capsule Floor</div>
                                    <div className="text-xl font-mono text-white">
                                        {currentMetrics ? `${currentMetrics.token_price.toFixed(2)} XEX` : '---'}
                                    </div>
                                </div>
                                <div className="p-3 bg-gray-800/50 rounded-lg text-center">
                                    <div className="text-xs text-gray-400 mb-1">Volume (24h)</div>
                                    <div className="text-xl font-mono text-green-400">+15%</div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-glass border border-glass-border rounded-xl p-6 backdrop-blur-md">
                            <h3 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
                                <Network className="w-5 h-5 text-purple-400" />
                                Network State
                            </h3>
                            <div className="space-y-3">
                                <div className="flex justify-between items-center text-sm">
                                    <span className="text-gray-400">Validators</span>
                                    <span className="text-white font-mono">15/15</span>
                                </div>
                                <div className="flex justify-between items-center text-sm">
                                    <span className="text-gray-400">Consensus</span>
                                    <span className="text-green-400 font-mono">SYNCED</span>
                                </div>
                                <div className="flex justify-between items-center text-sm">
                                    <span className="text-gray-400">Ledger Index</span>
                                    <span className="text-blue-400 font-mono">84,291,004</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </DysonLayout>
    );
};

export default EconomyPortal;
