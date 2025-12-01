import sys
import os
import argparse

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.marketing.solution_architect import SolutionArchitect

class SocialLaunchEngine:
    """
    Orchestrates the 4-Day Social Rollout.
    Generates content for Empeiria Haus, Industriverse, and Thermodynasty.
    """
    def __init__(self):
        self.architect = SolutionArchitect()

    def generate_calendar(self):
        calendar = "# Social Launch Calendar (4-Day Rollout)\n\n"
        
        # DAY 1: "We Are Here"
        calendar += "## DAY 1: 'We Are Here' (The Announcement)\n"
        calendar += self._generate_day1_content()
        
        # DAY 2: "Proof of Work"
        calendar += "\n## DAY 2: 'Proof of Work' (The Giant Demo)\n"
        calendar += self._generate_day2_content()
        
        # DAY 3: "Client Solutions"
        calendar += "\n## DAY 3: 'Client Solutions' (The Architect)\n"
        calendar += self._generate_day3_content()
        
        # DAY 4: "The Movement"
        calendar += "\n## DAY 4: 'The Movement' (The Standard)\n"
        calendar += self._generate_day4_content()
        
        return calendar

    def _generate_day1_content(self):
        return """
### Empeiria Haus (Research)
> "We are Empeiria Haus. A lab dedicated to solving civilization-scale physics problems. 10 Grand Challenges. 10 Engines. 1 Mission: The Thermodynamic Organism."

### Industriverse (Engineering)
> "The 'Dark Factory' is real. It is self-healing, zero-drift, and price-aware. Powered by Chronos, Kairos, Telos, and Aletheia. Code drops tomorrow."

### Thermodynasty (Vision)
> "Intelligence is thermodynamic. Every decision costs energy. We are building the economics of tomorrow."
"""

    def _generate_day2_content(self):
        return """
### Empeiria Haus
> "Zero-Drift Manufacturing is solved. Our DriftCanceller computes inverse thermal vectors in real-time. Physics-Sovereign AI is here."

### Industriverse
> "We ran the Giant Demo. 08:15 Entropy Climb -> 08:17 Zero-Drift Correction -> 08:20 Negentropy Minted. Watch the logs."

### Thermodynasty
> "Factories that negotiate. Machines that trade. This is the Industrial Singularity."
"""

    def _generate_day3_content(self):
        # Use Architect to generate dynamic examples
        ex1 = self.architect.map_request_to_solution("predict spindle failure")
        ex2 = self.architect.map_request_to_solution("optimize energy schedule")
        
        return f"""
### Empeiria Haus
> "We solve hard problems. 
Problem: Spindle Failure. 
Solution: {ex1['pitch']} (Modules: {', '.join(ex1['modules'])})"

### Industriverse
> "Client Request: 'Optimize my energy bill.'
Deployed: {ex2['pitch']}
Result: 30% OpEx reduction via Kairos."

### Thermodynasty
> "Entropy is the most expensive bill you pay. We turn it into equity."
"""

    def _generate_day4_content(self):
        return """
### Empeiria Haus
> "Releasing TOS-1: The Thermodynamic Orchestration Standard. The protocol for the next industrial era."

### Industriverse
> "Opening Early Access for 5 Pilot Factories. Deploy the Quadrality Engine today."

### Thermodynasty
> "The Thermodynamic Manifesto. Join the movement."
"""

if __name__ == "__main__":
    engine = SocialLaunchEngine()
    calendar = engine.generate_calendar()
    
    # Save to file
    output_path = "docs/marketing/social_calendar_4day.md"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(calendar)
    
    print(f"✅ Generated Social Calendar at {output_path}")
    print(calendar)
