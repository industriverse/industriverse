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
var TIME_RANGES = [
    { label: '1 Hour', value: '1h', minutes: 60 },
    { label: '24 Hours', value: '24h', minutes: 1440 },
    { label: '7 Days', value: '7d', minutes: 10080 },
    { label: '30 Days', value: '30d', minutes: 43200 },
];
export default function AmIVisualizationDashboard() {
    var _a = useState('24h'), timeRange = _a[0], setTimeRange = _a[1];
    var _b = useState([]), deployments = _b[0], setDeployments = _b[1];
    var _c = useState('all'), selectedDeployment = _c[0], setSelectedDeployment = _c[1];
    var _d = useState(true), isLive = _d[0], setIsLive = _d[1];
    // Generate mock data for visualization
    useEffect(function () {
        var generateMockData = function () {
            var _a;
            var now = Date.now();
            var range = ((_a = TIME_RANGES.find(function (r) { return r.value === timeRange; })) === null || _a === void 0 ? void 0 : _a.minutes) || 1440;
            var points = Math.min(range / 5, 100); // Max 100 data points
            var mockDeployments = [
                { id: 'tsmc-fab-18', name: 'TSMC Fab 18' },
                { id: 'intel-oregon', name: 'Intel Oregon' },
                { id: 'samsung-austin', name: 'Samsung Austin' },
            ];
            return mockDeployments.map(function (dep) {
                var metrics = [];
                for (var i = 0; i < points; i++) {
                    var timestamp = now - (points - i) * (range / points) * 60 * 1000;
                    metrics.push({
                        timestamp: timestamp,
                        contextAwareness: 70 + Math.random() * 25 + Math.sin(i / 10) * 5,
                        proactivity: 65 + Math.random() * 25 + Math.cos(i / 8) * 5,
                        seamlessness: 85 + Math.random() * 12 + Math.sin(i / 12) * 3,
                        adaptivity: 75 + Math.random() * 20 + Math.cos(i / 15) * 5,
                    });
                }
                var latest = metrics[metrics.length - 1];
                return {
                    deploymentId: dep.id,
                    deploymentName: dep.name,
                    metrics: metrics,
                    currentScore: {
                        contextAwareness: latest.contextAwareness,
                        proactivity: latest.proactivity,
                        seamlessness: latest.seamlessness,
                        adaptivity: latest.adaptivity,
                    },
                };
            });
        };
        setDeployments(generateMockData());
        // Simulate real-time updates
        if (isLive) {
            var interval_1 = setInterval(function () {
                setDeployments(generateMockData());
            }, 5000);
            return function () { return clearInterval(interval_1); };
        }
    }, [timeRange, isLive]);
    var getAggregatedMetrics = function () {
        var _a;
        if (selectedDeployment === 'all') {
            // Average across all deployments
            var allMetrics = deployments.flatMap(function (d) { return d.metrics; });
            var grouped_1 = new Map();
            allMetrics.forEach(function (m) {
                var key = Math.floor(m.timestamp / 60000) * 60000; // Round to minute
                if (!grouped_1.has(key))
                    grouped_1.set(key, []);
                grouped_1.get(key).push(m);
            });
            return Array.from(grouped_1.entries())
                .map(function (_a) {
                var timestamp = _a[0], metrics = _a[1];
                return ({
                    timestamp: timestamp,
                    contextAwareness: metrics.reduce(function (sum, m) { return sum + m.contextAwareness; }, 0) / metrics.length,
                    proactivity: metrics.reduce(function (sum, m) { return sum + m.proactivity; }, 0) / metrics.length,
                    seamlessness: metrics.reduce(function (sum, m) { return sum + m.seamlessness; }, 0) / metrics.length,
                    adaptivity: metrics.reduce(function (sum, m) { return sum + m.adaptivity; }, 0) / metrics.length,
                });
            })
                .sort(function (a, b) { return a.timestamp - b.timestamp; });
        }
        else {
            return ((_a = deployments.find(function (d) { return d.deploymentId === selectedDeployment; })) === null || _a === void 0 ? void 0 : _a.metrics) || [];
        }
    };
    var getCurrentScores = function () {
        var _a;
        if (selectedDeployment === 'all') {
            var scores = deployments.map(function (d) { return d.currentScore; });
            return {
                contextAwareness: scores.reduce(function (sum, s) { return sum + s.contextAwareness; }, 0) / scores.length,
                proactivity: scores.reduce(function (sum, s) { return sum + s.proactivity; }, 0) / scores.length,
                seamlessness: scores.reduce(function (sum, s) { return sum + s.seamlessness; }, 0) / scores.length,
                adaptivity: scores.reduce(function (sum, s) { return sum + s.adaptivity; }, 0) / scores.length,
            };
        }
        else {
            return ((_a = deployments.find(function (d) { return d.deploymentId === selectedDeployment; })) === null || _a === void 0 ? void 0 : _a.currentScore) || {
                contextAwareness: 0,
                proactivity: 0,
                seamlessness: 0,
                adaptivity: 0,
            };
        }
    };
    var metrics = getAggregatedMetrics();
    var currentScores = getCurrentScores();
    var renderMiniChart = function (data, color) {
        if (data.length === 0)
            return null;
        var max = Math.max.apply(Math, data);
        var min = Math.min.apply(Math, data);
        var range = max - min || 1;
        var points = data
            .map(function (value, index) {
            var x = (index / (data.length - 1)) * 100;
            var y = 100 - ((value - min) / range) * 100;
            return "".concat(x, ",").concat(y);
        })
            .join(' ');
        return (<svg viewBox="0 0 100 100" className="w-full h-24" preserveAspectRatio="none">
        <polyline points={points} fill="none" stroke={color} strokeWidth="2" vectorEffect="non-scaling-stroke"/>
      </svg>);
    };
    var handleExport = function () {
        var data = {
            timeRange: timeRange,
            deployment: selectedDeployment,
            exportTime: new Date().toISOString(),
            metrics: getAggregatedMetrics(),
            currentScores: getCurrentScores(),
        };
        var json = JSON.stringify(data, null, 2);
        var blob = new Blob([json], { type: 'application/json' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = "ami-metrics-".concat(selectedDeployment, "-").concat(timeRange, "-").concat(Date.now(), ".json");
        a.click();
    };
    return (<div className="min-h-screen bg-background">
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
              <Button variant={isLive ? 'default' : 'outline'} size="sm" onClick={function () { return setIsLive(!isLive); }}>
                {isLive ? '🔴 Live' : '⏸ Paused'}
              </Button>
              <Button variant="outline" size="sm" onClick={handleExport}>
                Export Data
              </Button>
              <Button variant="outline" onClick={function () { return (window.location.href = '/admin'); }}>
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
              <select value={selectedDeployment} onChange={function (e) { return setSelectedDeployment(e.target.value); }} className="px-3 py-2 bg-background border border-border rounded">
                <option value="all">All Deployments (Aggregated)</option>
                {deployments.map(function (dep) { return (<option key={dep.deploymentId} value={dep.deploymentId}>
                    {dep.deploymentName}
                  </option>); })}
              </select>
            </div>

            <div>
              <label className="text-sm font-medium mr-2">Time Range:</label>
              <div className="inline-flex gap-1">
                {TIME_RANGES.map(function (range) { return (<Button key={range.value} variant={timeRange === range.value ? 'default' : 'outline'} size="sm" onClick={function () { return setTimeRange(range.value); }}>
                    {range.label}
                  </Button>); })}
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
            {renderMiniChart(metrics.map(function (m) { return m.contextAwareness; }), '#0ea5e9')}
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-muted-foreground">Proactivity</h3>
              <div className="text-2xl">⚡</div>
            </div>
            <div className="text-3xl font-bold text-brand-secondary mb-2">
              {currentScores.proactivity.toFixed(1)}%
            </div>
            {renderMiniChart(metrics.map(function (m) { return m.proactivity; }), '#8b5cf6')}
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-muted-foreground">Seamlessness</h3>
              <div className="text-2xl">🌊</div>
            </div>
            <div className="text-3xl font-bold text-status-success mb-2">
              {currentScores.seamlessness.toFixed(1)}%
            </div>
            {renderMiniChart(metrics.map(function (m) { return m.seamlessness; }), '#10b981')}
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-muted-foreground">Adaptivity</h3>
              <div className="text-2xl">🔄</div>
            </div>
            <div className="text-3xl font-bold text-brand-accent mb-2">
              {currentScores.adaptivity.toFixed(1)}%
            </div>
            {renderMiniChart(metrics.map(function (m) { return m.adaptivity; }), '#f59e0b')}
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
                {deployments.map(function (dep) { return (<div key={dep.deploymentId}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{dep.deploymentName}</span>
                      <span className="text-sm text-muted-foreground">
                        Avg: {((dep.currentScore.contextAwareness +
                dep.currentScore.proactivity +
                dep.currentScore.seamlessness +
                dep.currentScore.adaptivity) / 4).toFixed(1)}%
                      </span>
                    </div>
                    <div className="grid grid-cols-4 gap-2">
                      <div className="h-2 bg-brand-primary rounded" style={{ width: "".concat(dep.currentScore.contextAwareness, "%") }}/>
                      <div className="h-2 bg-brand-secondary rounded" style={{ width: "".concat(dep.currentScore.proactivity, "%") }}/>
                      <div className="h-2 bg-status-success rounded" style={{ width: "".concat(dep.currentScore.seamlessness, "%") }}/>
                      <div className="h-2 bg-brand-accent rounded" style={{ width: "".concat(dep.currentScore.adaptivity, "%") }}/>
                    </div>
                  </div>); })}
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
    </div>);
}
//# sourceMappingURL=AmIVisualizationDashboard.jsx.map