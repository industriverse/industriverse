import math
from collections import Counter

class SocialEntropyEngine:
    """
    SPI Module 2: Social Entropy Engine (SEE).
    Detects 'Entropy Collapse' in conversation threads.
    Bots say the same thing (Low Entropy). Humans are diverse (High Entropy).
    """
    def __init__(self):
        pass
        
    def calculate_shannon_entropy(self, text_corpus: list) -> float:
        """
        Computes the entropy of the token distribution.
        """
        all_text = " ".join(text_corpus)
        tokens = all_text.split()
        total_tokens = len(tokens)
        if total_tokens == 0:
            return 0.0
            
        counts = Counter(tokens)
        entropy = 0.0
        
        for count in counts.values():
            p = count / total_tokens
            entropy -= p * math.log2(p)
            
        return entropy
        
    def detect_collapse(self, thread_messages: list) -> bool:
        """
        Flags if a thread looks like a bot swarm (Low Entropy).
        """
        entropy = self.calculate_shannon_entropy(thread_messages)
        print(f"🗣️ [SEE] Thread Entropy: {entropy:.4f}")
        
        # Threshold: Low entropy means repetitive content
        if entropy < 2.0 and len(thread_messages) > 5:
            print("   🚨 ALERT: Entropy Collapse Detected! (Bot Swarm?)")
            return True
        return False
