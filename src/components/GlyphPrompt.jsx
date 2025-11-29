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
                if (prompt.includes('bracket')) {
                    let price = '$15.20';
                    let energy = '120.5J';
                    if (prompt.includes('lightweight')) {
                        price = '$45.50'; // Higher price for precision
                        energy = '450.2J';
                    }
                    setPreview({
                        glyphs: prompt.includes('lightweight') ? ['⊸C', '⊽0.1', '⊻'] : ['⊸C', '⊽0.5', '⊻'],
                        price: price,
                        energy: energy
                    });
                }
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
                    <div className="absolute -top-16 left-0 w-full">
                        <div className="flex justify-between items-end mb-2">
                            <div className="flex gap-2">
                                {preview.glyphs.map((g, i) => (
                                    <div key={i} className="bg-black/80 border border-cyan-500/30 px-2 py-1 rounded text-cyan-300 text-sm font-mono animate-fade-in-up">
                                        {g}
                                    </div>
                                ))}
                            </div>
                            <div className="text-right">
                                <div className="text-xs text-gray-400">EST. EXERGY PRICE</div>
                                <div className="text-xl font-bold text-green-400">{preview.price}</div>
                                <div className="text-[10px] text-gray-500">{preview.energy}</div>
                            </div>
                        </div>
                    </div>
                )}
            </form>
        </div>
    );
};

export default GlyphPrompt;
