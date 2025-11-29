import json
import random
import time

class IntentVectorizer:
    """
    Mock implementation of the Intent Vectorizer.
    In the full system, this would load a CLIP or BERT model fine-tuned on Egocentric-10K.
    """
    def __init__(self):
        # print("Initializing Intent Vectorizer (Mock Mode)...")
        self.vocab = {
            "lightweight": [0.1, 0.8, -0.2],
            "strong": [0.9, -0.1, 0.5],
            "fast": [-0.2, 0.9, 0.1],
            "precision": [0.5, -0.5, 0.9],
            "bracket": [0.0, 0.0, 0.1], # Base object vector
            "gear": [0.0, 0.1, 0.0]
        }

    def vectorize(self, text):
        """
        Converts natural language text into a 'Physics Intent Vector'.
        Returns:
            vector (list): 3D embedding (mock)
            metadata (dict): Extracted keywords and confidence
        """
        tokens = text.lower().split()
        vector = [0.0, 0.0, 0.0]
        detected_keywords = []
        
        for token in tokens:
            if token in self.vocab:
                detected_keywords.append(token)
                v = self.vocab[token]
                vector[0] += v[0]
                vector[1] += v[1]
                vector[2] += v[2]
        
        # Normalize (Mock)
        mag = sum(x**2 for x in vector) ** 0.5
        if mag > 0:
            vector = [x/mag for x in vector]
            
        return {
            "vector": vector,
            "keywords": detected_keywords,
            "confidence": 0.85 + (random.random() * 0.1),
            "timestamp": time.time()
        }

if __name__ == "__main__":
    iv = IntentVectorizer()
    print(iv.vectorize("Make a lightweight strong bracket"))
