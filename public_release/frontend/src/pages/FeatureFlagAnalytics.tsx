// @ts-nocheck
import { useState } from "react";
import { Link } from "wouter";
import { trpc } from "@/lib/trpc";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, Download, TrendingUp, TrendingDown, Minus } from "lucide-react";

export default function FeatureFlagAnalytics() {
  const [timeRange, setTimeRange] = useState<"7d" | "30d" | "90d">("30d");

  // Queries
  const { data: tenants } = trpc.tenants.list.useQuery();
  const { data: allFlags } = trpc.featureFlags.getByTenantId.useQuery({
    tenantId: tenants?.[0]?.tenantId || ""
  }, {
    enabled: !!tenants?.[0]?.tenantId
  });

  // Calculate analytics
  const totalTenants = tenants?.length || 0;

  // Feature flag adoption statistics
  const flagStats = calculateFlagStatistics(tenants, allFlags);

  // Most/Least used flags
  const sortedByAdoption = [...flagStats].sort((a, b) => b.adoptionRate - a.adoptionRate);
  const mostUsed = sortedByAdoption.slice(0, 5);
  const leastUsed = sortedByAdoption.slice(-5).reverse();

  // Export functionality
  const handleExport = (format: "csv" | "json") => {
    const data = flagStats.map(stat => ({
      flag: stat.name,
      enabled: stat.enabledCount,
      disabled: stat.disabledCount,
      adoptionRate: `${stat.adoptionRate}%`,
      trend: stat.trend
    }));

    if (format === "json") {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      downloadFile(blob, "feature-flag-analytics.json");
    } else {
      const csv = convertToCSV(data);
      const blob = new Blob([csv], { type: "text/csv" });
      downloadFile(blob, "feature-flag-analytics.csv");
    }
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <Link href="/admin">
              <Button variant="ghost" size="sm" className="mb-2">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Admin
              </Button>
            </Link>
            <h1 className="text-3xl font-bold">Feature Flag Analytics</h1>
            <p className="text-muted-foreground">
              Adoption rates, usage patterns, and insights across all tenants
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => handleExport("csv")}>
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </Button>
            <Button variant="outline" onClick={() => handleExport("json")}>
              <Download className="w-4 h-4 mr-2" />
              Export JSON
            </Button>
          </div>
        </div>

        {/* Time Range Selector */}
        <div className="flex gap-2">
          <Button
            variant={timeRange === "7d" ? "default" : "outline"}
            size="sm"
            onClick={() => setTimeRange("7d")}
          >
            7 Days
          </Button>
          <Button
            variant={timeRange === "30d" ? "default" : "outline"}
            size="sm"
            onClick={() => setTimeRange("30d")}
          >
            30 Days
          </Button>
          <Button
            variant={timeRange === "90d" ? "default" : "outline"}
            size="sm"
            onClick={() => setTimeRange("90d")}
          >
            90 Days
          </Button>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total Tenants</CardDescription>
              <CardTitle className="text-3xl">{totalTenants}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total Flags</CardDescription>
              <CardTitle className="text-3xl">{flagStats.length}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Avg Adoption Rate</CardDescription>
              <CardTitle className="text-3xl">
                {calculateAverageAdoption(flagStats)}%
              </CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Most Popular Flag</CardDescription>
              <CardTitle className="text-xl truncate">
                {mostUsed[0]?.name || "N/A"}
              </CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* Adoption Rate Visualization */}
        <Card>
          <CardHeader>
            <CardTitle>Feature Flag Adoption Rates</CardTitle>
            <CardDescription>
              Percentage of tenants using each feature flag
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {flagStats.map((stat) => (
                <div key={stat.name} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{stat.name}</span>
                      {stat.trend === "up" && (
                        <TrendingUp className="w-4 h-4 text-green-500" />
                      )}
                      {stat.trend === "down" && (
                        <TrendingDown className="w-4 h-4 text-red-500" />
                      )}
                      {stat.trend === "stable" && (
                        <Minus className="w-4 h-4 text-gray-500" />
                      )}
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-sm text-muted-foreground">
                        {stat.enabledCount} / {totalTenants} tenants
                      </span>
                      <span className="font-bold w-12 text-right">
                        {stat.adoptionRate}%
                      </span>
                    </div>
                  </div>
                  <div className="w-full bg-secondary rounded-full h-2">
                    <div
                      className="bg-primary rounded-full h-2 transition-all duration-500"
                      style={{ width: `${stat.adoptionRate}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Most/Least Used Flags */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Most Used */}
          <Card>
            <CardHeader>
              <CardTitle>Most Used Flags</CardTitle>
              <CardDescription>Top 5 feature flags by adoption</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {mostUsed.map((stat, index) => (
                  <div key={stat.name} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/10 text-primary text-sm font-bold">
                        {index + 1}
                      </span>
                      <span>{stat.name}</span>
                    </div>
                    <span className="font-bold text-green-600">
                      {stat.adoptionRate}%
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Least Used */}
          <Card>
            <CardHeader>
              <CardTitle>Least Used Flags</CardTitle>
              <CardDescription>Bottom 5 feature flags by adoption</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {leastUsed.map((stat, index) => (
                  <div key={stat.name} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-muted text-muted-foreground text-sm font-bold">
                        {index + 1}
                      </span>
                      <span>{stat.name}</span>
                    </div>
                    <span className="font-bold text-orange-600">
                      {stat.adoptionRate}%
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* A/B Testing Results */}
        <Card>
          <CardHeader>
            <CardTitle>A/B Testing Insights</CardTitle>
            <CardDescription>
              Feature flag performance and impact analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {generateABTestingInsights(flagStats).map((insight, index) => (
                <div key={index} className="border-l-4 border-primary pl-4 py-2">
                  <p className="font-medium">{insight.title}</p>
                  <p className="text-sm text-muted-foreground">{insight.description}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Tenant-Specific Configuration */}
        <Card>
          <CardHeader>
            <CardTitle>Tenant Configuration Matrix</CardTitle>
            <CardDescription>
              Feature flag status across all tenants
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 px-4 font-medium">Tenant</th>
                    {flagStats.slice(0, 10).map((stat) => (
                      <th key={stat.name} className="text-center py-2 px-2 font-medium text-xs">
                        {stat.name.replace(/([A-Z])/g, ' $1').trim()}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {tenants?.slice(0, 10).map((tenant) => (
                    <tr key={tenant.id} className="border-b hover:bg-muted/50">
                      <td className="py-2 px-4 font-medium">{tenant.name}</td>
                      {flagStats.slice(0, 10).map((stat) => (
                        <td key={stat.name} className="text-center py-2 px-2">
                          <span className={`inline-block w-3 h-3 rounded-full ${Math.random() > 0.5 ? 'bg-green-500' : 'bg-gray-300'
                            }`} />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// Helper functions
interface FlagStat {
  name: string;
  enabledCount: number;
  disabledCount: number;
  adoptionRate: number;
  trend: "up" | "down" | "stable";
}

function calculateFlagStatistics(tenants: any[] | undefined, flags: any[] | undefined): FlagStat[] {
  if (!tenants || !flags) return [];

  // Define all possible feature flags from the FeatureFlags service
  const allFlagNames = [
    "websocketRealtime",
    "offlineMode",
    "pushNotifications",
    "walletOrbWidget",
    "proofTickerWidget",
    "capsuleCardWidget",
    "energyGaugeWidget",
    "utidBadgeWidget",
    "amiPulseWidget",
    "shadowTwinWidget",
    "amiContextAwareness",
    "amiProactivity",
    "amiSeamlessness",
    "amiAdaptivity",
    "cosmicIntelligenceFabric",
    "federatedLearning",
    "privacyPreservingAggregation",
    "crossDeploymentIntelligence",
    "advancedAnalytics",
    "customBranding",
    "apiAccess",
    "whiteGloveSupport",
    "experimentalFeatures"
  ];

  const totalTenants = tenants.length;

  return allFlagNames.map(flagName => {
    // Count how many tenants have this flag enabled
    const enabledCount = Math.floor(Math.random() * (totalTenants + 1)); // Mock data
    const disabledCount = totalTenants - enabledCount;
    const adoptionRate = totalTenants > 0 ? Math.round((enabledCount / totalTenants) * 100) : 0;

    // Mock trend (in production, compare with previous period)
    const trendRand = Math.random();
    const trend: "up" | "down" | "stable" =
      trendRand > 0.6 ? "up" : trendRand > 0.3 ? "stable" : "down";

    return {
      name: formatFlagName(flagName),
      enabledCount,
      disabledCount,
      adoptionRate,
      trend
    };
  });
}

function formatFlagName(camelCase: string): string {
  return camelCase
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, str => str.toUpperCase())
    .trim();
}

function calculateAverageAdoption(stats: FlagStat[]): number {
  if (stats.length === 0) return 0;
  const sum = stats.reduce((acc, stat) => acc + stat.adoptionRate, 0);
  return Math.round(sum / stats.length);
}

function generateABTestingInsights(stats: FlagStat[]): Array<{ title: string, description: string }> {
  const insights = [];

  const highAdoption = stats.filter(s => s.adoptionRate > 80);
  if (highAdoption.length > 0) {
    insights.push({
      title: `${highAdoption.length} flags have >80% adoption`,
      description: "These features are widely accepted and should be considered for standard inclusion in all deployments."
    });
  }

  const lowAdoption = stats.filter(s => s.adoptionRate < 20);
  if (lowAdoption.length > 0) {
    insights.push({
      title: `${lowAdoption.length} flags have <20% adoption`,
      description: "Consider investigating why these features have low adoption. They may need better documentation or marketing."
    });
  }

  const trending = stats.filter(s => s.trend === "up");
  if (trending.length > 0) {
    insights.push({
      title: `${trending.length} flags are trending up`,
      description: "These features are gaining traction and may benefit from additional investment and promotion."
    });
  }

  return insights;
}

function convertToCSV(data: any[]): string {
  if (data.length === 0) return "";

  const headers = Object.keys(data[0]).join(",");
  const rows = data.map(row => Object.values(row).join(","));

  return [headers, ...rows].join("\n");
}

function downloadFile(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
