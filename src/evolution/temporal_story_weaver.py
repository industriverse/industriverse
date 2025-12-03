"""
Temporal Story Weaver
Creates causal narratives from experiments, Hilbert metrics, telemetry & logs.
Outputs: JSON causal graph, markdown narrative, slide snippets.
"""

from typing import List, Dict, Any
import json
import hashlib
import datetime

# NOTE: integrate your BlackBox validation and Hilbert metrics imports
# from src.evolution.hilbert_metrics import HilbertVector
# from src.security.black_box import BlackBox

class TemporalStoryWeaver:
    def __init__(self, blackbox=None):
        """
        blackbox: optional BlackBox instance for provenance & hash anchoring.
        """
        self.blackbox = blackbox

    def ingest(self, experiment_logs: List[Dict[str, Any]], hilbert_vectors: Dict[str, Any], telemetry: List[Dict[str,Any]]) -> Dict[str,Any]:
        """
        Align timelines and preprocess inputs.
        Returns internal canonical representation.
        """
        # simple alignment by timestamp
        aligned = {
            "experiments": sorted(experiment_logs, key=lambda x: x.get("ts", 0)),
            "hilbert": hilbert_vectors,
            "telemetry": sorted(telemetry, key=lambda x: x.get("ts", 0))
        }
        return aligned

    def discover_interventions(self, aligned: Dict[str,Any]) -> List[Dict[str,Any]]:
        """
        Detect discrete interventions in experiments (parameter flips, deploys).
        Returns list of events with ts, event_type, payload.
        """
        events = []
        for e in aligned["experiments"]:
            # heuristics: look for 'change' markers or config diffs
            if e.get("type") in ("INTERVENTION","CONFIG_CHANGE") or "diff" in e:
                events.append({
                    "ts": e.get("ts"),
                    "id": e.get("id"),
                    "type": e.get("type","INTERVENTION"),
                    "payload": e
                })
        return events

    def causal_discovery(self, aligned: Dict[str,Any], interventions: List[Dict[str,Any]]) -> Dict[str,Any]:
        """
        Minimal causal discovery: pairwise influence scoring using transfer entropy placeholder
        (replace with proper TI/Granger or information-theoretic methods).
        Returns graph: nodes, edges with confidence score.
        """
        # placeholder simple correlational logic
        nodes = []
        edges = []
        for i,event in enumerate(interventions):
            nodes.append({"id": event["id"], "ts": event["ts"], "payload": event["payload"]})
            # naive correlation to hilbert magnitude change
            hv = aligned["hilbert"].get(event["id"], {})
            score = float(hv.get("novelty_score", 0.0))
            # create a synthetic edge to the most-changed metric
            edges.append({"from": event["id"], "to": "hilbert_novelty", "score": score})
        graph = {"nodes": nodes, "edges": edges}
        return graph

    def synthesize_narrative(self, graph: Dict[str,Any], audience: str = "investor") -> Dict[str,Any]:
        """
        Produce english narrative and slide bullet points.
        """
        # simple templating; will be swapped for LLM in production with references
        intro = "Summary of experiments"
        bullets = []
        for e in graph["edges"]:
            bullets.append(f"Intervention {e['from']} -> effect {e['to']} (score={e['score']:.3f})")
        narrative = {
            "title": f"Experiment Narrative ({datetime.datetime.utcnow().isoformat()})",
            "audience": audience,
            "intro": intro,
            "bullets": bullets,
            "confidence": sum([x["score"] for x in graph["edges"]]) / (len(graph["edges"]) if graph["edges"] else 1)
        }
        return narrative

    def sign_and_export(self, narrative: Dict[str,Any], graph: Dict[str,Any]) -> Dict[str,Any]:
        """
        Attach provenance hash and (optionally) write to blackbox.
        """
        payload = json.dumps({"narrative": narrative, "graph": graph}, sort_keys=True).encode("utf-8")
        h = hashlib.sha256(payload).hexdigest()
        record = {"hash": h, "narrative": narrative, "graph": graph}
        if self.blackbox:
            self.blackbox.log_event("story_weaver_export", record)
        return record

# Simple CLI utility function
def generate_story(experiment_logs, hilbert_vectors, telemetry, blackbox=None):
    tsw = TemporalStoryWeaver(blackbox=blackbox)
    aligned = tsw.ingest(experiment_logs, hilbert_vectors, telemetry)
    interventions = tsw.discover_interventions(aligned)
    graph = tsw.causal_discovery(aligned, interventions)
    narrative = tsw.synthesize_narrative(graph)
    return tsw.sign_and_export(narrative, graph)
