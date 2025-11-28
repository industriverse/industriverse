import time
import json
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class MockKnowledgeGraph:
    def __init__(self):
        self.data = {
            "refining_node_01": {
                "efficiency": 0.92,
                "status": "active",
                "last_maintenance": "2025-11-20"
            },
            "assembly_node_04": {
                "efficiency": 0.88,
                "status": "warning",
                "last_maintenance": "2025-10-15"
            }
        }

    def query(self, entity, attribute):
        if entity in self.data:
            return self.data[entity].get(attribute, "Unknown attribute")
        return "Entity not found"

class UserLM:
    def __init__(self, kg):
        self.kg = kg

    def process_query(self, user_input):
        logger.info(f"[UserLM] Processing: '{user_input}'")
        time.sleep(1.0) # Simulate inference latency
        
        # Simple regex-based intent parsing for demo purposes
        # In production, this would be a LLM call
        
        # Pattern: "What is the [attribute] of [entity]?"
        match = re.search(r"what is the (\w+) of ([\w_]+)", user_input.lower())
        
        if match:
            attribute = match.group(1)
            entity = match.group(2)
            
            logger.info(f"[UserLM] Intent Detected: GET_ATTRIBUTE(entity={entity}, attr={attribute})")
            
            value = self.kg.query(entity, attribute)
            
            # Generate natural language response
            response = f"The {attribute} of {entity} is currently {value}."
            return response
            
        return "I'm sorry, I didn't understand that query. Try asking about specific node attributes."

def run():
    print("\n" + "="*60)
    print(" DEMO 7: USERLM INTERACTIVE QUERY")
    print("="*60 + "\n")

    kg = MockKnowledgeGraph()
    user_lm = UserLM(kg)

    queries = [
        "What is the efficiency of refining_node_01?",
        "What is the status of assembly_node_04?",
        "What is the color of refining_node_01?" # Invalid attribute
    ]

    for q in queries:
        print(f"User: {q}")
        response = user_lm.process_query(q)
        print(f"UserLM: {response}\n")
        time.sleep(1)

    print("\n" + "="*60)
    print(" DEMO COMPLETE: NLP QUERY SUCCESSFUL")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
