/**
 * AmI Visualization Dashboard
 * Week 8: White-Label Platform - Phase 4 Final
 * 
 * Real-time visualization of 4 AmI principles across all deployments:
 * - Context Awareness
 * - Proactivity
 * - Seamlessness
 * - Adaptivity
 */

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useAmiWebSocket } from '@/hooks/useAmiWebSocket';
import { toast } from 'sonner';

interface AmIMetric {
  timestamp: number;
  contextAwareness: number;
  proactivity: number;
  seamlessness: number;
  adaptivity: number;
}

interface DeploymentMetrics {
  deploymentId: string;
  deploymentName: string;
  metrics: AmIMetric[];
  currentScore: {
    contextAwareness: number;
    proactivity: number;
    seamlessness: number;
    adaptivity: number;
  };
}

const TIME_RANGES = [
  { label: '1 Hour', value: '1h', minutes: 60 },
  { label: '24 Hours', value: '24h', minutes: 1440 },
  { label: '7 Days', value: '7d', minutes: 10080 },
  { label: '30 Days', value: '30d', minutes: 43200 },
];

export default function AmIVisualizationDashboard() {
  const [timeRange, setTimeRange] = useState('24h');
  const [deployments, setDeployments] = useState<DeploymentMetrics[]>([]);
  const [selectedDeployment, setSelectedDeployment] = useState<string>('all');
  const [isLive, setIsLive] = useState(true);

  // Connect to WebSocket for real-time AmI metrics
  const { isConnected, metrics, history } = useAmiWebSocket({
    autoConnect: isLive,
  });

  // Show connection status
  useEffect(() => {
    if (isConnected) {
      toast.success('Connected to AmI Metrics Stream', {
        description: 'Receiving real-time data from all deployments',
      });
    }
  }, [isConnected]);

  // Update deployments with real WebSocket data
  useEffect(() => {
    // Group history by deployment
    const deploymentMap = new Map<string, typeof history>();
    history.forEach(metric => {
      if (!deploymentMap.has(metric.deploymentId)) {
        deploymentMap.set(metric.deploymentId, []);
      }
      deploymentMap.get(metric.deploymentId)!.push(metric);
    });

    const mockDeploymentNames: Record<string, string> = {
      'tsmc-fab18-prod': 'TSMC Fab 18',
      'intel-oregon-prod': 'Intel Oregon',
      'samsung-austin-prod': 'Samsung Austin',
    };

    const newDeployments: DeploymentMetrics[] = Array.from(deploymentMap.entries()).map(([deploymentId, depMetrics]) => {
      // Group metrics by principle to get current scores
      const latestByPrinciple: Record<string, number> = {};
      depMetrics.forEach(m => {
        latestByPrinciple[m.principle] = m.value;
      });

      // Convert to AmIMetric format for charts
      const chartMetrics: AmIMetric[] = depMetrics.map(m => ({
        timestamp: new Date(m.timestamp).getTime(),
        contextAwareness: latestByPrinciple['context'] || 0,
        proactivity: latestByPrinciple['proactivity'] || 0,
        seamlessness: latestByPrinciple['seamlessness'] || 0,
        adaptivity: latestByPrinciple['adaptivity'] || 0,
      }));

      return {
        deploymentId,
        deploymentName: mockDeploymentNames[deploymentId] || deploymentId,
        metrics: chartMetrics,
        currentScore: {
          contextAwareness: latestByPrinciple['context'] || 0,
          proactivity: latestByPrinciple['proactivity'] || 0,
          seamlessness: latestByPrinciple['seamlessness'] || 0,
          adaptivity: latestByPrinciple['adaptivity'] || 0,
        },
      };
    });

    if (newDeployments.length > 0) {
      setDeployments(newDeployments);
    }
  }, [history]);

  const getAggregatedMetrics = () => {
    if (selectedDeployment === 'all') {
      // Average across all deployments
      const allMetrics = deployments.flatMap(d => d.metrics);
      const grouped = new Map<number, AmIMetric[]>();

      allMetrics.forEach(m => {
        const key = Math.floor(m.timestamp / 60000) * 60000; // Round to minute
        if (!grouped.has(key)) grouped.set(key, []);
        grouped.get(key)!.push(m);
      });

      return Array.from(grouped.entries())
        .map(([timestamp, metrics]) => ({
          timestamp,
          contextAwareness: metrics.reduce((sum, m) => sum + m.contextAwareness, 0) / metrics.length,
          proactivity: metrics.reduce((sum, m) => sum + m.proactivity, 0) / metrics.length,
          seamlessness: metrics.reduce((sum, m) => sum + m.seamlessness, 0) / metrics.length,
          adaptivity: metrics.reduce((sum, m) => sum + m.adaptivity, 0) / metrics.length,
        }))
        .sort((a, b) => a.timestamp - b.timestamp);
    } else {
      return deployments.find(d => d.deploymentId === selectedDeployment)?.metrics || [];
    }
  };

  const getCurrentScores = () => {
    if (deployments.length === 0) {
      // Use WebSocket metrics directly if no deployment data yet
      return {
        contextAwareness: metrics.context,
        proactivity: metrics.proactivity,
        seamlessness: metrics.seamlessness,
        adaptivity: metrics.adaptivity,
      };
    }

    if (selectedDeployment === 'all') {
      const scores = deployments.map(d => d.currentScore);
      return {
        contextAwareness: scores.reduce((sum, s) => sum + s.contextAwareness, 0) / scores.length,
        proactivity: scores.reduce((sum, s) => sum + s.proactivity, 0) / scores.length,
        seamlessness: scores.reduce((sum, s) => sum + s.seamlessness, 0) / scores.length,
        adaptivity: scores.reduce((sum, s) => sum + s.adaptivity, 0) / scores.length,
      };
    } else {
      return deployments.find(d => d.deploymentId === selectedDeployment)?.currentScore || {
        contextAwareness: 0,
        proactivity: 0,
        seamlessness: 0,
        adaptivity: 0,
      };
    }
  };

  const aggregatedMetrics = getAggregatedMetrics();
  const currentScores = getCurrentScores();

  const renderMiniChart = (data: number[], color: string) => {
    if (data.length === 0) return null;

    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min || 1;

    const points = data
      .map((value, index) => {
        const x = (index / (data.length - 1)) * 100;
        const y = 100 - ((value - min) / range) * 100;
        return `${x},${y}`;
      })
      .join(' ');

    return (
      <svg viewBox="0 0 100 100" className="w-full h-24" preserveAspectRatio="none">
        <polyline
          points={points}
          fill="none"
          stroke={color}
          strokeWidth="2"
          vectorEffect="non-scaling-stroke"
        />
      </svg>
    );
  };

  const handleExport = () => {
    const data = {
      timeRange,
      deployment: selectedDeployment,
      exportTime: new Date().toISOString(),
      metrics: getAggregatedMetrics(),
      currentScores: getCurrentScores(),
    };

    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ami-metrics-${selectedDeployment}-${timeRange}-${Date.now()}.json`;
    a.click();
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground">AmI Visualization Dashboard</h1>
              <p className="text-sm text-muted-foreground">
                Real-time ambient intelligence metrics across all deployments
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Button
                variant={isLive ? 'default' : 'outline'}
                size="sm"
                onClick={() => setIsLive(!isLive)}
              >
                {isLive ? '🔴 Live' : '⏸ Paused'}
              </Button>
              <Button variant="outline" size="sm" onClick={handleExport}>
                Export Data
              </Button>
              <Button variant="outline" onClick={() => (window.location.href = '/admin')}>
                Back to Admin
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Controls */}
      <div className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <div>
              <label className="text-sm font-medium mr-2">Deployment:</label>
              <select
                value={selectedDeployment}
                onChange={(e) => setSelectedDeployment(e.target.value)}
                className="px-3 py-2 bg-background border border-border rounded"
              >
                <option value="all">All Deployments (Aggregated)</option>
                {deployments.map((dep) => (
                  <option key={dep.deploymentId} value={dep.deploymentId}>
                    {dep.deploymentName}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-sm font-medium mr-2">Time Range:</label>
              <div className="inline-flex gap-1">
                {TIME_RANGES.map((range) => (
                  <Button
                    key={range.value}
                    variant={timeRange === range.value ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setTimeRange(range.value)}
                  >
                    {range.label}
                  </Button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Current Scores */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-muted-foreground">Context Awareness</h3>
              <div className="text-2xl">🎯</div>
            </div>
            <div className="text-3xl font-bold text-brand-primary mb-2">
              {currentScores.contextAwareness.toFixed(1)}%
            </div>
            {renderMiniChart(
              aggregatedMetrics.map(m => m.contextAwareness),
              '#0ea5e9'
            )}
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-muted-foreground">Proactivity</h3>
              <div className="text-2xl">⚡</div>
            </div>
            <div className="text-3xl font-bold text-brand-secondary mb-2">
              {currentScores.proactivity.toFixed(1)}%
            </div>
            {renderMiniChart(
              aggregatedMetrics.map(m => m.proactivity),
              '#8b5cf6'
            )}
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-muted-foreground">Seamlessness</h3>
              <div className="text-2xl">🌊</div>
            </div>
            <div className="text-3xl font-bold text-status-success mb-2">
              {currentScores.seamlessness.toFixed(1)}%
            </div>
            {renderMiniChart(
              aggregatedMetrics.map(m => m.seamlessness),
              '#10b981'
            )}
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-muted-foreground">Adaptivity</h3>
              <div className="text-2xl">🔄</div>
            </div>
            <div className="text-3xl font-bold text-brand-accent mb-2">
              {currentScores.adaptivity.toFixed(1)}%
            </div>
            {renderMiniChart(
              aggregatedMetrics.map(m => m.adaptivity),
              '#f59e0b'
            )}
          </Card>
        </div>

        {/* Detailed Charts */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="context">Context</TabsTrigger>
            <TabsTrigger value="proactive">Proactive</TabsTrigger>
            <TabsTrigger value="seamless">Seamless</TabsTrigger>
            <TabsTrigger value="adaptive">Adaptive</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">All AmI Principles</h2>
              <div className="h-96 flex items-center justify-center bg-muted/20 rounded">
                <div className="text-center">
                  <p className="text-muted-foreground mb-4">
                    Combined visualization of all 4 AmI principles over time
                  </p>
                  <div className="text-sm text-muted-foreground">
                    📊 Chart library integration: Use Recharts or Chart.js for production
                  </div>
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Deployment Comparison</h2>
              <div className="space-y-4">
                {deployments.map((dep) => (
                  <div key={dep.deploymentId}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{dep.deploymentName}</span>
                      <span className="text-sm text-muted-foreground">
                        Avg: {(
                          (dep.currentScore.contextAwareness +
                            dep.currentScore.proactivity +
                            dep.currentScore.seamlessness +
                            dep.currentScore.adaptivity) / 4
                        ).toFixed(1)}%
                      </span>
                    </div>
                    <div className="grid grid-cols-4 gap-2">
                      <div className="h-2 bg-brand-primary rounded" style={{ width: `${dep.currentScore.contextAwareness}%` }} />
                      <div className="h-2 bg-brand-secondary rounded" style={{ width: `${dep.currentScore.proactivity}%` }} />
                      <div className="h-2 bg-status-success rounded" style={{ width: `${dep.currentScore.seamlessness}%` }} />
                      <div className="h-2 bg-brand-accent rounded" style={{ width: `${dep.currentScore.adaptivity}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="context">
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Context Awareness</h2>
              <p className="text-sm text-muted-foreground mb-4">
                Measures how well the system understands and adapts to user context, environment, and situational factors.
              </p>
              <div className="h-96 flex items-center justify-center bg-muted/20 rounded">
                <p className="text-muted-foreground">Context Awareness trend chart</p>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="proactive">
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Proactivity</h2>
              <p className="text-sm text-muted-foreground mb-4">
                Tracks the system's ability to anticipate user needs and take preemptive actions without explicit requests.
              </p>
              <div className="h-96 flex items-center justify-center bg-muted/20 rounded">
                <p className="text-muted-foreground">Proactivity trend chart</p>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="seamless">
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Seamlessness</h2>
              <p className="text-sm text-muted-foreground mb-4">
                Evaluates how invisibly and naturally the system integrates into user workflows and operations.
              </p>
              <div className="h-96 flex items-center justify-center bg-muted/20 rounded">
                <p className="text-muted-foreground">Seamlessness trend chart</p>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="adaptive">
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Adaptivity</h2>
              <p className="text-sm text-muted-foreground mb-4">
                Monitors the system's capacity to learn from interactions and continuously improve its behavior.
              </p>
              <div className="h-96 flex items-center justify-center bg-muted/20 rounded">
                <p className="text-muted-foreground">Adaptivity trend chart</p>
              </div>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Network Intelligence */}
        <Card className="p-6 mt-8">
          <h2 className="text-xl font-semibold mb-4">Cosmic Intelligence Fabric</h2>
          <p className="text-sm text-muted-foreground mb-6">
            Federated learning insights aggregated across all white-label deployments while preserving privacy.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="p-4">
              <div className="text-sm text-muted-foreground">Pattern Sharing</div>
              <div className="text-2xl font-bold mt-2">2,847</div>
              <div className="text-xs text-status-success mt-1">+12% this week</div>
            </Card>

            <Card className="p-4">
              <div className="text-sm text-muted-foreground">Privacy Score</div>
              <div className="text-2xl font-bold mt-2">98.5%</div>
              <div className="text-xs text-muted-foreground mt-1">Differential privacy</div>
            </Card>

            <Card className="p-4">
              <div className="text-sm text-muted-foreground">Network Effect</div>
              <div className="text-2xl font-bold mt-2">3.2x</div>
              <div className="text-xs text-muted-foreground mt-1">Intelligence multiplier</div>
            </Card>
          </div>
        </Card>
      </main>
    </div>
  );
}
