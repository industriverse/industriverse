import numpy as np
from typing import List, Dict
from .rco import ResourceClusterObject

# Try to import sklearn
try:
    from sklearn.cluster import DBSCAN
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️  Scikit-learn not found. Using Fallback Clusterer.")

class Clusterer:
    """
    The Mining Engine.
    Uses DBSCAN (or Fallback) to find clusters in feature space.
    """
    def __init__(self, eps=0.5, min_samples=2):
        self.eps = eps
        self.min_samples = min_samples
        if SKLEARN_AVAILABLE:
            self.model = DBSCAN(eps=eps, min_samples=min_samples)

    def mine_clusters(self, feature_vectors: List[Dict[str, float]]) -> List[ResourceClusterObject]:
        """
        Clusters feature vectors into RCOs.
        """
        if not feature_vectors:
            return []

        # Convert dicts to numpy array [entropy, gradient, stability]
        data = []
        for f in feature_vectors:
            data.append([f['entropy'], f['gradient'], f['stability']])
        
        X = np.array(data)
        
        if SKLEARN_AVAILABLE:
            # Fit DBSCAN
            labels = self.model.fit_predict(X)
        else:
            # Fallback: Simple Euclidean Distance Grouping
            labels = self._fallback_clustering(X)
        
        # Group by label
        clusters = {}
        for i, label in enumerate(labels):
            if label == -1: continue # Noise
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(feature_vectors[i])
            
        # Create RCOs
        rcos = []
        for label, members in clusters.items():
            # Calculate centroid
            centroid = {
                "entropy": np.mean([m['entropy'] for m in members]),
                "gradient": np.mean([m['gradient'] for m in members]),
                "stability": np.mean([m['stability'] for m in members]),
                "avg_temp": np.mean([m['avg_temp'] for m in members]),
                "spectral_energy": np.mean([m.get('spectral_energy', 0.0) for m in members])
            }
            
            # Classification Logic
            tags = []
            if centroid['avg_temp'] > 50: tags.append("thermal")
            if centroid['spectral_energy'] > 0.5: tags.append("vibration")
            if centroid['stability'] > 0.8: tags.append("stable")
            if not tags: tags.append("unknown")

            rco = ResourceClusterObject(
                centroid_energy_signature=centroid,
                entropy_gradient=centroid['gradient'],
                stability_index=centroid['stability'],
                classification_tags=tags
            )
            rcos.append(rco)
            
        print(f"⛏️  RCE: Mined {len(rcos)} clusters from {len(feature_vectors)} samples.")
        return rcos

    def _fallback_clustering(self, X):
        """
        Simple O(N^2) clustering for fallback.
        """
        n = len(X)
        labels = [-1] * n
        cluster_id = 0
        
        for i in range(n):
            if labels[i] != -1: continue
            
            # Start new cluster
            labels[i] = cluster_id
            found_neighbor = False
            
            for j in range(i+1, n):
                if labels[j] != -1: continue
                
                dist = np.linalg.norm(X[i] - X[j])
                if dist < self.eps:
                    labels[j] = cluster_id
                    found_neighbor = True
            
            if found_neighbor:
                cluster_id += 1
            else:
                labels[i] = -1 # Noise if no neighbors
                
        return labels
