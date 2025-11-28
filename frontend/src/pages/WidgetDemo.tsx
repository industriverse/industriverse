// @ts-nocheck
/**
 * Widget Demo Page
 * Week 8: White-Label Platform
 * Showcase all <iv-*> widgets with live theme switching
 */

/// <reference path="../widgets/custom-elements.d.ts" />

import React, { useEffect, useState } from 'react';
import { ThemeSwitcher } from '../components/ThemeSwitcher';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { toast } from 'sonner';

// Import widgets to register them
import '../widgets/iv-wallet-orb';
import '../widgets/iv-proof-ticker';
import '../widgets/iv-capsule-card';

export default function WidgetDemo() {
  const [walletBalance, setWalletBalance] = useState(1250.50);

  useEffect(() => {
    // Listen for widget events
    const handleViewCapsule = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      toast.info(`View Capsule: ${detail.title}`, {
        description: `ID: ${detail.capsuleId}, Status: ${detail.status}`,
      });
    };

    const handleProofAdded = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      toast.success(`New Proof: ${detail.type}`, {
        description: `Value: $${detail.value.toFixed(2)}`,
      });
    };

    document.addEventListener('view-capsule', handleViewCapsule);
    document.addEventListener('proof-added', handleProofAdded);

    return () => {
      document.removeEventListener('view-capsule', handleViewCapsule);
      document.removeEventListener('proof-added', handleProofAdded);
    };
  }, []);

  const simulateBalanceChange = () => {
    const change = (Math.random() - 0.5) * 500;
    setWalletBalance(prev => Math.max(0, prev + change));
  };

  const simulateProofGeneration = () => {
    const proofTypes = ['execution', 'energy', 'optimization', 'calibration', 'thermodynamic'];
    const randomType = proofTypes[Math.floor(Math.random() * proofTypes.length)];
    const randomValue = Math.random() * 10;

    const ticker = document.querySelector('iv-proof-ticker');
    if (ticker) {
      // Simulate WebSocket message
      const event = new MessageEvent('message', {
        data: JSON.stringify({
          type: 'proof_generated',
          id: `proof_${Date.now()}`,
          proofType: randomType,
          value: randomValue,
          source: 'demo_simulator',
        }),
      });

      // Trigger the widget's WebSocket handler
      (ticker as any).onWebSocketMessage(event);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold">Widget Demo</h1>
            <p className="text-muted-foreground mt-2">
              Week 8: White-Label Platform - Interactive widget showcase
            </p>
          </div>
          <Button variant="outline" onClick={() => window.history.back()}>
            ← Back
          </Button>
        </div>

        {/* Theme Switcher */}
        <Card className="p-6">
          <h2 className="text-2xl font-semibold mb-4">Theme Configuration</h2>
          <ThemeSwitcher showPreview={true} />
        </Card>

        {/* Widget Showcase */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Wallet Orb Widget */}
          <Card className="p-6">
            <h3 className="text-xl font-semibold mb-4">Wallet Orb Widget</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Real-time balance display with AmI glow effects
            </p>

            <div className="flex flex-col items-center gap-4">
              <iv-wallet-orb
                balance={walletBalance.toString()}
                currency="USD"
              />

              <div className="flex gap-2">
                <Button onClick={simulateBalanceChange} size="sm">
                  Simulate Change
                </Button>
                <Button onClick={() => setWalletBalance(1250.50)} variant="outline" size="sm">
                  Reset
                </Button>
              </div>
            </div>

            <div className="mt-4 p-3 bg-muted rounded text-sm font-mono">
              {`<iv-wallet-orb
  balance="${walletBalance.toFixed(2)}"
  currency="USD"
/>`}
            </div>
          </Card>

          {/* Proof Ticker Widget */}
          <Card className="p-6">
            <h3 className="text-xl font-semibold mb-4">Proof Ticker Widget</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Real-time proof generation feed
            </p>

            <div className="space-y-4">
              <iv-proof-ticker
                max-items="5"
                scroll-speed="normal"
              />

              <Button onClick={simulateProofGeneration} size="sm" className="w-full">
                Generate Random Proof
              </Button>
            </div>

            <div className="mt-4 p-3 bg-muted rounded text-sm font-mono">
              {`<iv-proof-ticker
  max-items="5"
  scroll-speed="normal"
/>`}
            </div>
          </Card>

          {/* Capsule Card Widgets */}
          <Card className="p-6 lg:col-span-2">
            <h3 className="text-xl font-semibold mb-4">Capsule Card Widgets</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Compact capsule displays with status indicators
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <iv-capsule-card
                capsule-id="cap_001"
                title="System Health Check"
                status="active"
                priority="P1"
                source="system_monitor"
                description="Regular system health monitoring"
              />

              <iv-capsule-card
                capsule-id="cap_002"
                title="Thermal Anomaly Detected"
                status="critical"
                priority="P5"
                source="thermal_sampler"
                description="Temperature spike in Zone A"
              />

              <iv-capsule-card
                capsule-id="cap_003"
                title="Plasma Dynamics Optimization"
                status="warning"
                priority="P3"
                source="world_model"
                description="Optimization in progress"
              />

              <iv-capsule-card
                capsule-id="cap_004"
                title="Edge Adaptation Complete"
                status="resolved"
                priority="P2"
                source="microadapt_edge"
                description="Successfully adapted to new regime"
              />
            </div>

            <div className="mt-4 p-3 bg-muted rounded text-sm font-mono">
              {`<iv-capsule-card
  capsule-id="cap_001"
  title="System Health Check"
  status="active"
  priority="P1"
  source="system_monitor"
/>`}
            </div>
          </Card>
        </div>

        {/* Widget Documentation */}
        <Card className="p-6">
          <h2 className="text-2xl font-semibold mb-4">Widget Documentation</h2>

          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold mb-2">Embedding Widgets</h3>
              <p className="text-sm text-muted-foreground mb-2">
                All widgets are custom elements that can be embedded anywhere:
              </p>
              <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                <li>Pure HTML pages</li>
                <li>React/Vue/Angular applications</li>
                <li>WordPress/Drupal sites</li>
                <li>Electron/Tauri desktop apps</li>
                <li>Mobile WebView apps</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">Theme Integration</h3>
              <p className="text-sm text-muted-foreground">
                Widgets automatically inherit theme from CSS custom properties.
                Change the theme above to see all widgets update instantly.
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">WebSocket Support</h3>
              <p className="text-sm text-muted-foreground">
                Add <code className="bg-muted px-1 rounded">ws-url</code> attribute to enable real-time updates:
              </p>
              <pre className="mt-2 p-3 bg-muted rounded text-sm font-mono overflow-x-auto">
                {`<iv-proof-ticker
  ws-url="wss://api.industriverse.io/ws"
  user-id="user123"
  max-items="10"
/>`}
              </pre>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">Event Handling</h3>
              <p className="text-sm text-muted-foreground">
                Widgets emit custom events that you can listen to:
              </p>
              <pre className="mt-2 p-3 bg-muted rounded text-sm font-mono overflow-x-auto">
                {`document.addEventListener('view-capsule', (e) => {
  console.log('Capsule clicked:', e.detail);
});

document.addEventListener('proof-added', (e) => {
  console.log('New proof:', e.detail);
});`}
              </pre>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
