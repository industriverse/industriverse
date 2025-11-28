import React from 'react';
import { Link } from 'wouter';
import { DysonLayout } from '../layouts/DysonLayout';
import { TruthSigil } from '../components/ui/TruthSigil';
import { cn } from '@/lib/utils';
import { ArrowRight, Cpu, Shield, Zap, Globe } from 'lucide-react';

export default function LandingIndustriverse() {
    return (
        <DysonLayout>
            <div className="relative z-10 flex flex-col items-center justify-center min-h-[80vh] text-center">

                {/* The Sigil of the Core */}
                <div className="mb-8 relative group cursor-pointer">
                    <div className="absolute -inset-4 bg-dyson-plasma/20 rounded-full blur-xl animate-pulse group-hover:bg-dyson-plasma/40 transition-all duration-500"></div>
                    <div className="relative w-24 h-24 border-2 border-dyson-amber rounded-full flex items-center justify-center bg-black/50 backdrop-blur-sm group-hover:border-dyson-plasma transition-colors duration-300">
                        <Zap className="w-10 h-10 text-dyson-gold animate-pulse" />
                    </div>
                </div>

                {/* Hero Title */}
                <h1 className="text-5xl md:text-8xl font-bold tracking-tighter mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white via-gray-200 to-gray-600 drop-shadow-[0_0_15px_rgba(255,255,255,0.1)]">
                    INDUSTRI<span className="text-dyson-plasma">VERSE</span>
                </h1>

                {/* Subtitle / Manifesto */}
                <p className="text-xl md:text-2xl text-gray-400 mb-12 max-w-2xl font-light leading-relaxed">
                    The Control Interface for the <span className="text-dyson-amber">Thermodynamic Dyson Sphere</span>.
                    <br />
                    <span className="text-sm uppercase tracking-widest opacity-70 mt-2 block">
                        Where Code is Law & Data is Energy
                    </span>
                </p>

                {/* The Portals (Action Buttons) */}
                <div className="flex flex-col md:flex-row gap-6 w-full max-w-4xl justify-center items-stretch">

                    {/* Portal: Dashboard */}
                    <Link href="/dashboard">
                        <div className="group relative px-8 py-6 bg-black/40 border border-dyson-plasma/30 hover:border-dyson-plasma rounded-lg transition-all duration-300 hover:bg-dyson-plasma/10 cursor-pointer flex-1 flex flex-col items-center gap-3 backdrop-blur-md">
                            <div className="absolute inset-0 bg-gradient-to-b from-dyson-plasma/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-lg" />
                            <Cpu className="w-8 h-8 text-dyson-plasma mb-2 group-hover:scale-110 transition-transform duration-300" />
                            <h3 className="text-xl font-bold text-white tracking-wide">ENTER PORTAL</h3>
                            <p className="text-xs text-gray-500 uppercase tracking-widest">Operator Access</p>
                            <ArrowRight className="w-4 h-4 text-dyson-plasma opacity-0 group-hover:opacity-100 transform translate-x-[-10px] group-hover:translate-x-0 transition-all duration-300 absolute bottom-4 right-4" />
                        </div>
                    </Link>

                    {/* Portal: Thermodynasty */}
                    <Link href="/thermodynasty">
                        <div className="group relative px-8 py-6 bg-black/40 border border-dyson-amber/30 hover:border-dyson-amber rounded-lg transition-all duration-300 hover:bg-dyson-amber/10 cursor-pointer flex-1 flex flex-col items-center gap-3 backdrop-blur-md">
                            <div className="absolute inset-0 bg-gradient-to-b from-dyson-amber/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-lg" />
                            <Globe className="w-8 h-8 text-dyson-amber mb-2 group-hover:scale-110 transition-transform duration-300" />
                            <h3 className="text-xl font-bold text-white tracking-wide">THERMODYNASTY</h3>
                            <p className="text-xs text-gray-500 uppercase tracking-widest">Brand Identity</p>
                            <ArrowRight className="w-4 h-4 text-dyson-amber opacity-0 group-hover:opacity-100 transform translate-x-[-10px] group-hover:translate-x-0 transition-all duration-300 absolute bottom-4 right-4" />
                        </div>
                    </Link>

                </div>

                {/* Live Truth Stream (Decorative) */}
                <div className="mt-24 w-full max-w-md opacity-80 hover:opacity-100 transition-opacity duration-500">
                    <div className="text-xs text-center text-dyson-gold/50 uppercase tracking-[0.2em] mb-4">
                        Live Proof Stream
                    </div>
                    <TruthSigil />
                </div>

            </div>

            {/* Footer / Status */}
            <footer className="absolute bottom-4 w-full text-center">
                <div className="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-white/5 border border-white/10 backdrop-blur-md">
                    <div className="w-1.5 h-1.5 rounded-full bg-dyson-teal animate-pulse" />
                    <span className="text-[10px] text-gray-500 font-mono uppercase tracking-widest">
                        System Nominal • v5.0.0
                    </span>
                </div>
            </footer>
        </DysonLayout>
    );
}

