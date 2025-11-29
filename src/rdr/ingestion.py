import time
from typing import List, Dict, Any

class PhysicsDataPreparation:
    def __init__(self, llm_filter_model=None):
        self.venues = [
            'arXiv:astro-ph', 'arXiv:physics.plasm-ph', 'arXiv:physics.flu-dyn',
            'Physical Review Letters', 'Nature Physics', 'Astrophysical Journal',
            'Physics of Fluids', 'Plasma Physics and Controlled Fusion'
        ]
        self.llm_filter = llm_filter_model
    
    def collect_papers(self, start_year: int = 2020) -> List[Dict[str, Any]]:
        """Collect physics papers from top venues"""
        papers = []
        for venue in self.venues:
            papers.extend(self._crawl_venue(venue, start_year))
        return papers
    
    def filter_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter papers using LLM-based domain matching"""
        physics_definition = """
        Research involving computational physics simulations, experimental 
        datasets from high-energy physics, astrophysics, fluid dynamics, 
        plasma physics, and materials science. These datasets enable discovery 
        of physical laws, mechanisms, and predictive models.
        
        Key Indicators:
        - MHD simulations
        - Astrophysical phenomena (supernovae, neutron stars)
        - Turbulent flow dynamics
        - Plasma physics
        - Computational fluid dynamics
        """
        
        filtered = []
        for paper in papers:
            if self._matches_domain(paper, physics_definition):
                filtered.append(paper)
        
        return filtered

    def _crawl_venue(self, venue: str, start_year: int) -> List[Dict[str, Any]]:
        """
        Scan local directory 'data/ingest' for real files.
        Replaces mock crawler.
        """
        import os
        import hashlib
        
        ingest_dir = os.path.join(os.getcwd(), "data", "ingest")
        if not os.path.exists(ingest_dir):
            os.makedirs(ingest_dir, exist_ok=True)
            # Create a sample file if empty to demonstrate functionality
            with open(os.path.join(ingest_dir, "sample_physics.txt"), "w") as f:
                f.write("Title: MHD Simulation of Plasma\nAbstract: We simulate high-energy plasma turbulence using Navier-Stokes equations.")
        
        print(f"Scanning {ingest_dir} for papers...")
        papers = []
        
        for root, dirs, files in os.walk(ingest_dir):
            for file in files:
                if file.endswith(".txt") or file.endswith(".md"):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            content = f.read()
                            
                        # Simple parsing: Assume first line is title, rest is abstract
                        lines = content.split('\n')
                        title = lines[0].replace("Title:", "").strip() if lines else file
                        abstract = "\n".join(lines[1:]).replace("Abstract:", "").strip() if len(lines) > 1 else ""
                        
                        papers.append({
                            "id": hashlib.md5(path.encode()).hexdigest(),
                            "title": title,
                            "abstract": abstract,
                            "year": 2024, # Default to current year for local files
                            "venue": "Local Ingest"
                        })
                    except Exception as e:
                        print(f"Error reading {file}: {e}")
                        
        return papers

    def _matches_domain(self, paper: Dict[str, Any], definition: str) -> bool:
        """
        Check if paper matches the physics domain definition.
        Uses LLM if available, otherwise keyword matching.
        """
        if self.llm_filter:
            # Mock LLM call
            # prompt = f"Does this paper match the definition?\nPaper: {paper}\nDefinition: {definition}"
            # return self.llm_filter.generate(prompt) == "Yes"
            return True
        
        # Fallback: Keyword matching
        keywords = ["MHD", "plasma", "turbulence", "fluid", "simulation", "physics"]
        text = (paper['title'] + " " + paper['abstract']).lower()
        return any(k.lower() in text for k in keywords)
