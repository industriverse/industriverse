import pytest
from src.marketing.narrative_feedback import NarrativeFeedback

def test_attention_scoring_and_mapping():
    nf = NarrativeFeedback({"vc":5.0,"default":1.0})
    raw = [{"id":"c1","ts":1,"impr":1000,"eng":10,"actor_type":"vc"}]
    norm = nf.normalize_signals(raw)
    scores = nf.score_attention(norm)
    mapping = {"c1":"exp1"}
    exp_scores = nf.map_to_experiments(mapping, scores)
    assert "exp1" in exp_scores
    recs = nf.produce_recommendations(exp_scores, {"exp1":0.3})
    assert recs[0]["experiment"] == "exp1"
