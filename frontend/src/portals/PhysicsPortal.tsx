import React from 'react';
import DysonLayout from '../layout/DysonLayout';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const mockFusionData = Array.from({ length: 20 }, (_, i) => ({
    time: i,
    stability: 0.5 + Math.random() * 0.4,
    energy: 10 - Math.random() * 2,
}));

const PhysicsPortal: React.FC = () => {
    const [data, setData] = React.useState<any[]>([]);
    const [currentMetrics, setCurrentMetrics] = React.useState<any>(null);

    React.useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/capsules/fusion_v1');
                const json = await res.json();

                setCurrentMetrics(json.data);

                setData(prev => {
                    const newData = [
                        ...prev,
                        {
                            time: new Date().toLocaleTimeString(),
                            stability: json.data.stability_index,
                            energy: json.data.energy_output_mw / 100 // Normalize for chart
                        }
                    ];
                    return newData.slice(-20); // Keep last 20 points
                });
            } catch (e) {
                console.error("Failed to fetch physics data", e);
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
                        <h2 className="text-3xl font-light text-white mb-1">Physics Portal</h2>
                        <p className="text-gray-400 font-mono text-sm">SECTOR: HIGH ENERGY PHYSICS</p>
                    </div>
                    <div className="text-right">
                        <div className="text-2xl font-mono text-plasma">
                            {currentMetrics ? `${(currentMetrics.stability_index * 100).toFixed(1)}%` : '---'}
                        </div>
                        <div className="text-xs text-gray-500 uppercase">System Stability</div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Fusion Reactor Status */}
                    <div className="bg-glass border border-glass-border rounded-xl p-6 backdrop-blur-md">
                        <h3 className="text-lg font-medium text-solar mb-4 flex items-center gap-2">
                            <span className="w-2 h-2 bg-solar rounded-full animate-pulse" />
                            Fusion Plasma Stability
                        </h3>
                        <div className="h-64 w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={data}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                    <XAxis dataKey="time" stroke="#666" tick={{ fill: '#666', fontSize: 10 }} interval={4} />
                                    <YAxis stroke="#666" tick={{ fill: '#666', fontSize: 12 }} domain={[0, 10]} />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#050505', borderColor: '#333', color: '#fff' }}
                                        itemStyle={{ color: '#00F0FF' }}
                                    />
                                    <Line type="monotone" dataKey="stability" stroke="#00F0FF" strokeWidth={2} dot={false} />
                                    <Line type="monotone" dataKey="energy" stroke="#FF0055" strokeWidth={2} dot={false} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Grid Load Map (Placeholder) */}
                    <div className="bg-glass border border-glass-border rounded-xl p-6 backdrop-blur-md">
                        <h3 className="text-lg font-medium text-nebula mb-4">Grid Load Distribution</h3>
                        <div className="h-64 w-full flex flex-col items-center justify-center border border-dashed border-gray-700 rounded-lg gap-4">
                            <div className="text-4xl font-mono text-white">
                                {currentMetrics ? `${currentMetrics.energy_output_mw.toFixed(0)} MW` : '---'}
                            </div>
                            <span className="text-gray-500 font-mono text-sm">CURRENT OUTPUT</span>
                        </div>
                    </div>
                </div>
            </div>
        </DysonLayout>
    );
};

export default PhysicsPortal;
