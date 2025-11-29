import React, { useState, useEffect } from 'react';

const GlyphPrompt = ({ onGenerate }) => {
    const [prompt, setPrompt] = useState('');
    const [isDreaming, setIsDreaming] = useState(false);
    const [preview, setPreview] = useState(null);

    // Simulate "Dreaming" effect
    useEffect(() => {
        if (prompt.length > 3) {
            setIsDreaming(true);
            // Mock preview update
            const timer = setTimeout(() => {
                setIsDreaming(false);
                // Simple client-side heuristic for preview
                if (prompt.includes('bracket')) setPreview(['⊸C', '⊽...', '⊻']);
                else setPreview(null);
            }, 500);
            return () => clearTimeout(timer);
        } else {
            setPreview(null);
        }
    }, [prompt]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (onGenerate) onGenerate(prompt);
        setPrompt('');
    };

    return (
        <div className="fixed bottom-10 left-1/2 transform -translate-x-1/2 w-[600px] z-50">
            <form onSubmit={handleSubmit} className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-purple-600 rounded-xl blur opacity-30 animate-pulse"></div>
                <input
                    type="text"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Describe your intent (e.g., 'Make a lightweight bracket')..."
                    className="w-full bg-black/90 border border-cyan-500/50 text-white px-6 py-4 rounded-xl shadow-2xl focus:outline-none focus:border-cyan-400 font-mono text-lg placeholder-gray-600 backdrop-blur-xl"
                    autoFocus
                />

                {/* Dreaming Indicator */}
                {isDreaming && (
                    <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                        <div className="flex gap-1">
                            <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"></span>
                            <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-75"></span>
                            <span className="w-2 h-2 bg-pink-400 rounded-full animate-bounce delay-150"></span>
                        </div>
                    </div>
                )}

                {/* Glyph Preview */}
                {preview && !isDreaming && (
                    <div className="absolute -top-12 left-0 flex gap-2">
                        {preview.map((g, i) => (
                            <div key={i} className="bg-black/80 border border-cyan-500/30 px-2 py-1 rounded text-cyan-300 text-sm font-mono animate-fade-in-up">
                                {g}
                            </div>
                        ))}
                    </div>
                )}
            </form>
        </div>
    );
};

export default GlyphPrompt;
