/**
 * CapsulePill Component
 * 
 * Displays a capsule in one of three states:
 * - pill: Collapsed, minimal information
 * - expanded: Medium detail with actions
 * - full: Complete detail view
 */

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  AlertCircle,
  AlertTriangle,
  CheckCircle,
  ChevronDown,
  ChevronUp,
  Clock,
  Maximize2,
  Minimize2,
  Shield,
  X,
  Zap
} from 'lucide-react';
import type { CapsuleData, CapsuleViewState, CapsuleStatus, CapsuleAction } from '@/types/capsule';

interface CapsulePillProps {
  capsule: CapsuleData;
  initialState?: CapsuleViewState;
  onAction?: (action: CapsuleAction, capsuleId: string) => void;
  onStateChange?: (state: CapsuleViewState) => void;
}

const statusConfig: Record<CapsuleStatus, {
  icon: typeof AlertCircle;
  color: string;
  bgColor: string;
  borderColor: string;
}> = {
  active: {
    icon: Zap,
    color: 'text-cyan-400',
    bgColor: 'bg-slate-800/80',
    borderColor: 'border-cyan-500/40'
  },
  warning: {
    icon: AlertTriangle,
    color: 'text-amber-400',
    bgColor: 'bg-slate-800/80',
    borderColor: 'border-amber-500/40'
  },
  critical: {
    icon: AlertCircle,
    color: 'text-rose-400',
    bgColor: 'bg-slate-800/80',
    borderColor: 'border-rose-500/40'
  },
  resolved: {
    icon: CheckCircle,
    color: 'text-emerald-400',
    bgColor: 'bg-slate-800/80',
    borderColor: 'border-emerald-500/40'
  },
  dismissed: {
    icon: X,
    color: 'text-slate-400',
    bgColor: 'bg-slate-800/50',
    borderColor: 'border-slate-600/40'
  }
};

const actionConfig: Record<CapsuleAction, {
  label: string;
  icon: typeof Shield;
  variant: 'default' | 'destructive' | 'outline' | 'secondary';
}> = {
  mitigate: {
    label: 'Mitigate',
    icon: Shield,
    variant: 'default'
  },
  inspect: {
    label: 'Inspect',
    icon: Maximize2,
    variant: 'outline'
  },
  dismiss: {
    label: 'Dismiss',
    icon: X,
    variant: 'outline'
  },
  escalate: {
    label: 'Escalate',
    icon: AlertCircle,
    variant: 'destructive'
  },
  acknowledge: {
    label: 'Acknowledge',
    icon: CheckCircle,
    variant: 'secondary'
  }
};

export default function CapsulePill({
  capsule,
  initialState = 'pill',
  onAction,
  onStateChange
}: CapsulePillProps) {
  const [viewState, setViewState] = useState<CapsuleViewState>(initialState);
  
  const config = statusConfig[capsule.status];
  const StatusIcon = config.icon;
  
  const handleStateChange = (newState: CapsuleViewState) => {
    setViewState(newState);
    onStateChange?.(newState);
  };
  
  const handleAction = (action: CapsuleAction) => {
    onAction?.(action, capsule.id);
  };
  
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };
  
  // Pill State (Collapsed)
  if (viewState === 'pill') {
    return (
      <Card
        className={`
          ${config.bgColor} ${config.borderColor}
          border-2 p-3 cursor-pointer
          transition-all duration-200 hover:scale-[1.02] hover:shadow-lg
          animate-in slide-in-from-bottom-2
        `}
        onClick={() => handleStateChange('expanded')}
      >
        <div className="flex items-center gap-3">
          <StatusIcon className={`${config.color} h-5 w-5 flex-shrink-0`} />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-foreground truncate">
              {capsule.title}
            </p>
            <p className="text-xs text-muted-foreground truncate">
              {capsule.source}
            </p>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <Badge variant="outline" className="text-xs">
              P{capsule.priority}
            </Badge>
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          </div>
        </div>
      </Card>
    );
  }
  
  // Expanded State (Medium Detail)
  if (viewState === 'expanded') {
    return (
      <Card
        className={`
          ${config.bgColor} ${config.borderColor}
          border-2 p-4
          transition-all duration-200
          animate-in slide-in-from-top-2
        `}
      >
        <div className="space-y-3">
          {/* Header */}
          <div className="flex items-start gap-3">
            <StatusIcon className={`${config.color} h-6 w-6 flex-shrink-0 mt-0.5`} />
            <div className="flex-1 min-w-0">
              <h3 className="text-base font-semibold text-foreground">
                {capsule.title}
              </h3>
              <p className="text-sm text-muted-foreground mt-1">
                {capsule.description}
              </p>
            </div>
            <div className="flex gap-1 flex-shrink-0">
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={() => handleStateChange('full')}
              >
                <Maximize2 className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={() => handleStateChange('pill')}
              >
                <ChevronUp className="h-4 w-4" />
              </Button>
            </div>
          </div>
          
          {/* Metadata */}
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <div className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              <span>{formatTimestamp(capsule.timestamp)}</span>
            </div>
            <Badge variant="outline" className="text-xs">
              Priority {capsule.priority}
            </Badge>
            <Badge variant="secondary" className="text-xs">
              {capsule.source}
            </Badge>
          </div>
          
          {/* Actions */}
          <div className="flex flex-wrap gap-2 pt-2">
            {capsule.actions.map((action) => {
              const actionCfg = actionConfig[action];
              const ActionIcon = actionCfg.icon;
              return (
                <Button
                  key={action}
                  variant={actionCfg.variant}
                  size="sm"
                  onClick={() => handleAction(action)}
                  className="gap-1.5"
                >
                  <ActionIcon className="h-3.5 w-3.5" />
                  {actionCfg.label}
                </Button>
              );
            })}
          </div>
        </div>
      </Card>
    );
  }
  
  // Full State (Complete Detail)
  return (
    <Card
      className={`
        ${config.bgColor} ${config.borderColor}
        border-2 p-6
        transition-all duration-200
        animate-in slide-in-from-top-4
      `}
    >
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-start gap-4">
          <div className={`${config.bgColor} p-3 rounded-lg border ${config.borderColor}`}>
            <StatusIcon className={`${config.color} h-8 w-8`} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="outline">
                Priority {capsule.priority}
              </Badge>
              <Badge className={config.color}>
                {capsule.status.toUpperCase()}
              </Badge>
            </div>
            <h2 className="text-xl font-bold text-foreground">
              {capsule.title}
            </h2>
            <p className="text-sm text-muted-foreground mt-2">
              {capsule.description}
            </p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => handleStateChange('expanded')}
          >
            <Minimize2 className="h-5 w-5" />
          </Button>
        </div>
        
        {/* Metadata Grid */}
        <div className="grid grid-cols-2 gap-4 p-4 bg-background/50 rounded-lg border border-border">
          <div>
            <p className="text-xs text-muted-foreground mb-1">Source</p>
            <p className="text-sm font-medium text-foreground">{capsule.source}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-1">Timestamp</p>
            <p className="text-sm font-medium text-foreground">
              {new Date(capsule.timestamp).toLocaleString()}
            </p>
          </div>
          {capsule.utid && (
            <div>
              <p className="text-xs text-muted-foreground mb-1">UTID</p>
              <p className="text-sm font-mono text-foreground truncate">{capsule.utid}</p>
            </div>
          )}
          {capsule.proofId && (
            <div>
              <p className="text-xs text-muted-foreground mb-1">Proof ID</p>
              <p className="text-sm font-mono text-foreground truncate">{capsule.proofId}</p>
            </div>
          )}
          {capsule.energyConsumed !== undefined && (
            <div>
              <p className="text-xs text-muted-foreground mb-1">Energy Consumed</p>
              <p className="text-sm font-medium text-foreground">{capsule.energyConsumed.toFixed(2)} J</p>
            </div>
          )}
          {capsule.carbonFootprint !== undefined && (
            <div>
              <p className="text-xs text-muted-foreground mb-1">Carbon Footprint</p>
              <p className="text-sm font-medium text-foreground">{capsule.carbonFootprint.toFixed(4)} kg CO₂</p>
            </div>
          )}
        </div>
        
        {/* Additional Metadata */}
        {Object.keys(capsule.metadata).length > 0 && (
          <div className="p-4 bg-background/50 rounded-lg border border-border">
            <h4 className="text-sm font-semibold text-foreground mb-2">Additional Information</h4>
            <div className="space-y-1">
              {Object.entries(capsule.metadata).map(([key, value]) => (
                <div key={key} className="flex justify-between text-sm">
                  <span className="text-muted-foreground">{key}:</span>
                  <span className="text-foreground font-medium">{String(value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Actions */}
        <div className="flex flex-wrap gap-2 pt-2">
          {capsule.actions.map((action) => {
            const actionCfg = actionConfig[action];
            const ActionIcon = actionCfg.icon;
            return (
              <Button
                key={action}
                variant={actionCfg.variant}
                onClick={() => handleAction(action)}
                className="gap-2"
              >
                <ActionIcon className="h-4 w-4" />
                {actionCfg.label}
              </Button>
            );
          })}
        </div>
      </div>
    </Card>
  );
}
