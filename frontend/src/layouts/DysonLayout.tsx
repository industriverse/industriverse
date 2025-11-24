import React from 'react';

interface DysonLayoutProps {
    children: React.ReactNode;
}

export function DysonLayout({ children }: DysonLayoutProps) {
    return (
        <div className="min-h-screen bg-background text-foreground font-sans selection:bg-dyson-plasma selection:text-white overflow-hidden relative">
            {/* Ambient Background Mesh (The Dyson Sphere Shell) */}
            <div className="fixed inset-0 z-0 pointer-events-none">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,51,51,0.03)_0%,rgba(5,5,5,0)_70%)] animate-breathe" />
                <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_60%_at_50%_50%,#000_70%,transparent_100%)]" />
            </div>

            {/* Main Content Area (The Void) */}
            <main className="relative z-10 container mx-auto px-4 py-8">
                {children}
            </main>

            {/* Overlay Elements (The HUD) */}
            <div className="fixed top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-dyson-plasma to-transparent opacity-50" />
            <div className="fixed bottom-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-dyson-amber to-transparent opacity-30" />
        </div>
    );
}
