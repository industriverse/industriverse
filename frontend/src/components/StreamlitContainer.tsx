import React, { useState } from 'react';
import { ExternalLink, RefreshCw } from 'lucide-react';

interface StreamlitContainerProps {
    url: string;
    title?: string;
    height?: string;
}

export const StreamlitContainer: React.FC<StreamlitContainerProps> = ({
    url,
    title = "Pilot App",
    height = "600px"
}) => {
    const [key, setKey] = useState(0); // Used to force reload iframe

    const reload = () => setKey(prev => prev + 1);

    return (
        <div className="w-full border border-slate-800 rounded-xl overflow-hidden bg-slate-950 flex flex-col">
            {/* Header Bar */}
            <div className="flex items-center justify-between px-4 py-2 bg-slate-900 border-b border-slate-800">
                <div className="flex items-center gap-2">
                    <span className="text-red-500 font-bold text-lg">🎈</span>
                    <span className="text-sm font-medium text-slate-300">{title}</span>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={reload}
                        className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded transition-colors"
                        title="Reload App"
                    >
                        <RefreshCw size={14} />
                    </button>
                    <a
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded transition-colors"
                        title="Open in New Tab"
                    >
                        <ExternalLink size={14} />
                    </a>
                </div>
            </div>

            {/* Iframe */}
            <div className="relative w-full bg-black" style={{ height }}>
                <iframe
                    key={key}
                    src={url}
                    className="w-full h-full border-0"
                    title={title}
                    allow="accelerometer; camera; encrypted-media; geolocation; gyroscope; microphone; midi; clipboard-read; clipboard-write"
                    sandbox="allow-forms allow-scripts allow-same-origin allow-popups allow-downloads"
                />

                {/* Loading Overlay (Optional - simple implementation) */}
                <div className="absolute inset-0 pointer-events-none flex items-center justify-center bg-black/50 opacity-0 transition-opacity duration-500">
                    <span className="text-cyan-500 animate-pulse">Loading Streamlit...</span>
                </div>
            </div>
        </div>
    );
};
