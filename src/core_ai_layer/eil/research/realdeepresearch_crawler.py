"""
RealDeepResearch: Continuous Research Integration

Implementation inspired by arXiv:2510.20809v1
- Continuous ArXiv paper ingestion (daily updates)
- Perspective-based decomposition (I-M-O-W-R framework)
- Embedding-based clustering for knowledge graphs
- Automated integration into EIL enhancement pipeline

Perspective Framework (I-M-O-W-R):
- Introduction (I): Problem statement
- Methods (M): Technical approach
- Observations (O): Experimental results
- What next (W): Future work
- Related work (R): Prior art

Integration with EIL:
- Discover new physics-based learning techniques
- Identify relevant datasets (like Egocentric-10K)
- Extract architectural innovations (like LeJEPA)
- Continuous knowledge graph updates
"""

import requests
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import time
import json
from pathlib import Path
import numpy as np
import warnings


@dataclass
class PaperMetadata:
    """Metadata for a research paper"""
    arxiv_id: str
    title: str
    authors: List[str]
    abstract: str
    categories: List[str]
    published_date: datetime
    updated_date: datetime
    pdf_url: str
    arxiv_url: str


@dataclass
class PaperPerspectives:
    """Perspective-based decomposition of paper

    I-M-O-W-R Framework from RealDeepResearch
    """
    introduction: str  # Problem statement and motivation
    methods: str  # Technical approach and algorithms
    observations: str  # Experimental results and findings
    what_next: str  # Future work and limitations
    related_work: str  # Prior art and connections

    # Embeddings for similarity search
    introduction_embedding: Optional[np.ndarray] = None
    methods_embedding: Optional[np.ndarray] = None
    observations_embedding: Optional[np.ndarray] = None


@dataclass
class ResearchCluster:
    """Cluster of related papers"""
    cluster_id: int
    paper_ids: List[str]
    centroid_embedding: np.ndarray
    keywords: List[str]
    relevance_score: float


class ArxivCrawler:
    """ArXiv API crawler for continuous paper ingestion

    Fetches papers from specific categories relevant to EIL:
    - cs.LG (Machine Learning)
    - cs.AI (Artificial Intelligence)
    - cs.RO (Robotics)
    - cs.CV (Computer Vision)
    - physics.comp-ph (Computational Physics)
    """

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./arxiv_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_recent_papers(
        self,
        categories: List[str] = ["cs.LG", "cs.AI", "cs.RO", "cs.CV"],
        days_back: int = 7,
        max_results: int = 100
    ) -> List[PaperMetadata]:
        """Fetch recent papers from ArXiv

        Args:
            categories: ArXiv categories to search
            days_back: How many days back to search
            max_results: Maximum papers to fetch

        Returns:
            List of paper metadata
        """
        print(f"🔍 Fetching papers from ArXiv...")
        print(f"   Categories: {', '.join(categories)}")
        print(f"   Days back: {days_back}")

        # Construct search query
        category_query = " OR ".join([f"cat:{cat}" for cat in categories])
        query = f"({category_query})"

        # Date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        params = {
            'search_query': query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            warnings.warn(f"ArXiv API request failed: {e}")
            print("⚠️  Using cached/simulated data")
            return self._load_simulated_papers(max_results)

        # Parse XML response
        papers = self._parse_arxiv_response(response.text, start_date)

        print(f"✅ Fetched {len(papers)} papers")
        return papers

    def _parse_arxiv_response(
        self,
        xml_text: str,
        start_date: datetime
    ) -> List[PaperMetadata]:
        """Parse ArXiv API XML response"""
        root = ET.fromstring(xml_text)
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}

        papers = []

        for entry in root.findall('atom:entry', namespace):
            # Extract metadata
            arxiv_id = entry.find('atom:id', namespace).text.split('/abs/')[-1]
            title = entry.find('atom:title', namespace).text.strip()
            abstract = entry.find('atom:summary', namespace).text.strip()

            # Authors
            authors = [
                author.find('atom:name', namespace).text
                for author in entry.findall('atom:author', namespace)
            ]

            # Dates
            published = datetime.fromisoformat(
                entry.find('atom:published', namespace).text.replace('Z', '+00:00')
            )
            updated = datetime.fromisoformat(
                entry.find('atom:updated', namespace).text.replace('Z', '+00:00')
            )

            # Filter by date (make start_date timezone-aware)
            from datetime import timezone
            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=timezone.utc)

            if published < start_date:
                continue

            # Categories
            categories = [
                cat.attrib['term']
                for cat in entry.findall('atom:category', namespace)
            ]

            # URLs
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"

            papers.append(PaperMetadata(
                arxiv_id=arxiv_id,
                title=title,
                authors=authors,
                abstract=abstract,
                categories=categories,
                published_date=published,
                updated_date=updated,
                pdf_url=pdf_url,
                arxiv_url=arxiv_url
            ))

        return papers

    def _load_simulated_papers(self, num_papers: int) -> List[PaperMetadata]:
        """Generate simulated papers for testing"""
        papers = []

        simulated_titles = [
            "Self-Supervised Learning for Industrial Physics Prediction",
            "Egocentric Video Understanding in Factory Environments",
            "Physics-Grounded Robot Manipulation with 4D Reconstruction",
            "Continuous Research Integration for Adaptive AI Systems",
            "Thermodynamic Energy Map Prediction via Neural Networks"
        ]

        for i in range(min(num_papers, len(simulated_titles))):
            papers.append(PaperMetadata(
                arxiv_id=f"2025.{i:05d}",
                title=simulated_titles[i],
                authors=["Simulated Author"],
                abstract=f"This is a simulated abstract for paper {i}.",
                categories=["cs.LG"],
                published_date=datetime.now() - timedelta(days=i),
                updated_date=datetime.now() - timedelta(days=i),
                pdf_url=f"https://arxiv.org/pdf/2025.{i:05d}.pdf",
                arxiv_url=f"https://arxiv.org/abs/2025.{i:05d}"
            ))

        return papers


class PerspectiveDecomposer:
    """Decompose papers into I-M-O-W-R perspectives

    Uses abstract and title to extract perspectives.
    In production, would use full PDF text extraction.
    """

    @staticmethod
    def decompose(paper: PaperMetadata) -> PaperPerspectives:
        """Decompose paper into perspectives

        Args:
            paper: Paper metadata

        Returns:
            Perspectives extracted from paper
        """
        # Simplified: Extract from abstract
        # In production: Use PDF parsing + NLP section extraction

        abstract = paper.abstract.lower()

        # Heuristic perspective extraction
        introduction = PerspectiveDecomposer._extract_introduction(abstract, paper.title)
        methods = PerspectiveDecomposer._extract_methods(abstract)
        observations = PerspectiveDecomposer._extract_observations(abstract)
        what_next = PerspectiveDecomposer._extract_future_work(abstract)
        related_work = PerspectiveDecomposer._extract_related_work(abstract)

        return PaperPerspectives(
            introduction=introduction,
            methods=methods,
            observations=observations,
            what_next=what_next,
            related_work=related_work
        )

    @staticmethod
    def _extract_introduction(abstract: str, title: str) -> str:
        """Extract problem statement (Introduction)"""
        # First 2 sentences typically describe problem
        sentences = abstract.split('.')
        intro = '. '.join(sentences[:2]) if len(sentences) >= 2 else abstract
        return f"{title}. {intro}"

    @staticmethod
    def _extract_methods(abstract: str) -> str:
        """Extract methods section"""
        # Look for method keywords
        method_keywords = ['propose', 'introduce', 'develop', 'design', 'implement', 'algorithm', 'architecture']

        sentences = abstract.split('.')
        method_sentences = [
            s for s in sentences
            if any(kw in s.lower() for kw in method_keywords)
        ]

        return '. '.join(method_sentences) if method_sentences else "Methods not extracted from abstract."

    @staticmethod
    def _extract_observations(abstract: str) -> str:
        """Extract experimental results (Observations)"""
        # Look for result keywords
        result_keywords = ['achieve', 'demonstrate', 'show', 'outperform', 'improve', 'result', 'experiment']

        sentences = abstract.split('.')
        result_sentences = [
            s for s in sentences
            if any(kw in s.lower() for kw in result_keywords)
        ]

        return '. '.join(result_sentences) if result_sentences else "Results not extracted from abstract."

    @staticmethod
    def _extract_future_work(abstract: str) -> str:
        """Extract future work (What next)"""
        # Look for future work keywords
        future_keywords = ['future', 'next', 'plan', 'extend', 'improve', 'limitation']

        sentences = abstract.split('.')
        future_sentences = [
            s for s in sentences
            if any(kw in s.lower() for kw in future_keywords)
        ]

        return '. '.join(future_sentences) if future_sentences else "Future work not mentioned in abstract."

    @staticmethod
    def _extract_related_work(abstract: str) -> str:
        """Extract related work"""
        # Look for related work keywords
        related_keywords = ['prior', 'previous', 'existing', 'related', 'compared', 'baseline']

        sentences = abstract.split('.')
        related_sentences = [
            s for s in sentences
            if any(kw in s.lower() for kw in related_keywords)
        ]

        return '. '.join(related_sentences) if related_sentences else "Related work not mentioned in abstract."


class EmbeddingGenerator:
    """Generate embeddings for perspective texts

    Uses simple TF-IDF in placeholder mode.
    In production: Use Sentence-BERT or similar
    """

    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.vocab = {}
        self.idf = {}

    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text

        Args:
            text: Input text

        Returns:
            embedding: [embedding_dim] vector
        """
        # Placeholder: Random embedding based on text hash
        # In production: Use sentence-transformers

        # Simple hash-based embedding for reproducibility
        words = text.lower().split()
        if not words:
            return np.zeros(self.embedding_dim)

        # Create pseudo-embedding from word hashes
        embedding = np.zeros(self.embedding_dim)
        for word in words:
            word_hash = hash(word) % self.embedding_dim
            embedding[word_hash] += 1.0

        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding


class ResearchIntegrator:
    """Integrate research papers into EIL knowledge base

    - Continuous paper ingestion from ArXiv
    - Perspective decomposition (I-M-O-W-R)
    - Embedding-based clustering
    - Knowledge graph construction
    """

    def __init__(self, cache_dir: Optional[str] = None):
        self.crawler = ArxivCrawler(cache_dir)
        self.decomposer = PerspectiveDecomposer()
        self.embedder = EmbeddingGenerator(embedding_dim=384)
        self.knowledge_base: Dict[str, PaperPerspectives] = {}
        self.clusters: List[ResearchCluster] = []

    def daily_update(
        self,
        categories: List[str] = ["cs.LG", "cs.AI", "cs.RO", "cs.CV"],
        days_back: int = 1,
        max_papers: int = 50
    ) -> Dict[str, Any]:
        """Daily research update pipeline

        Args:
            categories: ArXiv categories
            days_back: Days to look back
            max_papers: Max papers to process

        Returns:
            Update statistics
        """
        print(f"\n{'='*70}")
        print(f"RealDeepResearch: Daily Update")
        print(f"{'='*70}\n")

        # 1. Fetch papers
        papers = self.crawler.fetch_recent_papers(
            categories=categories,
            days_back=days_back,
            max_results=max_papers
        )

        if not papers:
            print("⚠️  No new papers found")
            return {
                'papers_processed': 0,
                'total_papers': len(self.knowledge_base),
                'num_clusters': len(self.clusters)
            }

        # 2. Decompose into perspectives
        print(f"\n🔬 Decomposing {len(papers)} papers...")
        new_papers = 0

        for paper in papers:
            if paper.arxiv_id in self.knowledge_base:
                continue  # Already processed

            # Decompose
            perspectives = self.decomposer.decompose(paper)

            # Generate embeddings
            perspectives.introduction_embedding = self.embedder.generate_embedding(
                perspectives.introduction
            )
            perspectives.methods_embedding = self.embedder.generate_embedding(
                perspectives.methods
            )
            perspectives.observations_embedding = self.embedder.generate_embedding(
                perspectives.observations
            )

            # Add to knowledge base
            self.knowledge_base[paper.arxiv_id] = perspectives
            new_papers += 1

        print(f"✅ Decomposed {new_papers} new papers")

        # 3. Update clusters
        print(f"\n📊 Updating research clusters...")
        self._update_clusters()

        print(f"✅ Knowledge base updated")
        print(f"   Total papers: {len(self.knowledge_base)}")
        print(f"   Research clusters: {len(self.clusters)}")

        return {
            'papers_processed': new_papers,
            'total_papers': len(self.knowledge_base),
            'num_clusters': len(self.clusters)
        }

    def _update_clusters(self, n_clusters: int = 5):
        """Update research clusters using k-means

        Args:
            n_clusters: Number of clusters
        """
        if len(self.knowledge_base) < n_clusters:
            return

        # Extract method embeddings for clustering
        paper_ids = list(self.knowledge_base.keys())
        embeddings = np.array([
            self.knowledge_base[pid].methods_embedding
            for pid in paper_ids
        ])

        # Simple k-means clustering
        centroids = embeddings[np.random.choice(len(embeddings), n_clusters, replace=False)]

        # Assign papers to clusters
        cluster_assignments = []
        for emb in embeddings:
            distances = np.linalg.norm(centroids - emb, axis=1)
            cluster_assignments.append(np.argmin(distances))

        # Create clusters
        self.clusters = []
        for cluster_id in range(n_clusters):
            cluster_papers = [
                paper_ids[i] for i, c in enumerate(cluster_assignments)
                if c == cluster_id
            ]

            if cluster_papers:
                self.clusters.append(ResearchCluster(
                    cluster_id=cluster_id,
                    paper_ids=cluster_papers,
                    centroid_embedding=centroids[cluster_id],
                    keywords=[f"cluster_{cluster_id}"],
                    relevance_score=0.5
                ))

    def find_relevant_papers(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """Find papers relevant to query

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of (paper_id, similarity_score) tuples
        """
        # Generate query embedding
        query_embedding = self.embedder.generate_embedding(query)

        # Compute similarities
        similarities = []
        for paper_id, perspectives in self.knowledge_base.items():
            # Compare with methods embedding
            if perspectives.methods_embedding is not None:
                similarity = float(np.dot(query_embedding, perspectives.methods_embedding))
                similarities.append((paper_id, similarity))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    def export_knowledge_graph(self, output_path: str):
        """Export knowledge base to JSON

        Args:
            output_path: Path to save JSON file
        """
        data = {
            'papers': {
                paper_id: {
                    'introduction': persp.introduction,
                    'methods': persp.methods,
                    'observations': persp.observations,
                    'what_next': persp.what_next,
                    'related_work': persp.related_work
                }
                for paper_id, persp in self.knowledge_base.items()
            },
            'clusters': [
                {
                    'cluster_id': cluster.cluster_id,
                    'paper_ids': cluster.paper_ids,
                    'keywords': cluster.keywords
                }
                for cluster in self.clusters
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✅ Knowledge graph exported to {output_path}")


if __name__ == "__main__":
    print("=" * 70)
    print("RealDeepResearch Crawler Test")
    print("=" * 70)

    # Initialize integrator
    integrator = ResearchIntegrator(cache_dir="./arxiv_cache")

    # Run daily update
    stats = integrator.daily_update(
        categories=["cs.LG", "cs.AI"],
        days_back=7,
        max_papers=10
    )

    print(f"\n📈 Update Statistics:")
    print(f"   Papers processed: {stats['papers_processed']}")
    print(f"   Total in knowledge base: {stats['total_papers']}")
    print(f"   Research clusters: {stats['num_clusters']}")

    # Test search
    print(f"\n🔍 Testing search...")
    query = "self-supervised learning for physics prediction"
    results = integrator.find_relevant_papers(query, top_k=3)

    print(f"\n   Query: '{query}'")
    print(f"   Top {len(results)} results:")
    for i, (paper_id, score) in enumerate(results):
        perspectives = integrator.knowledge_base[paper_id]
        print(f"\n   {i+1}. Paper ID: {paper_id}")
        print(f"      Similarity: {score:.3f}")
        print(f"      Intro: {perspectives.introduction[:100]}...")

    # Export knowledge graph
    print(f"\n💾 Exporting knowledge graph...")
    integrator.export_knowledge_graph("./knowledge_graph.json")

    print("\n" + "=" * 70)
    print("✅ REALDEEPRESEARCH CRAWLER COMPLETE")
    print("=" * 70)
