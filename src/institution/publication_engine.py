from typing import List, Dict
from src.anthropology.cognitive_fossil_record import CognitiveFossil

class PublicationEngine:
    """
    The Automated Scribe.
    Generates scientific papers and reports from the Cognitive Fossil Record.
    """
    
    @staticmethod
    def generate_paper(fossil: CognitiveFossil, trail: List[CognitiveFossil]) -> str:
        """
        Compiles a scientific paper from a discovery and its lineage.
        """
        title = f"Paper: {fossil.description}"
        
        # 1. Authors (All contributors in the trail)
        authors = sorted(list(set([f.creator_id for f in trail])))
        author_line = f"Authors: {', '.join(authors)}"
        
        # 2. Abstract
        abstract = f"Abstract:\nThis paper presents the evolution of '{fossil.description}'. "
        abstract += f"The research originated from '{trail[0].description}' and underwent {len(trail)-1} evolutionary iterations. "
        abstract += f"Key methodologies included: {', '.join(PublicationEngine._extract_methods(trail))}."
        
        # 3. Methodology Section (The Trail)
        methodology = "Evolutionary Methodology:\n"
        for i, step in enumerate(trail):
            methodology += f"  Step {i+1}: {step.description}\n"
            methodology += f"    - Agent: {step.creator_id}\n"
            methodology += f"    - Context: {step.narrative_context}\n"
        
        # Assemble
        full_text = f"""
{'='*40}
{title}
{author_line}
{'='*40}

{abstract}

{methodology}
{'='*40}
        """
        return full_text

    @staticmethod
    def _extract_methods(trail: List[CognitiveFossil]) -> List[str]:
        """
        Parses 'Mechanism Used' from fossil descriptions.
        """
        methods = []
        for f in trail:
            if "Tool:" in f.description:
                try:
                    # Hacky parsing based on our genealogy format
                    parts = f.description.split("Tool: ")
                    if len(parts) > 1:
                        methods.append(parts[1].strip())
                except:
                    pass
        return list(set(methods))

# --- Verification ---
if __name__ == "__main__":
    # Mock Data
    f1 = CognitiveFossil(description="Idea A | Tool: Brainstorm", creator_id="Agent A")
    f2 = CognitiveFossil(description="Idea A.1 | Tool: Optimizer", creator_id="Agent B")
    paper = PublicationEngine.generate_paper(f2, [f1, f2])
    print(paper)
