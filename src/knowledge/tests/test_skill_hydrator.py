import pytest
from src.knowledge.skill_hydrator import SkillHydrator

class DummyCatalog:
    def __init__(self): self._l = []
    def put(self, x): self._l.append(x)
    def list(self): return self._l

class DummySandbox:
    def run_tests(self, repo_url):
        return (True, {"tests":"ok"})

def test_ingest_repo_and_paper():
    cat = DummyCatalog()
    sd = DummySandbox()
    sh = SkillHydrator(catalog_store=cat, sandbox_runner=sd)
    r = sh.ingest_github_repo("https://github.com/example/repo", owner="alice")
    p = sh.ingest_paper("abstract text", {"url":"http://paper"})
    assert r["id"].startswith("capsule_")
    assert p["id"].startswith("paper_")
    assert len(cat.list()) == 2
