"""
Narrative Feedback Loop
Consumes social signals and maps them back to experiments and product priorities.
"""

from typing import Dict, Any, List
import statistics

class NarrativeFeedback:
    def __init__(self, stakeholder_weights: Dict[str,float]=None):
        # e.g., {"vc":5.0, "press":1.2, "peer_researcher":3.0}
        self.weights = stakeholder_weights or {"default":1.0}

    def normalize_signals(self, raw: List[Dict[str,Any]]) -> List[Dict[str,Any]]:
        """
        Convert raw social API payloads into normalized attention datapoints:
        {"content_id","timestamp","impressions","engagement","actor_type"}
        """
        normalized = []
        for r in raw:
            norm = {
                "content_id": r.get("id"),
                "ts": r.get("ts"),
                "impressions": int(r.get("impr",0)),
                "engagement": int(r.get("eng",0)),
                "actor_type": r.get("actor_type","default")
            }
            normalized.append(norm)
        return normalized

    def score_attention(self, normalized: List[Dict[str,Any]]) -> Dict[str, float]:
        """
        Return aggregated attention scores per content_id.
        attention = weighted_sum(engagement + impressions * alpha)
        """
        scores = {}
        for n in normalized:
            w = self.weights.get(n["actor_type"], self.weights.get("default",1.0))
            base = n["engagement"] + 0.01 * n["impressions"]
            score = base * w
            scores.setdefault(n["content_id"], 0.0)
            scores[n["content_id"]] += score
        return scores

    def map_to_experiments(self, content_map: Dict[str,str], attention_scores: Dict[str,float]) -> Dict[str,float]:
        """
        content_map: content_id -> experiment_id
        returns: experiment_id -> aggregated attention score
        """
        exp_scores = {}
        for content_id, score in attention_scores.items():
            exp_id = content_map.get(content_id)
            if not exp_id:
                continue
            exp_scores.setdefault(exp_id,0.0)
            exp_scores[exp_id] += score
        return exp_scores

    def produce_recommendations(self, exp_scores: Dict[str,float], hilbert_novelty: Dict[str,float]) -> List[Dict[str,Any]]:
        """
        Combine attention and novelty to rank experiments for budget allocation.
        """
        recs = []
        for exp, atn in exp_scores.items():
            nov = hilbert_novelty.get(exp, 0.0)
            score = atn * (1 + nov)
            recs.append({"experiment":exp,"attention":atn,"novelty":nov,"composite_score":score})
        return sorted(recs, key=lambda x: x["composite_score"], reverse=True)
