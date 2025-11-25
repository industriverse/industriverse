// @ts-nocheck
import React from 'react';
import { cn } from '@/lib/utils';

interface GlassPanelProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: 'default' | 'hover' | 'critical';
    children: React.ReactNode;
}

export const GlassPanel = React.forwardRef<HTMLDivElement, GlassPanelProps>(
    ({ className, variant = 'default', children, ...props }, ref) => {
        return (
            <div
                ref={ref}
                className={cn(
                    "glass-panel rounded-lg p-6 transition-all duration-300",
                    variant === 'hover' && "glass-panel-hover cursor-pointer",
                    variant === 'critical' && "border-destructive/50 shadow-[0_0_15px_rgba(255,0,153,0.3)]",
                    className
                )}
                {...props}
            >
                {children}
            </div>
        );
    }
);

GlassPanel.displayName = "GlassPanel";
