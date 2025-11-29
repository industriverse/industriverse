import React, { useState, useEffect } from 'react';

const MaestroCursor = ({ activeGlyph, machineState }) => {
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [isHovering, setIsHovering] = useState(false);

    useEffect(() => {
        const updatePosition = (e) => {
            setPosition({ x: e.clientX, y: e.clientY });
        };

        window.addEventListener('mousemove', updatePosition);
        return () => window.removeEventListener('mousemove', updatePosition);
    }, []);

    if (!activeGlyph) return null;

    return (
        <div
            className="fixed pointer-events-none z-50 flex items-center"
            style={{
                left: position.x + 15,
                top: position.y + 15,
                transform: 'translate(0, 0)'
            }}
        >
            {/* Holographic Orb */}
            <div className="relative">
                <div className="absolute inset-0 bg-cyan-500 rounded-full blur-md opacity-50 animate-pulse"></div>
                <div className="relative bg-black border border-cyan-400 rounded-lg p-2 shadow-[0_0_15px_rgba(34,211,238,0.6)]">
                    <div className="flex items-center gap-2">
                        <span className="text-2xl font-bold text-white">{activeGlyph.symbol}</span>
                        <div className="flex flex-col">
                            <span className="text-[10px] text-cyan-200 uppercase tracking-wider">
                                {activeGlyph.desc}
                            </span>
                            {machineState && (
                                <span className={`text-[9px] ${machineState.safe ? 'text-green-400' : 'text-red-400'}`}>
                                    {machineState.safe ? '✓ SAFE' : '⚠ WARNING'}
                                </span>
                            )}
                        </div>
                    </div>

                    {/* Energy Projection */}
                    <div className="mt-1 h-1 bg-gray-800 rounded overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-cyan-500 to-purple-500"
                            style={{ width: '75%' }} // Mock energy level
                        ></div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MaestroCursor;
