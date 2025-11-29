import React, { useState } from 'react';

const GLYPHS = [
    { id: 'expose_euv', symbol: '⊼13E', desc: 'Expose 13.5nm EUV', energy: '4.2J' },
    { id: 'cut_01', symbol: '⊽0.1', desc: 'Mill 0.1mm', energy: '50J' },
    { id: 'align_center', symbol: '⊸C', desc: 'Align Center', energy: '0.5J' },
    { id: 'etch_plasma', symbol: '⊿5P', desc: 'Etch 5um Plasma', energy: '120J' },
    { id: 'multi_pattern', symbol: '⋙3', desc: 'Multi-Pattern 3nm', energy: '200J' },
    { id: 'verify', symbol: '⊻', desc: 'Verify Fidelity', energy: '1.0J' },
    { id: 'fix_drift', symbol: '⊿!', desc: 'Auto-Fix Drift', energy: '15J' }
];

const GlyphPalette = ({ onSelectGlyph }) => {
    const [draggedGlyph, setDraggedGlyph] = useState(null);

    const handleDragStart = (e, glyph) => {
        setDraggedGlyph(glyph);
        e.dataTransfer.setData('glyph', JSON.stringify(glyph));
        e.dataTransfer.effectAllowed = 'copy';
    };

    return (
        <div className="glyph-palette p-4 bg-gray-900 text-cyan-400 border-r border-cyan-800 h-full w-64 font-mono">
            <h2 className="text-xl mb-4 border-b border-cyan-700 pb-2">LCODE Glyphs</h2>
            <div className="grid grid-cols-2 gap-4">
                {GLYPHS.map(glyph => (
                    <div
                        key={glyph.id}
                        draggable
                        onDragStart={(e) => handleDragStart(e, glyph)}
                        onClick={() => onSelectGlyph && onSelectGlyph(glyph)}
                        className="glyph-item p-3 border border-cyan-600 rounded hover:bg-cyan-900 cursor-grab active:cursor-grabbing transition-all hover:shadow-[0_0_10px_rgba(34,211,238,0.5)]"
                        title={`${glyph.desc} (Est: ${glyph.energy})`}
                    >
                        <div className="text-3xl text-center mb-1">{glyph.symbol}</div>
                        <div className="text-xs text-center text-cyan-300">{glyph.id}</div>
                    </div>
                ))}
            </div>

            <div className="mt-8 text-xs text-gray-500">
                <p>Drag to Canvas</p>
                <p>v1.0.4 (Secure)</p>
            </div>
        </div>
    );
};

export default GlyphPalette;
