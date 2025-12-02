from dataclasses import dataclass, field
from typing import Dict, List, Optional
import uuid

@dataclass
class LogisticsNode:
    id: str
    name: str # e.g., "Factory_Shanghai", "Port_LA"
    type: str # FACTORY, PORT, WAREHOUSE

@dataclass
class Route:
    id: str
    source_id: str
    target_id: str
    status: str = "OPEN" # OPEN, CONGESTED, BLOCKED
    transit_time_days: float = 10.0

class CognitiveSupplyChain:
    """
    The Nervous System of Global Trade.
    Manages nodes and routes, optimizing for resilience.
    """
    
    def __init__(self):
        self.nodes: Dict[str, LogisticsNode] = {}
        self.routes: Dict[str, Route] = {}
        
    def add_node(self, name: str, node_type: str) -> str:
        node = LogisticsNode(str(uuid.uuid4()), name, node_type)
        self.nodes[node.id] = node
        return node.id
        
    def add_route(self, source_id: str, target_id: str, days: float) -> str:
        route = Route(str(uuid.uuid4()), source_id, target_id, "OPEN", days)
        self.routes[route.id] = route
        return route.id
        
    def find_route(self, source_id: str, target_id: str) -> Optional[Route]:
        """
        Finds the best OPEN route between two nodes.
        (Simplified: Direct routes only for this demo)
        """
        for route in self.routes.values():
            if route.source_id == source_id and route.target_id == target_id:
                if route.status == "OPEN":
                    return route
                else:
                    print(f"   ⚠️ Route {route.id} is {route.status}. Searching for alternative...")
        return None

    def update_route_status(self, route_id: str, status: str):
        if route_id in self.routes:
            self.routes[route_id].status = status
            print(f"   🚚 [LOGISTICS] Route {route_id} Status: {status}")

# --- Verification ---
if __name__ == "__main__":
    chain = CognitiveSupplyChain()
    n1 = chain.add_node("A", "PORT")
    n2 = chain.add_node("B", "WAREHOUSE")
    r1 = chain.add_route(n1, n2, 5.0)
    chain.update_route_status(r1, "BLOCKED")
