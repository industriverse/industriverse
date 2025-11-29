import React, { useState, useEffect } from 'react';
import demoRegistry from '../demos/demo_registry.json';
import packARunner from '../demos/pack_a_runner.js';
import packBRunner from '../demos/pack_b_runner.js';
import packCRunner from '../demos/pack_c_runner.js';
import packDRunner from '../demos/pack_d_runner.js';
import packERunner from '../demos/pack_e_runner.js';

const DemoDashboard = () => {
    const [activePack, setActivePack] = useState(demoRegistry.packs[0]);
    const [activeDemo, setActiveDemo] = useState(demoRegistry.packs[0].demos[0]);
    const [demoOutput, setDemoOutput] = useState(null);
    const [isRunning, setIsRunning] = useState(false);

    // Mock execution of a demo
    const runDemo = async (demo) => {
        setIsRunning(true);
        setDemoOutput(`Initializing ${demo.title}...\n`);

        const logCallback = (msg) => {
            setDemoOutput(prev => prev + "\n" + msg);
        };

        try {
            let runner;
            if (activePack.id === 'pack_a') runner = packARunner;
            else if (activePack.id === 'pack_b') runner = packBRunner;
            else if (activePack.id === 'pack_c') runner = packCRunner;
            else if (activePack.id === 'pack_d') runner = packDRunner;
            else if (activePack.id === 'pack_e') runner = packERunner;

            if (runner) {
                await runner.run(demo.id, demo.config, logCallback);
            } else {
                logCallback("Error: No runner found for this pack.");
            }
        } catch (e) {
            logCallback(`Error: ${e.message}`);
        }

        setIsRunning(false);
    };

    return (
        <div className="flex h-screen bg-gray-900 text-white font-mono">
            {/* Sidebar: Packs */}
            <div className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
                <div className="p-4 border-b border-gray-700">
                    <h1 className="text-xl font-bold text-blue-400">Industriverse</h1>
                    <p className="text-xs text-gray-400">Investor Demo Suite</p>
                </div>
                <div className="flex-1 overflow-y-auto">
                    {demoRegistry.packs.map(pack => (
                        <div key={pack.id} className="mb-4">
                            <div
                                className={`px-4 py-2 cursor-pointer font-bold ${activePack.id === pack.id ? 'text-blue-300' : 'text-gray-500'}`}
                                onClick={() => setActivePack(pack)}
                            >
                                {pack.title}
                            </div>
                            {activePack.id === pack.id && (
                                <div className="pl-4">
                                    {pack.demos.map(demo => (
                                        <div
                                            key={demo.id}
                                            className={`px-4 py-1 text-sm cursor-pointer hover:bg-gray-700 ${activeDemo.id === demo.id ? 'bg-gray-700 text-white' : 'text-gray-400'}`}
                                            onClick={() => { setActiveDemo(demo); setDemoOutput(null); }}
                                        >
                                            {demo.id.toUpperCase()}: {demo.title}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Main Content: Active Demo */}
            <div className="flex-1 flex flex-col">
                {/* Header */}
                <div className="p-6 border-b border-gray-700 bg-gray-800">
                    <h2 className="text-2xl font-bold">{activeDemo.title}</h2>
                    <p className="text-gray-400">{activePack.description} - {activeDemo.type}</p>
                </div>

                {/* Visualization Area (Mock) */}
                <div className="flex-1 p-6 bg-black relative overflow-hidden">
                    <div className="absolute inset-0 flex items-center justify-center opacity-20 pointer-events-none">
                        {/* Background Grid or Logo */}
                        <div className="text-9xl font-bold text-gray-800">DEMO</div>
                    </div>

                    <div className="relative z-10">
                        <div className="mb-4">
                            <button
                                onClick={() => runDemo(activeDemo)}
                                disabled={isRunning}
                                className={`px-6 py-2 rounded font-bold ${isRunning ? 'bg-gray-600' : 'bg-blue-600 hover:bg-blue-500'}`}
                            >
                                {isRunning ? 'Running...' : '▶ Run Demo'}
                            </button>
                        </div>

                        {/* Output Console */}
                        <div className="bg-gray-900 border border-gray-700 p-4 rounded h-96 font-mono text-green-400 overflow-y-auto">
                            <p className="text-gray-500">$ systemctl start demo_{activeDemo.id}</p>
                            {demoOutput && (
                                <>
                                    <p className="mt-2">{demoOutput}</p>
                                    <p className="mt-2 text-blue-400">
                                        {JSON.stringify(activeDemo.config, null, 2)}
                                    </p>
                                </>
                            )}
                            {isRunning && <p className="mt-2 animate-pulse">Processing...</p>}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DemoDashboard;
