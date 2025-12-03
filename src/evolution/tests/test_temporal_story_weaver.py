import pytest
from src.evolution.temporal_story_weaver import TemporalStoryWeaver

def test_basic_flow():
    tsw = TemporalStoryWeaver()
    ex = [{"id":"e1","ts":1,"type":"INTERVENTION","diff":"a->b"}]
    hv = {"e1":{"novelty_score":0.8}}
    telem = [{"ts":2,"temperature":45}]
    record = tsw.sign_and_export(tsw.synthesize_narrative(tsw.causal_discovery(tsw.ingest(ex,hv,telem), tsw.discover_interventions(tsw.ingest(ex,hv,telem)))), {})
    assert "hash" in record
