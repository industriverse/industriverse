"""
RDR (Real Deep Research) Engine

Paper ingestion, 6D thermodynamic embedding, and insight discovery system.
Enables deep research integration for the I³ (Industrial Internet of Intelligence) platform.

Key Mechanisms:
- Multi-source paper ingestion (arXiv, IEEE, ACM, Nature, Science)
- 6D thermodynamic embeddings combining semantic, temporal, and causal dimensions
- Knowledge graph construction with semantic relationships
- Insight discovery with confidence scoring
- Proof-of-Insight validation
- UTID (Universal Tokenized ID) generation for discoveries
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import hashlib
import json
import numpy as np
from collections import defaultdict


class PaperSource(Enum):
    """Research paper sources"""
    ARXIV = "arxiv"
    IEEE = "ieee"
    ACM = "acm"
    NATURE = "nature"
    SCIENCE = "science"
    CUSTOM = "custom"


class InsightType(Enum):
    """Types of discovered insights"""
    PATTERN = "pattern"  # Recurring patterns across papers
    ANOMALY = "anomaly"  # Unexpected findings
    CAUSALITY = "causality"  # Cause-effect relationships
    SYNTHESIS = "synthesis"  # Combined insights from multiple papers
    PREDICTION = "prediction"  # Future trend predictions
    CONTRADICTION = "contradiction"  # Conflicting claims


@dataclass
class Paper:
    """Research paper metadata"""
    paper_id: str
    title: str
    authors: List[str]
    abstract: str
    source: str
    url: str
    published_date: datetime

    # Content
    full_text: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    citations: int = 0

    # Processing
    ingested_at: datetime = field(default_factory=datetime.now)
    embedding_6d: Optional[np.ndarray] = None
    embedding_metadata: Dict[str, Any] = field(default_factory=dict)

    # Relationships
    cited_by: List[str] = field(default_factory=list)
    cites: List[str] = field(default_factory=list)
    related_papers: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'paper_id': self.paper_id,
            'title': self.title,
            'authors': self.authors,
            'abstract': self.abstract,
            'source': self.source,
            'url': self.url,
            'published_date': self.published_date.isoformat(),
            'keywords': self.keywords,
            'citations': self.citations,
            'ingested_at': self.ingested_at.isoformat(),
            'cited_by': self.cited_by,
            'cites': self.cites,
            'related_papers': self.related_papers,
        }


@dataclass
class Insight:
    """Discovered insight from research analysis"""
    insight_id: str
    insight_type: str
    text: str
    confidence: float  # 0.0 to 1.0

    # Source papers
    source_papers: List[str]

    # Proof-of-Insight
    proof_score: float = 0.0
    validated: bool = False
    validation_method: Optional[str] = None

    # UTID (Universal Tokenized ID)
    utid: Optional[str] = None

    # Discovery metadata
    discovered_at: datetime = field(default_factory=datetime.now)
    discovered_by: str = "rdr-engine"

    # Impact
    potential_impact: str = "unknown"  # low, medium, high, breakthrough
    applicability: List[str] = field(default_factory=list)

    # Relationships
    related_insights: List[str] = field(default_factory=list)
    contradicts: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'insight_id': self.insight_id,
            'insight_type': self.insight_type,
            'text': self.text,
            'confidence': self.confidence,
            'source_papers': self.source_papers,
            'proof_score': self.proof_score,
            'validated': self.validated,
            'validation_method': self.validation_method,
            'utid': self.utid,
            'discovered_at': self.discovered_at.isoformat(),
            'discovered_by': self.discovered_by,
            'potential_impact': self.potential_impact,
            'applicability': self.applicability,
            'related_insights': self.related_insights,
            'contradicts': self.contradicts,
        }


@dataclass
class Embedding6D:
    """
    6D Thermodynamic Embedding

    Combines multiple dimensions for rich semantic representation:
    1. Semantic: Core meaning and concepts
    2. Temporal: Time evolution and trends
    3. Causal: Cause-effect relationships
    4. Entropy: Information disorder/novelty
    5. Energy: Research "activation" or importance
    6. Momentum: Research velocity and direction
    """
    semantic: np.ndarray  # [768] - BERT-like semantic embedding
    temporal: float  # Time decay factor
    causal: np.ndarray  # [64] - Causal relationship encoding
    entropy: float  # Information novelty (0-1)
    energy: float  # Research importance score (0-1)
    momentum: np.ndarray  # [32] - Research direction vector

    def to_vector(self) -> np.ndarray:
        """Flatten to single vector for similarity computation"""
        return np.concatenate([
            self.semantic,
            [self.temporal],
            self.causal,
            [self.entropy, self.energy],
            self.momentum
        ])

    def similarity(self, other: 'Embedding6D') -> float:
        """Compute thermodynamic similarity between embeddings"""
        v1 = self.to_vector()
        v2 = other.to_vector()

        # Cosine similarity
        cos_sim = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

        # Weight by entropy and energy alignment
        entropy_factor = 1 - abs(self.entropy - other.entropy)
        energy_factor = 1 - abs(self.energy - other.energy)

        return cos_sim * 0.7 + entropy_factor * 0.15 + energy_factor * 0.15


class RDREngine:
    """
    Real Deep Research Engine

    Core mechanisms:
    1. Paper ingestion from multiple sources
    2. 6D thermodynamic embedding generation
    3. Knowledge graph construction
    4. Insight discovery and validation
    5. UTID generation for discoveries
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("./rdr_data")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Paper storage
        self.papers: Dict[str, Paper] = {}
        self.papers_by_source: Dict[str, List[str]] = defaultdict(list)

        # Insight storage
        self.insights: Dict[str, Insight] = {}
        self.insights_by_type: Dict[str, List[str]] = defaultdict(list)

        # Knowledge graph (adjacency list)
        self.knowledge_graph: Dict[str, Set[str]] = defaultdict(set)

        # Embedding index for fast similarity search
        self.embedding_index: List[Tuple[str, np.ndarray]] = []

    def ingest_paper(
        self,
        title: str,
        authors: List[str],
        abstract: str,
        source: PaperSource,
        url: str,
        published_date: datetime,
        full_text: Optional[str] = None,
        keywords: Optional[List[str]] = None
    ) -> Paper:
        """
        Ingest a research paper into RDR system

        Process:
        1. Create paper metadata
        2. Generate 6D embedding
        3. Add to knowledge graph
        4. Discover potential insights
        """
        # Generate paper ID
        paper_id = self._generate_paper_id(title, authors[0] if authors else "unknown")

        # Create paper object
        paper = Paper(
            paper_id=paper_id,
            title=title,
            authors=authors,
            abstract=abstract,
            source=source.value,
            url=url,
            published_date=published_date,
            full_text=full_text,
            keywords=keywords or []
        )

        # Generate 6D embedding
        paper.embedding_6d = self._generate_6d_embedding(paper)

        # Store paper
        self.papers[paper_id] = paper
        self.papers_by_source[source.value].append(paper_id)

        # Add to embedding index
        if paper.embedding_6d is not None:
            self.embedding_index.append((paper_id, paper.embedding_6d.to_vector()))

        # Update knowledge graph
        self._update_knowledge_graph(paper)

        # Discover insights
        self._discover_insights_from_paper(paper)

        # Save to storage
        self._save_paper(paper)

        return paper

    def _generate_6d_embedding(self, paper: Paper) -> Embedding6D:
        """
        Generate 6D thermodynamic embedding for paper

        Dimensions:
        1. Semantic: Extract from title + abstract using transformer model
        2. Temporal: Time decay based on publication date
        3. Causal: Extract cause-effect patterns from text
        4. Entropy: Measure information novelty
        5. Energy: Importance score (citations, keywords, venue)
        6. Momentum: Research trend direction
        """
        # 1. Semantic embedding (mock - in production use BERT/SciBERT)
        semantic = self._extract_semantic_embedding(paper.abstract)

        # 2. Temporal decay
        days_old = (datetime.now() - paper.published_date).days
        temporal = np.exp(-days_old / 365.0)  # Exponential decay over 1 year

        # 3. Causal relationships
        causal = self._extract_causal_patterns(paper.abstract)

        # 4. Entropy (novelty)
        entropy = self._compute_entropy(paper)

        # 5. Energy (importance)
        energy = self._compute_energy(paper)

        # 6. Momentum (research direction)
        momentum = self._compute_momentum(paper)

        return Embedding6D(
            semantic=semantic,
            temporal=temporal,
            causal=causal,
            entropy=entropy,
            energy=energy,
            momentum=momentum
        )

    def _extract_semantic_embedding(self, text: str) -> np.ndarray:
        """Extract semantic embedding from text"""
        # Mock implementation - in production use SciBERT or similar
        # For now, create a hash-based deterministic embedding
        hash_val = hashlib.sha256(text.encode()).digest()
        embedding = np.frombuffer(hash_val[:128], dtype=np.uint8).astype(float)
        # Normalize to 768 dimensions (BERT standard)
        embedding = np.tile(embedding, 6)[:768]
        return embedding / np.linalg.norm(embedding)

    def _extract_causal_patterns(self, text: str) -> np.ndarray:
        """Extract causal relationship patterns"""
        # Mock implementation - look for causal keywords
        causal_keywords = ['causes', 'leads to', 'results in', 'due to', 'because', 'therefore']

        embedding = np.zeros(64)
        for i, keyword in enumerate(causal_keywords):
            if keyword in text.lower():
                embedding[i % 64] += 1.0

        return embedding / (np.linalg.norm(embedding) + 1e-10)

    def _compute_entropy(self, paper: Paper) -> float:
        """
        Compute information entropy (novelty)

        High entropy = novel/unexpected research
        Low entropy = incremental/predictable research
        """
        # Check how different this paper is from existing corpus
        if not self.embedding_index:
            return 1.0  # First paper is novel

        # Mock: Use keyword uniqueness as proxy
        unique_keywords = set(paper.keywords)
        all_keywords = set()
        for p in self.papers.values():
            all_keywords.update(p.keywords)

        if not all_keywords:
            return 0.5

        novelty = len(unique_keywords - all_keywords) / max(len(unique_keywords), 1)
        return min(novelty, 1.0)

    def _compute_energy(self, paper: Paper) -> float:
        """
        Compute research energy (importance)

        Based on:
        - Citation count
        - Venue prestige
        - Author reputation
        - Keyword relevance
        """
        energy = 0.0

        # Citations (0-0.4)
        energy += min(paper.citations / 100.0, 0.4)

        # Source prestige (0-0.3)
        source_prestige = {
            'nature': 0.3,
            'science': 0.3,
            'arxiv': 0.2,
            'ieee': 0.25,
            'acm': 0.25,
        }
        energy += source_prestige.get(paper.source, 0.1)

        # Keyword relevance (0-0.3)
        key_terms = ['thermodynamic', 'quantum', 'ai', 'security', 'energy', 'entropy']
        keyword_score = sum(1 for k in paper.keywords if any(term in k.lower() for term in key_terms))
        energy += min(keyword_score / 10.0, 0.3)

        return min(energy, 1.0)

    def _compute_momentum(self, paper: Paper) -> np.ndarray:
        """
        Compute research momentum (direction)

        Represents the "direction" of research progress
        """
        # Mock: Create direction vector from keywords
        momentum = np.zeros(32)

        for i, keyword in enumerate(paper.keywords[:32]):
            hash_val = hash(keyword) % 32
            momentum[hash_val] += 1.0

        return momentum / (np.linalg.norm(momentum) + 1e-10)

    def _update_knowledge_graph(self, paper: Paper):
        """Update knowledge graph with paper relationships"""
        paper_id = paper.paper_id

        # Connect to papers with similar keywords
        for other_id, other_paper in self.papers.items():
            if other_id == paper_id:
                continue

            # Check keyword overlap
            common_keywords = set(paper.keywords) & set(other_paper.keywords)
            if len(common_keywords) >= 2:
                self.knowledge_graph[paper_id].add(other_id)
                self.knowledge_graph[other_id].add(paper_id)

                if other_id not in paper.related_papers:
                    paper.related_papers.append(other_id)

        # Connect to papers by same authors
        for other_id, other_paper in self.papers.items():
            if other_id == paper_id:
                continue

            common_authors = set(paper.authors) & set(other_paper.authors)
            if common_authors:
                self.knowledge_graph[paper_id].add(other_id)
                self.knowledge_graph[other_id].add(paper_id)

    def _discover_insights_from_paper(self, paper: Paper):
        """Discover insights by analyzing paper in context of corpus"""
        # Pattern discovery: Find recurring themes
        if len(self.papers) >= 5:
            self._discover_patterns(paper)

        # Anomaly detection: Find unexpected results
        self._discover_anomalies(paper)

        # Synthesis: Combine with existing papers
        if len(self.papers) >= 3:
            self._discover_synthesis(paper)

    def _discover_patterns(self, paper: Paper):
        """Discover recurring patterns"""
        # Find papers with similar keywords
        keyword_counts = defaultdict(int)
        for p in self.papers.values():
            for keyword in p.keywords:
                keyword_counts[keyword] += 1

        # Identify patterns (keywords appearing in >= 30% of papers)
        threshold = len(self.papers) * 0.3
        patterns = [k for k, count in keyword_counts.items() if count >= threshold]

        if patterns and any(k in paper.keywords for k in patterns):
            insight_text = f"Recurring pattern identified: {', '.join(patterns[:3])} appears across {len(self.papers)} papers"

            insight = self._create_insight(
                insight_type=InsightType.PATTERN,
                text=insight_text,
                source_papers=[paper.paper_id],
                confidence=0.7
            )

            self.insights[insight.insight_id] = insight
            self.insights_by_type[InsightType.PATTERN.value].append(insight.insight_id)

    def _discover_anomalies(self, paper: Paper):
        """Discover anomalous findings"""
        # Check if entropy is unusually high
        if paper.embedding_6d and paper.embedding_6d.entropy > 0.8:
            insight_text = f"Novel research direction identified in: {paper.title}"

            insight = self._create_insight(
                insight_type=InsightType.ANOMALY,
                text=insight_text,
                source_papers=[paper.paper_id],
                confidence=paper.embedding_6d.entropy
            )

            self.insights[insight.insight_id] = insight
            self.insights_by_type[InsightType.ANOMALY.value].append(insight.insight_id)

    def _discover_synthesis(self, paper: Paper):
        """Discover synthesis insights from multiple papers"""
        # Find most similar papers
        similar_papers = self.find_similar_papers(paper.paper_id, top_k=3)

        if len(similar_papers) >= 2:
            insight_text = f"Synthesis of findings from {len(similar_papers) + 1} papers suggests new connections"

            source_ids = [paper.paper_id] + [pid for pid, _ in similar_papers]

            insight = self._create_insight(
                insight_type=InsightType.SYNTHESIS,
                text=insight_text,
                source_papers=source_ids,
                confidence=0.75
            )

            self.insights[insight.insight_id] = insight
            self.insights_by_type[InsightType.SYNTHESIS.value].append(insight.insight_id)

    def _create_insight(
        self,
        insight_type: InsightType,
        text: str,
        source_papers: List[str],
        confidence: float
    ) -> Insight:
        """Create new insight with Proof-of-Insight validation"""
        insight_id = self._generate_insight_id(text)

        # Calculate Proof-of-Insight score
        proof_score = self._calculate_proof_of_insight(source_papers, confidence)

        # Generate UTID if proof score is high enough
        utid = None
        validated = False
        if proof_score >= 0.85:
            utid = self._generate_utid(insight_id, proof_score)
            validated = True

        # Determine impact
        impact = self._assess_impact(insight_type, confidence, len(source_papers))

        return Insight(
            insight_id=insight_id,
            insight_type=insight_type.value,
            text=text,
            confidence=confidence,
            source_papers=source_papers,
            proof_score=proof_score,
            validated=validated,
            validation_method="rdr-thermodynamic" if validated else None,
            utid=utid,
            potential_impact=impact
        )

    def _calculate_proof_of_insight(self, source_papers: List[str], confidence: float) -> float:
        """
        Calculate Proof-of-Insight score

        Based on:
        - Source paper energy (importance)
        - Number of confirming sources
        - Confidence score
        - Cross-validation across sources
        """
        if not source_papers:
            return 0.0

        # Average energy of source papers
        avg_energy = 0.0
        for paper_id in source_papers:
            paper = self.papers.get(paper_id)
            if paper and paper.embedding_6d:
                avg_energy += paper.embedding_6d.energy
        avg_energy /= len(source_papers)

        # Source count bonus (diminishing returns)
        source_bonus = min(len(source_papers) / 10.0, 0.3)

        # Combine factors
        proof_score = (avg_energy * 0.4) + (confidence * 0.4) + source_bonus

        return min(proof_score, 1.0)

    def _generate_utid(self, insight_id: str, proof_score: float) -> str:
        """
        Generate Universal Tokenized ID for validated insight

        Format: UTID-{timestamp}-{hash}-{proof}
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        hash_part = hashlib.sha256(insight_id.encode()).hexdigest()[:12]
        proof_part = f"{int(proof_score * 100):02d}"

        return f"UTID-{timestamp}-{hash_part}-{proof_part}"

    def _assess_impact(self, insight_type: InsightType, confidence: float, source_count: int) -> str:
        """Assess potential impact of insight"""
        score = confidence * 0.6 + min(source_count / 10.0, 0.4)

        if insight_type == InsightType.ANOMALY and score > 0.8:
            return "breakthrough"
        elif score >= 0.8:
            return "high"
        elif score >= 0.6:
            return "medium"
        else:
            return "low"

    def find_similar_papers(self, paper_id: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find most similar papers using 6D embeddings"""
        paper = self.papers.get(paper_id)
        if not paper or not paper.embedding_6d:
            return []

        similarities = []
        for other_id, other_paper in self.papers.items():
            if other_id == paper_id:
                continue

            if other_paper.embedding_6d:
                similarity = paper.embedding_6d.similarity(other_paper.embedding_6d)
                similarities.append((other_id, similarity))

        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def query_insights(
        self,
        insight_type: Optional[InsightType] = None,
        min_confidence: float = 0.0,
        validated_only: bool = False,
        min_impact: Optional[str] = None
    ) -> List[Insight]:
        """Query insights with filters"""
        results = []

        for insight in self.insights.values():
            # Filter by type
            if insight_type and insight.insight_type != insight_type.value:
                continue

            # Filter by confidence
            if insight.confidence < min_confidence:
                continue

            # Filter by validation
            if validated_only and not insight.validated:
                continue

            # Filter by impact
            if min_impact:
                impact_levels = ['low', 'medium', 'high', 'breakthrough']
                if impact_levels.index(insight.potential_impact) < impact_levels.index(min_impact):
                    continue

            results.append(insight)

        # Sort by confidence
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results

    def get_knowledge_subgraph(self, paper_id: str, depth: int = 2) -> Dict[str, Set[str]]:
        """Get subgraph around a paper up to specified depth"""
        subgraph = {}
        visited = set()
        queue = [(paper_id, 0)]

        while queue:
            current_id, current_depth = queue.pop(0)

            if current_id in visited or current_depth > depth:
                continue

            visited.add(current_id)
            neighbors = self.knowledge_graph.get(current_id, set())
            subgraph[current_id] = neighbors

            if current_depth < depth:
                for neighbor in neighbors:
                    queue.append((neighbor, current_depth + 1))

        return subgraph

    def _generate_paper_id(self, title: str, first_author: str) -> str:
        """Generate unique paper ID"""
        content = f"{title}:{first_author}".lower()
        hash_val = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"paper-{hash_val}"

    def _generate_insight_id(self, text: str) -> str:
        """Generate unique insight ID"""
        hash_val = hashlib.sha256(text.encode()).hexdigest()[:16]
        return f"insight-{hash_val}"

    def _save_paper(self, paper: Paper):
        """Save paper to storage"""
        paper_dir = self.storage_path / 'papers' / paper.source
        paper_dir.mkdir(parents=True, exist_ok=True)

        paper_file = paper_dir / f"{paper.paper_id}.json"

        # Don't save embedding numpy array to JSON
        data = paper.to_dict()

        with open(paper_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get_stats(self) -> Dict[str, Any]:
        """Get RDR engine statistics"""
        return {
            'total_papers': len(self.papers),
            'papers_by_source': {src: len(papers) for src, papers in self.papers_by_source.items()},
            'total_insights': len(self.insights),
            'insights_by_type': {itype: len(insights) for itype, insights in self.insights_by_type.items()},
            'validated_insights': sum(1 for i in self.insights.values() if i.validated),
            'utid_count': sum(1 for i in self.insights.values() if i.utid),
            'knowledge_graph_edges': sum(len(neighbors) for neighbors in self.knowledge_graph.values()) // 2,
        }


# Global RDR engine instance
_rdr_engine: Optional[RDREngine] = None


def get_rdr_engine(storage_path: Optional[Path] = None) -> RDREngine:
    """Get or create global RDR engine"""
    global _rdr_engine
    if _rdr_engine is None:
        _rdr_engine = RDREngine(storage_path)
    return _rdr_engine
