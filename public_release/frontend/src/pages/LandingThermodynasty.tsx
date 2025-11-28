import React from 'react';
import { Link } from 'wouter';
import { cn } from '@/lib/utils';
import { ArrowRight, Flame, Hexagon, Triangle } from 'lucide-react';

export default function LandingThermodynasty() {
    return (
        <div className="min-h-screen bg-dyson-void text-foreground font-serif relative overflow-hidden selection:bg-dyson-gold selection:text-black">

            {/* Background: The Cathedral of Physics */}
            <div className="absolute inset-0 z-0 pointer-events-none">
                {/* Deep Void Gradient */}
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_30%,#1a1a1a_0%,#000_100%)]" />

                {/* Sacred Geometry Grid */}
                <div className="absolute inset-0 opacity-10 bg-[linear-gradient(60deg,#d4af37_1px,transparent_1px),linear-gradient(-60deg,#d4af37_1px,transparent_1px)] bg-[size:100px_173.2px]" />

                {/* Ambient Glow */}
                <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-dyson-gold/5 blur-[100px] rounded-full" />
            </div>

            <main className="relative z-10 container mx-auto px-4 min-h-screen flex flex-col items-center justify-center text-center">

                {/* Brand Mark: The Alchemical Symbol */}
                <div className="mb-12 relative">
                    <div className="absolute inset-0 bg-dyson-gold/20 blur-2xl rounded-full animate-pulse" />
                    <div className="relative w-32 h-32 border border-dyson-gold/30 rotate-45 flex items-center justify-center backdrop-blur-sm">
                        <div className="w-24 h-24 border border-dyson-gold/50 rotate-45 flex items-center justify-center">
                            <Flame className="w-12 h-12 text-dyson-gold -rotate-90" />
                        </div>
                    </div>
                </div>

                {/* Hero Title */}
                <h1 className="text-6xl md:text-9xl font-bold tracking-widest mb-4 text-dyson-gold uppercase drop-shadow-2xl font-serif">
                    Thermo<br className="md:hidden" />dynasty
                </h1>

                {/* The Great Work Subtitle */}
                <div className="flex items-center gap-4 mb-12 opacity-80">
                    <div className="h-[1px] w-12 bg-dyson-gold/50" />
                    <span className="text-dyson-gold/80 uppercase tracking-[0.3em] text-sm md:text-base font-sans">
                        Forging the Future in the Fires of Physics
                    </span>
                    <div className="h-[1px] w-12 bg-dyson-gold/50" />
                </div>

                {/* Manifesto Text */}
                <div className="max-w-2xl mx-auto mb-16 space-y-6 text-gray-400 font-sans font-light leading-relaxed text-lg">
                    <p>
                        We are the architects of the <strong className="text-dyson-gold font-normal">Grand Unification</strong>.
                        Where the ancient laws of thermodynamics meet the infinite potential of artificial intelligence.
                    </p>
                    <p>
                        We do not build software. We build <strong className="text-white font-normal">Digital Matter</strong>.
                        Immutable. Verifiable. Eternal.
                    </p>
                </div>

                {/* Call to Action */}
                <a href="https://portal.industriverse.ai" className="group relative inline-flex items-center gap-3 px-12 py-4 bg-transparent border border-dyson-gold/30 hover:border-dyson-gold text-dyson-gold uppercase tracking-widest text-sm font-sans transition-all duration-500 hover:bg-dyson-gold/5">
                    <span className="relative z-10">Access The Network</span>
                    <ArrowRight className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" />

                    {/* Corner Accents */}
                    <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-dyson-gold opacity-50 group-hover:opacity-100 transition-opacity" />
                    <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-dyson-gold opacity-50 group-hover:opacity-100 transition-opacity" />
                    <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-dyson-gold opacity-50 group-hover:opacity-100 transition-opacity" />
                    <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-dyson-gold opacity-50 group-hover:opacity-100 transition-opacity" />
                </a>

                {/* Footer / Copyright */}
                <div className="absolute bottom-8 text-dyson-gold/20 text-xs uppercase tracking-widest font-sans">
                    Est. 2025 • The Great Work
                </div>

            </main>
        </div>
    );
}

