import React, { Suspense } from 'react';
import PlasmaVisualizer from './visualizers/PlasmaVisualizer';
import NetworkGraph from './visualizers/NetworkGraph';
import { Heatmap3D } from './visualizers/IndustrialWidgets/Heatmap3D';
import { GeoMap } from './visualizers/IndustrialWidgets/GeoMap';
import { MoleculeViewer } from './visualizers/IndustrialWidgets/MoleculeViewer';
import { StreamlitContainer } from './StreamlitContainer';
import { Skeleton } from '@/components/ui/skeleton';

interface ComponentSchema {
    type: string;
    props: Record<string, any>;
}

interface DACSchema {
    layout: string;
    theme: string;
    components: ComponentSchema[];
}

interface DACRendererProps {
    schema: DACSchema;
}

const componentMap: Record<string, React.ComponentType<any>> = {
    'plasma_visualizer': PlasmaVisualizer,
    'network_graph': NetworkGraph,
    'Heatmap3D': Heatmap3D,
    'GeoMap': GeoMap,
    'MoleculeViewer': MoleculeViewer,
    'StreamlitView': StreamlitContainer,
    // Add more mappings here
};

const DACRenderer: React.FC<DACRendererProps> = ({ schema }) => {
    if (!schema || !schema.components) return <div className="text-red-500">Invalid DAC Schema</div>;

    return (
        <div className="dac-container p-6 bg-gray-950 text-white rounded-xl shadow-2xl border border-gray-800">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {schema.components.map((comp, index) => {
                    switch (comp.type) {
                        case 'Slider':
                            return (
                                <div key={index} className="p-4 bg-gray-900 rounded border border-gray-700">
                                    <label className="text-xs text-gray-400 uppercase mb-2 block">{comp.props.label}</label>
                                    <input
                                        type="range"
                                        min={comp.props.min}
                                        max={comp.props.max}
                                        step={comp.props.step}
                                        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                                    />
                                </div>
                            );

                        case 'Button':
                            return (
                                <div key={index} className="p-4 bg-gray-900 rounded border border-gray-700 flex items-center justify-center">
                                    <button className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded shadow-lg transition-all transform hover:scale-105">
                                        {comp.props.label}
                                    </button>
                                </div>
                            );

                        case 'ProofWidget':
                            return (
                                <div key={index} className="p-4 bg-gray-900 rounded border border-gray-700">
                                    <h3 className="text-xs text-gray-400 uppercase mb-2">Sovereign Proof</h3>
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
                                        <span className="font-mono text-xs text-green-400">Verified</span>
                                    </div>
                                    <div className="mt-2 text-xs text-gray-500 font-mono truncate">
                                        0x{Math.random().toString(16).slice(2)}...
                                    </div>
                                </div>
                            );

                        case 'Header':
                            return (
                                <div key={index} className="col-span-full border-b border-gray-800 pb-4 mb-4">
                                    <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
                                        {comp.props.title}
                                    </h1>
                                </div>
                            );

                        case 'ReactorGauge':
                            return (
                                <div key={index} className="p-4 bg-gray-900 rounded border border-gray-700">
                                    <h3 className="text-xs text-gray-400 uppercase mb-2">Reactor Metric</h3>
                                    <div className="text-3xl font-mono text-blue-400">{comp.props.metric ? comp.props.metric.toUpperCase() : "ENERGY"}</div>
                                    <div className="w-full bg-gray-800 h-2 mt-2 rounded-full overflow-hidden">
                                        <div className="bg-blue-500 h-full w-3/4 animate-pulse"></div>
                                    </div>
                                </div>
                            );

                        case 'TruthSigil':
                            return (
                                <div key={index} className="p-4 bg-gray-900 rounded border border-gray-700 flex items-center justify-between">
                                    <div>
                                        <h3 className="text-xs text-gray-400 uppercase">Proof Type</h3>
                                        <div className="font-mono text-yellow-500">{comp.props.proof_type}</div>
                                    </div>
                                    <div className="w-12 h-12 rounded-full border-2 border-yellow-500/50 flex items-center justify-center">
                                        <span className="text-2xl">⚡</span>
                                    </div>
                                </div>
                            );

                        case 'PlasmaVisualizer':
                            return (
                                <div key={index} className="col-span-full md:col-span-1">
                                    <PlasmaVisualizer {...comp.props} />
                                </div>
                            );

                        case 'NetworkGraph':
                            return (
                                <div key={index} className="col-span-full md:col-span-1">
                                    <NetworkGraph {...comp.props} />
                                </div>
                            );

                        case 'CoilControls':
                            return (
                                <div key={index} className="p-4 bg-gray-900 rounded border border-gray-700">
                                    <h3 className="text-xs text-gray-400 uppercase mb-2">Magnetic Coils</h3>
                                    <div className="grid grid-cols-5 gap-2">
                                        {Array.from({ length: comp.props.count || 5 }).map((_, i) => (
                                            <div key={i} className="h-8 bg-purple-900/50 rounded border border-purple-500/30 flex items-center justify-center text-xs">
                                                C{i + 1}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            );

                        case 'FrequencyMonitor':
                            return (
                                <div key={index} className="p-4 bg-gray-900 rounded border border-gray-700">
                                    <h3 className="text-xs text-gray-400 uppercase mb-2">Grid Frequency</h3>
                                    <div className="text-4xl font-mono text-green-400">{comp.props.nominal} Hz</div>
                                </div>
                            );

                        default:
                            return (
                                <div key={index} className="p-4 bg-gray-800/50 rounded border border-gray-700 border-dashed text-gray-500 text-sm">
                                    Unknown Component: {comp.type}
                                </div>
                            );
                    }
                })}
            </div>
        </div>
    );
};

export default DACRenderer;
