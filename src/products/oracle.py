from src.core.oracle import Oracle

class TheOracle:
    """
    Product 7: The Oracle
    Physics-First RAG.
    """
    def __init__(self):
        self.name = "The Oracle"
        self.oracle = Oracle()

    def get_status(self):
        return {
            "product": self.name,
            "status": "OMNISCIENT",
            "knowledge_base": "Physics"
        }

    def consult(self, query):
        print(f"[{self.name}] Consulting First Principles: {query}")
        return self.oracle.consult(query)
