import { useEffect, useState } from "react";

type ProofEdge = {
  from: string;
  to: string;
  description?: string;
};

type ProofNode = {
  id: string;
  utid: string;
  status?: string;
};

export function ProofLineage() {
  const [nodes, setNodes] = useState<ProofNode[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [edges, setEdges] = useState<ProofEdge[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchProofs = async () => {
      try {
        setLoading(true);
        const resp = await fetch("/v1/proofs?limit=20");
        if (!resp.ok) throw new Error("Failed to load proofs");
        const data = await resp.json();
        const mapped = data.map((p: any) => ({
          id: p.proof_id,
          utid: p.utid,
          status: p.metadata?.status,
        }));
        setNodes(mapped);
        const edgeResp = await fetch("/v1/proofs/lineage");
        if (edgeResp.ok) {
          const edgeData = await edgeResp.json();
          setEdges(edgeData);
        }
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };
    fetchProofs();
  }, []);

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold">Proof Lineage</h3>
        {error && <span className="text-xs text-red-400">{error}</span>}
      </div>
      <div className="text-xs space-y-2">
        {loading && <div className="text-muted-foreground">Loading...</div>}
        {nodes.map((n) => (
          <div key={n.id} className="border border-border/50 rounded p-2">
            <div className="font-mono">{n.id}</div>
            <div className="text-muted-foreground">UTID: {n.utid}</div>
            <div>Status: {n.status || "unknown"}</div>
            <div className="mt-1">Edges:</div>
            {(n.id && edges.filter((e) => e.from === n.id || e.to === n.id)).map((e, idx) => (
              <div key={idx} className="text-muted-foreground">
                {e.from} → {e.to} {e.description ? `(${e.description})` : ""}
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
