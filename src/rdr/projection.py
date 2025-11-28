import numpy as np
from typing import List, Dict, Any

class PhysicsContentProjection:
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model  # e.g. nvidia/NV-Embed-v2 wrapper
    
    def project_to_embedding_space(self, papers_with_perspectives: List[Dict[str, Any]]) -> np.ndarray:
        """Project physics perspectives into embedding space"""
        embeddings = []
        
        for paper in papers_with_perspectives:
            # Concatenate all 6 perspectives
            p = paper.get('perspectives', {})
            text = " ".join([
                f"Observable: {p.get('Observable', '')}",
                f"Phenomenon: {p.get('Phenomenon', '')}",
                f"Mechanism: {p.get('Mechanism', '')}",
                f"Scale: {p.get('Scale', '')}",
                f"Method: {p.get('Method', '')}",
                f"Application: {p.get('Application', '')}"
            ])
            
            # Embed
            if hasattr(self.embedding_model, 'encode'):
                embedding = self.embedding_model.encode(text)
            else:
                # Mock embedding
                embedding = np.random.rand(768).astype(np.float32)
                
            embeddings.append(embedding)
        
        return np.array(embeddings)
    
    def cluster_embeddings(self, embeddings: np.ndarray, papers_with_perspectives: List[Dict[str, Any]], n_clusters: int = 5) -> Dict[str, Any]:
        """Cluster physics papers by embedding similarity"""
        try:
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(embeddings)
        except ImportError:
            print("sklearn not found, using mock clustering")
            cluster_labels = np.random.randint(0, n_clusters, size=len(embeddings))
        
        # Extract keywords for each cluster (Mock extraction for now)
        cluster_keywords = {}
        for cluster_id in range(n_clusters):
            # In real impl, we'd sample papers and ask LLM for keywords
            cluster_keywords[cluster_id] = f"Cluster {cluster_id} Keywords"
        
        return {
            'cluster_labels': cluster_labels,
            'cluster_keywords': cluster_keywords
        }
