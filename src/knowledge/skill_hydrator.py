"""
Skill Hydrator
Ingests public repositories, papers, patents and converts into internal capsules.
Integrates with catalog and sandbox validator.
"""

from typing import Dict, Any, List
import os
import uuid
import shutil

# placeholder for embedding / vector store integration
# from src.ml.embeddings import embed_document
# from src.sandbox.runner import SandboxRunner

class SkillHydrator:
    def __init__(self, catalog_store=None, sandbox_runner=None):
        self.catalog = catalog_store
        self.sandbox = sandbox_runner

    def ingest_github_repo(self, repo_url: str, owner:str=None) -> Dict[str,Any]:
        """
        Clone repo, detect language, tests, create capsule manifest.
        """
        # For this skeleton, we won't actually git clone; instead we create a capsule record.
        capsule_id = "capsule_" + uuid.uuid4().hex[:8]
        manifest = {
            "id": capsule_id,
            "source": repo_url,
            "type": "code",
            "owner": owner,
            "created": True,
            "trust_score": 0.5
        }
        # optionally run sandbox tests and update trust_score
        if self.sandbox:
            ok, results = self.sandbox.run_tests(repo_url)
            manifest["trust_score"] = 0.9 if ok else 0.3
            manifest["sandbox"] = results
        # write to catalog (if available)
        if self.catalog:
            self.catalog.put(manifest)
        return manifest

    def ingest_paper(self, paper_text: str, metadata: Dict[str,Any]) -> Dict[str,Any]:
        """
        Convert paper to vectorized knowledge and capsule entry.
        """
        capsule_id = "paper_" + uuid.uuid4().hex[:8]
        # embeddings = embed_document(paper_text)  # offload to ML infra
        manifest = {
            "id": capsule_id,
            "type": "paper",
            "metadata": metadata,
            "provenance": metadata.get("url"),
            "trust_score": 0.7
        }
        if self.catalog:
            self.catalog.put(manifest)
        return manifest

    def list_catalog(self):
        if not self.catalog:
            return []
        return self.catalog.list()
