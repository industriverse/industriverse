import { useEffect, useState } from "react";

type Proof = {
  proof_id: string;
  utid: string;
  domain: string;
  metadata: Record<string, any>;
  anchors?: { chain?: string; tx?: string }[];
};

const fallbackProofs: Proof[] = [
  { proof_id: "proof-mock-1", utid: "UTID:REAL:mock", domain: "general", metadata: { energy_joules: 12.3, status: "mock" } },
  { proof_id: "proof-mock-2", utid: "UTID:REAL:mock2", domain: "general", metadata: { energy_joules: 5.1, status: "mock" } },
];

export function ProofWidget() {
  const [proofs, setProofs] = useState<Proof[]>(fallbackProofs);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProofs = async () => {
      try {
        const resp = await fetch("/v1/proofs?limit=5");
        if (!resp.ok) throw new Error("Failed to load proofs");
        const data = await resp.json();
        setProofs(data);
      } catch (e: any) {
        setError(e.message);
      }
    };
    fetchProofs();
  }, []);

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold">Latest Proofs</h3>
        {error && <span className="text-xs text-red-400">{error}</span>}
      </div>
      <div className="space-y-2">
        {proofs.map((p) => (
          <div key={p.proof_id} className="text-xs border border-border/50 rounded p-2">
            <div className="font-mono">{p.proof_id}</div>
            <div className="text-muted-foreground">UTID: {p.utid}</div>
            <div className="flex gap-2">
              <span>Status: {p.metadata?.status || "unknown"}</span>
              {p.metadata?.energy_joules && <span>Energy: {p.metadata.energy_joules} J</span>}
              {p.metadata?.proof_score && <span>Score: {p.metadata.proof_score}</span>}
            </div>
            {p.metadata?.anchors && p.metadata.anchors.length > 0 && (
              <div className="mt-1">
                Anchors:
                {p.metadata.anchors.map((a: any, idx: number) => (
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
