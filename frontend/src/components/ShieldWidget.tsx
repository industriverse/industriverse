import { useEffect, useState } from "react";

type ShieldState = {
  status: string;
  last_event_ts: number;
  metrics?: Record<string, any>;
  energy?: number;
};

export function ShieldWidget() {
  const [shield, setShield] = useState<ShieldState | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchShield = async () => {
      try {
        const resp = await fetch("/v1/shield/state");
        if (!resp.ok) throw new Error("Failed to load shield state");
        const data = await resp.json();
        setShield(data);
      } catch (e: any) {
        setError(e.message);
      }
    };
    fetchShield();
    const interval = setInterval(fetchShield, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold">Shield State</h3>
        {error && <span className="text-xs text-red-400">{error}</span>}
      </div>
      <div className="text-xs space-y-1">
        <div>Status: {shield?.status || "unknown"}</div>
        <div>Last Event: {shield?.last_event_ts ? new Date(shield.last_event_ts * 1000).toLocaleTimeString() : "n/a"}</div>
        {shield?.metrics && (
          <div className="space-y-1">
            {Object.entries(shield.metrics).map(([k, v]) => (
              <div key={k}>
                {k}: {String(v)}
              </div>
            ))}
          </div>
        )}
        {!shield && !error && <div className="text-muted-foreground">Loading shield state...</div>}
      </div>
    </div>
  );
}
