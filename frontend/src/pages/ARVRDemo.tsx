/**
 * AR/VR Demo Page
 * 
 * Showcase MediaPipe gesture controls and TouchDesigner visualizations
 */

import { useState } from 'react';
import { ARVRContainer, type ARVRMode } from '@/components/ar-vr/ARVRContainer';
import { TouchDesignerVisualizer, type CapsuleMetrics } from '@/components/ar-vr/TouchDesignerVisualizer';
import { ProofNetworkVisualizer } from '@/components/ar-vr/ProofNetworkVisualizer';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Link } from 'wouter';
import type { CapsuleData } from '@/types/capsule';

// Mock capsule data with metrics
const mockCapsulesWithMetrics: (CapsuleData & { metrics: CapsuleMetrics })[] = [
  {
    id: 'cap-001',
    title: 'Motor 001 Overheating',
    description: 'Temperature exceeded 80°C',
    status: 'critical',
    priority: 5,
    timestamp: new Date().toISOString(),
    source: 'motor_001',
    actions: ['mitigate', 'inspect', 'escalate'],
    metrics: {
      temperature: 85,
      vibration: 72,
      speed: 3200,
      power: 45,
    },
  },
  {
    id: 'cap-002',
    title: 'High Pressure Alert',
    description: 'Pressure exceeded 85 PSI',
    status: 'warning',
    priority: 3,
    timestamp: new Date().toISOString(),
    source: 'compressor_001',
    actions: ['acknowledge', 'inspect', 'dismiss'],
    metrics: {
      pressure: 88,
      temperature: 65,
      vibration: 45,
    },
  },
  {
    id: 'cap-003',
    title: 'Production Line Optimal',
    description: 'All systems operating normally',
    status: 'active',
    priority: 1,
    timestamp: new Date().toISOString(),
    source: 'line_monitor',
    actions: ['inspect', 'dismiss'],
    metrics: {
      temperature: 45,
      pressure: 60,
      vibration: 30,
      speed: 1800,
      power: 28,
    },
  },
  {
    id: 'cap-004',
    title: 'Maintenance Complete',
    description: 'Scheduled maintenance finished successfully',
    status: 'resolved',
    priority: 2,
    timestamp: new Date().toISOString(),
    source: 'maintenance_system',
    actions: ['inspect', 'dismiss'],
    metrics: {
      temperature: 35,
      pressure: 50,
      vibration: 15,
    },
  },
];

export default function ARVRDemo() {
  const [mode, setMode] = useState<ARVRMode>('2d');
  const [selectedCapsule, setSelectedCapsule] = useState<string | null>(null);

  return (
    <ARVRContainer mode={mode} onModeChange={setMode}>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-40">
          <div className="container py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-foreground">AR/VR Demo</h1>
                <p className="text-sm text-muted-foreground">
                  Gesture-free interaction + Living data visualizations
                </p>
              </div>
              <div className="flex items-center gap-3">
                <Link href="/">
                  <Button variant="outline" size="sm">
                    ← Back to Home
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="container py-8">
          <div className="max-w-6xl mx-auto space-y-8">
            {/* Introduction */}
            <Card>
              <CardHeader>
                <CardTitle>Welcome to AR/VR Mode</CardTitle>
                <CardDescription>
                  Experience the future of industrial intelligence with gesture-free interaction
                  and generative data visualizations
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <h3 className="font-semibold">✋ Gesture Controls</h3>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Point to highlight capsules</li>
                      <li>• Pinch to select</li>
                      <li>• Open palm to dismiss</li>
                      <li>• Thumbs up to acknowledge</li>
                      <li>• Closed fist to execute</li>
                    </ul>
                  </div>
                  <div className="space-y-2">
                    <h3 className="font-semibold">🎨 Living Data Art</h3>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Temperature → Color gradient</li>
                      <li>• Pressure → Glow intensity</li>
                      <li>• Vibration → Pulse amplitude</li>
                      <li>• Speed → Rotation speed</li>
                      <li>• Real-time generative visuals</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Capsule Visualizations */}
            <div className="space-y-4">
              <h2 className="text-xl font-bold">Live Capsule Visualizations</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {mockCapsulesWithMetrics.map((capsule) => (
                  <Card
                    key={capsule.id}
                    data-capsule-id={capsule.id}
                    className={`transition-all ${
                      selectedCapsule === capsule.id ? 'ring-2 ring-primary' : ''
                    }`}
                  >
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle className="text-lg">{capsule.title}</CardTitle>
                          <CardDescription>{capsule.description}</CardDescription>
                        </div>
                        <div
                          className={`px-2 py-1 rounded text-xs font-medium ${
                            capsule.status === 'critical'
                              ? 'bg-red-500/20 text-red-400'
                              : capsule.status === 'warning'
                              ? 'bg-amber-500/20 text-amber-400'
                              : capsule.status === 'active'
                              ? 'bg-green-500/20 text-green-400'
                              : 'bg-gray-500/20 text-gray-400'
                          }`}
                        >
                          {capsule.status}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {/* TouchDesigner Visualization */}
                      <TouchDesignerVisualizer
                        capsuleId={capsule.id}
                        metrics={capsule.metrics}
                        status={capsule.status}
                        enabled={true}
                      />

                      {/* Metrics */}
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        {capsule.metrics.temperature !== undefined && (
                          <div>
                            <span className="text-muted-foreground">Temperature:</span>
                            <span className="ml-2 font-medium">{capsule.metrics.temperature}°C</span>
                          </div>
                        )}
                        {capsule.metrics.pressure !== undefined && (
                          <div>
                            <span className="text-muted-foreground">Pressure:</span>
                            <span className="ml-2 font-medium">{capsule.metrics.pressure} PSI</span>
                          </div>
                        )}
                        {capsule.metrics.vibration !== undefined && (
                          <div>
                            <span className="text-muted-foreground">Vibration:</span>
                            <span className="ml-2 font-medium">{capsule.metrics.vibration} Hz</span>
                          </div>
                        )}
                        {capsule.metrics.speed !== undefined && (
                          <div>
                            <span className="text-muted-foreground">Speed:</span>
                            <span className="ml-2 font-medium">{capsule.metrics.speed} RPM</span>
                          </div>
                        )}
                        {capsule.metrics.power !== undefined && (
                          <div>
                            <span className="text-muted-foreground">Power:</span>
                            <span className="ml-2 font-medium">{capsule.metrics.power} kW</span>
                          </div>
                        )}
                      </div>

                      {/* Actions */}
                      <div className="flex gap-2">
                        {capsule.actions.map((action) => (
                          <Button
                            key={action}
                            variant="outline"
                            size="sm"
                            data-action={action}
                            onClick={() => {
                              console.log(`Action: ${action} on ${capsule.id}`);
                              setSelectedCapsule(capsule.id);
                            }}
                          >
                            {action}
                          </Button>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            {/* Proof Network Visualizer */}
            <Card>
              <CardHeader>
                <CardTitle>Shadow Twin Consensus Network</CardTitle>
                <CardDescription>
                  Real-time 3D visualization of distributed predictor network
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[500px]">
                  <ProofNetworkVisualizer enabled={true} showMetrics={true} />
                </div>
              </CardContent>
            </Card>

            {/* Performance Stats */}
            <Card>
              <CardHeader>
                <CardTitle>Performance Metrics</CardTitle>
                <CardDescription>Real-time rendering statistics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Rendering:</span>
                    <span className="ml-2 font-medium text-green-400">60 FPS</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Hand Tracking:</span>
                    <span className="ml-2 font-medium text-green-400">30 FPS</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Gesture Latency:</span>
                    <span className="ml-2 font-medium text-green-400">&lt;50ms</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Active Capsules:</span>
                    <span className="ml-2 font-medium">{mockCapsulesWithMetrics.length}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </ARVRContainer>
  );
}
