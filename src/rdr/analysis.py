import json
from collections import Counter
import numpy as np
from typing import List, Dict, Any

try:
    import networkx as nx
except ImportError:
    nx = None

try:
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    def cosine_similarity(a, b=None):
        a = np.array(a)
        if b is None:
            b = a
        else:
            b = np.array(b)
        norm_a = np.linalg.norm(a, axis=1, keepdims=True)
        norm_b = np.linalg.norm(b, axis=1, keepdims=True)
        return np.dot(a, b.T) / (norm_a * norm_b.T + 1e-9)

class PhysicsEmbeddingAnalysis:
    def __init__(self, llm_model):
        self.llm = llm_model
    
    def generate_domain_survey(self, cluster_keywords: Dict[int, str]) -> str:
        """Generate automated physics domain survey"""
        prompt = f"""
        Those are summarized keywords for physics research papers clustered 
        by abstract contents. Please create a comprehensive survey organized 
        into major categories and sub-categories.
        
        Cluster Keywords:
        {json.dumps(cluster_keywords, indent=2)}
        
        Generate structured survey with citations.
        """
        
        if hasattr(self.llm, 'generate'):
            survey = self.llm.generate(prompt, max_tokens=4000)
        else:
            survey = "# Automated Physics Survey\n\n## 1. Plasma Physics\n..."
            
        return survey
    
    def analyze_trends_over_time(self, papers_with_clusters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Track research trends over time"""
        trends = {}
        
        # Mock year range
        for year in range(2020, 2026):
            year_papers = [p for p in papers_with_clusters if p.get('year') == year]
            cluster_counts = Counter([p.get('cluster') for p in year_papers])
            trends[year] = dict(cluster_counts)
        
        # Identify rising vs declining topics (Mock logic)
        rising_topics = ["MHD", "Machine Learning"]
        declining_topics = ["Classical Mechanics"]
        
        return {
            'trends': trends,
            'rising': rising_topics,
            'declining': declining_topics
        }
    
    def build_knowledge_graph(self, papers_with_embeddings: List[Dict[str, Any]]) -> Any:
        """Build cross-domain knowledge graph"""
        if nx is None or cosine_similarity is None:
            return "NetworkX or sklearn not installed"

        G = nx.Graph()
        
        # Add nodes (papers as topic clusters)
        for paper in papers_with_embeddings:
            G.add_node(paper['id'], 
                      cluster=paper.get('cluster'),
                      keywords=paper.get('keywords', []))
        
        # Add edges (semantic similarity > threshold)
        # Simplified: just connect adjacent for demo if list is long
        # Real impl: O(N^2) comparison
        embeddings = [p['embedding'] for p in papers_with_embeddings]
        if len(embeddings) > 0:
            sim_matrix = cosine_similarity(embeddings)
            rows, cols = np.where(sim_matrix > 0.7)
            for r, c in zip(rows, cols):
                if r < c:
                    G.add_edge(papers_with_embeddings[r]['id'], papers_with_embeddings[c]['id'], weight=sim_matrix[r, c])
        
        return G
    
    def semantic_retrieval(self, query: str, papers_with_embeddings: List[Dict[str, Any]], embedding_model, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve most relevant papers for a query"""
        if cosine_similarity is None:
            return []

        if hasattr(embedding_model, 'encode'):
            query_embedding = embedding_model.encode(query)
        else:
            query_embedding = np.random.rand(768).astype(np.float32)
        
        similarities = []
        for paper in papers_with_embeddings:
            sim = cosine_similarity([query_embedding], [paper['embedding']])[0][0]
            similarities.append((paper, sim))
        
        # Sort by similarity and return top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [p[0] for p in similarities[:top_k]]
