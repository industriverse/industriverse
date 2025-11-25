import React from 'react';
import PlasmaVisualizer from './visualizers/PlasmaVisualizer';
import NetworkGraph from './visualizers/NetworkGraph';

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

const DACRenderer: React.FC<DACRendererProps> = ({ schema }) => {
    if (!schema || !schema.components) return <div className="text-red-500">Invalid DAC Schema</div>;

    return (
        <div className="dac-container p-6 bg-gray-950 text-white rounded-xl shadow-2xl border border-gray-800">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {schema.components.map((comp, index) => {
                    switch (comp.type) {
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
                                    <div className="text-3xl font-mono text-blue-400">{comp.props.metric.toUpperCase()}</div>
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
