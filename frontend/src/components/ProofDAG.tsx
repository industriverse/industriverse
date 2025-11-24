import { useEffect, useState } from "react";

type ProofNode = {
  id: string;
  utid: string;
  status?: string;
  energy?: number;
  anchors?: { chain?: string; tx?: string }[];
};

export function ProofDAG() {
  const [nodes, setNodes] = useState<ProofNode[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProofs = async () => {
      try {
        const resp = await fetch("/v1/proofs?limit=10");
        if (!resp.ok) throw new Error("Failed to load proofs");
        const data = await resp.json();
        const mapped = data.map((p: any) => ({
          id: p.proof_id,
          utid: p.utid,
          status: p.metadata?.status,
          energy: p.metadata?.energy_joules,
          anchors: p.metadata?.anchors,
        }));
        setNodes(mapped);
      } catch (e: any) {
        setError(e.message);
      }
    };
    fetchProofs();
  }, []);

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold">Proof DAG</h3>
        {error && <span className="text-xs text-red-400">{error}</span>}
      </div>
      <div className="text-xs space-y-2">
        {nodes.map((n) => (
          <div key={n.id} className="border border-border/50 rounded p-2">
            <div className="font-mono">{n.id}</div>
            <div className="text-muted-foreground">UTID: {n.utid}</div>
            <div className="flex gap-2">
              <span>Status: {n.status || "unknown"}</span>
              {n.energy && <span>Energy: {n.energy} J</span>}
            </div>
            {n.anchors && n.anchors.length > 0 && (
              <div className="mt-1">
                Anchors:
                {n.anchors.map((a, idx) => (
                  <div key={idx} className="text-muted-foreground">
                    {a.chain}:{a.tx}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
