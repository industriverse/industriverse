import React, { ReactNode } from 'react';
import SphereBackground from '../components/SphereBackground';
import { Link } from 'wouter'; // Assuming wouter is used based on package.json
import { Activity, Cpu, Globe, Zap, Database, Hexagon } from 'lucide-react';

interface DysonLayoutProps {
    children: ReactNode;
}

const NavItem = ({ to, icon: Icon, label }: { to: string; icon: any; label: string }) => (
    <Link href={to} className="group flex items-center gap-3 p-3 rounded-lg hover:bg-glass transition-all duration-300 cursor-pointer">
        <Icon className="w-5 h-5 text-plasma group-hover:text-solar transition-colors" />
        <span className="text-sm font-medium text-gray-400 group-hover:text-white transition-colors font-mono tracking-wide">
            {label}
        </span>
    </Link>
);

const DysonLayout: React.FC<DysonLayoutProps> = ({ children }) => {
    return (
        <div className="min-h-screen text-white font-sans selection:bg-plasma selection:text-black overflow-hidden relative">
            <SphereBackground />

            {/* Holographic Header */}
            <header className="fixed top-0 left-0 right-0 h-16 border-b border-glass-border bg-void/50 backdrop-blur-md z-50 flex items-center px-6 justify-between">
                <div className="flex items-center gap-2">
                    <Hexagon className="w-8 h-8 text-solar animate-pulse" />
                    <h1 className="text-xl font-bold tracking-widest uppercase bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                        Industriverse
                    </h1>
                </div>
                <div className="flex items-center gap-4">
                    <div className="px-3 py-1 rounded-full border border-plasma/30 bg-plasma/10 text-plasma text-xs font-mono">
                        SYSTEM: ONLINE
                    </div>
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-ping" />
                </div>
            </header>

            {/* Obsidian Glass Sidebar */}
            <aside className="fixed left-0 top-16 bottom-0 w-64 border-r border-glass-border bg-void/30 backdrop-blur-xl z-40 p-4 flex flex-col gap-2">
                <div className="mb-4 px-3 text-xs font-mono text-gray-500 uppercase tracking-wider">
                    Portals
                </div>
                <NavItem to="/physics" icon={Zap} label="PHYSICS" />
                <NavItem to="/bio" icon={Activity} label="BIO / CHEM" />
                <NavItem to="/space" icon={Globe} label="SPACE" />
                <NavItem to="/hardware" icon={Cpu} label="HARDWARE" />
                <NavItem to="/economy" icon={Database} label="ECONOMY" />
            </aside>

            {/* Main Content Area (The Portal View) */}
            <main className="pl-64 pt-16 min-h-screen relative z-10">
                <div className="p-8 max-w-7xl mx-auto animate-in fade-in duration-700 slide-in-from-bottom-4">
                    {children}
                </div>
            </main>
        </div>
    );
};

export default DysonLayout;
