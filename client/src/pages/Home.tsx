import { useState } from 'react';
import CapsulePill from '@/components/CapsulePill';
import { Button } from '@/components/ui/button';
import type { CapsuleData, CapsuleAction } from '@/types/capsule';
import { toast } from 'sonner';

// Mock capsule data for demonstration
const mockCapsules: CapsuleData[] = [
  {
    id: 'cap-001',
    title: 'Thermal Anomaly Detected',
    description: 'Temperature spike detected in reactor core zone A3. Immediate attention required.',
    status: 'critical',
    priority: 5,
    timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
    source: 'thermal_sampler',
    metadata: {
      zone: 'A3',
      temperature: '385°C',
      threshold: '350°C',
      deviation: '+10%'
    },
    actions: ['mitigate', 'inspect', 'escalate'],
    utid: 'UTID-thermal-a3-001',
    proofId: 'PRF-thermal-001',
    energyConsumed: 245.8,
    carbonFootprint: 0.1229
  },
  {
    id: 'cap-002',
    title: 'Plasma Dynamics Optimization',
    description: 'WorldModel suggests parameter adjustment for improved efficiency.',
    status: 'warning',
    priority: 3,
    timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
    source: 'world_model',
    metadata: {
      efficiency: '87.3%',
      potential: '92.1%',
      gain: '+4.8%'
    },
    actions: ['inspect', 'acknowledge', 'dismiss'],
    utid: 'UTID-plasma-opt-002',
    energyConsumed: 156.2,
    carbonFootprint: 0.0781
  },
  {
    id: 'cap-003',
    title: 'Edge Adaptation Complete',
    description: 'MicroAdapt successfully adapted to new operating regime.',
    status: 'resolved',
    priority: 2,
    timestamp: new Date(Date.now() - 30 * 60000).toISOString(),
    source: 'microadapt_edge',
    metadata: {
      regime: 'high-throughput',
      adaptation_time: '1.2s',
      accuracy: '98.7%'
    },
    actions: ['inspect', 'dismiss'],
    utid: 'UTID-adapt-003',
    energyConsumed: 89.4,
    carbonFootprint: 0.0447
  },
  {
    id: 'cap-004',
    title: 'System Health Check',
    description: 'All systems operating within normal parameters.',
    status: 'active',
    priority: 1,
    timestamp: new Date(Date.now() - 2 * 60000).toISOString(),
    source: 'system_monitor',
    metadata: {
      cpu: '45%',
      memory: '62%',
      network: 'optimal'
    },
    actions: ['inspect', 'dismiss'],
    energyConsumed: 12.3,
    carbonFootprint: 0.0062
  }
];

export default function Home() {
  const [capsules] = useState<CapsuleData[]>(mockCapsules);
  
  const handleAction = (action: CapsuleAction, capsuleId: string) => {
    const capsule = capsules.find(c => c.id === capsuleId);
    if (!capsule) return;
    
    toast.success(`Action: ${action}`, {
      description: `Executed ${action} on ${capsule.title}`
    });
    
    // In real implementation, this would call the Capsule Gateway API
    console.log(`Action ${action} on capsule ${capsuleId}`);
  };
  
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground">Capsule Pins</h1>
              <p className="text-sm text-muted-foreground">Real-time industrial intelligence</p>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm">
                Settings
              </Button>
              <Button variant="default" size="sm">
                Connect
              </Button>
            </div>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="container py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-card border border-border rounded-lg p-4">
              <p className="text-sm text-muted-foreground">Active Capsules</p>
              <p className="text-2xl font-bold text-foreground mt-1">
                {capsules.filter(c => c.status === 'active').length}
              </p>
            </div>
            <div className="bg-card border border-border rounded-lg p-4">
              <p className="text-sm text-muted-foreground">Warnings</p>
              <p className="text-2xl font-bold text-amber-400 mt-1">
                {capsules.filter(c => c.status === 'warning').length}
              </p>
            </div>
            <div className="bg-card border border-border rounded-lg p-4">
              <p className="text-sm text-muted-foreground">Critical</p>
              <p className="text-2xl font-bold text-rose-400 mt-1">
                {capsules.filter(c => c.status === 'critical').length}
              </p>
            </div>
            <div className="bg-card border border-border rounded-lg p-4">
              <p className="text-sm text-muted-foreground">Resolved</p>
              <p className="text-2xl font-bold text-emerald-400 mt-1">
                {capsules.filter(c => c.status === 'resolved').length}
              </p>
            </div>
          </div>
          
          {/* Capsules List */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-foreground">Live Capsules</h2>
              <p className="text-sm text-muted-foreground">
                {capsules.length} total
              </p>
            </div>
            
            {capsules.map((capsule) => (
              <CapsulePill
                key={capsule.id}
                capsule={capsule}
                onAction={handleAction}
              />
            ))}
          </div>
          
          {/* Info Section */}
          <div className="bg-card border border-border rounded-lg p-6 mt-8">
            <h3 className="text-lg font-semibold text-foreground mb-3">About Capsule Pins</h3>
            <div className="space-y-2 text-sm text-muted-foreground">
              <p>
                Capsule Pins provide real-time visibility into your industrial intelligence ecosystem.
                Each capsule represents an actionable insight from the Industriverse platform.
              </p>
              <p>
                Powered by the complete vertical stack: Remix Lab → A2A → MCP → Thermodynamic Computing → DAC Factory
              </p>
              <p className="text-xs text-muted-foreground/70 mt-4">
                Week 7 - Progressive Web App Implementation
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
