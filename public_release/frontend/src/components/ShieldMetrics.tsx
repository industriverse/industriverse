import { useEffect, useState } from "react";

type ShieldMetricsState = {
  total_power_watts?: number;
  avg_temperature_c?: number;
  system_entropy?: number;
  node_count?: number;
};

export function ShieldMetrics() {
  const [metrics, setMetrics] = useState<ShieldMetricsState | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const resp = await fetch("/ws/pulse");
        // In a real implementation, this would use a websocket; here we fallback to GET shield state + heuristic
        const stateResp = await fetch("/v1/shield/state");
        if (!stateResp.ok) throw new Error("Failed to load shield metrics");
        const data = await stateResp.json();
        setMetrics(data.metrics || {});
      } catch (e: any) {
        setError(e.message);
      }
    };
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold">Thermo Metrics</h3>
        {error && <span className="text-xs text-red-400">{error}</span>}
      </div>
      <div className="text-xs space-y-1">
        {metrics ? (
          <>
            <div>Total Power: {metrics.total_power_watts ?? "n/a"} W</div>
            <div>Avg Temp: {metrics.avg_temperature_c ?? "n/a"} °C</div>
            <div>Entropy: {metrics.system_entropy ?? "n/a"}</div>
            <div>Nodes: {metrics.node_count ?? "n/a"}</div>
          </>
        ) : (
          <div className="text-muted-foreground">Loading...</div>
        )}
      </div>
    </div>
  );
}
