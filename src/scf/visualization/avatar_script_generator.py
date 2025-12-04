import logging
import re
from typing import Dict, Any

LOG = logging.getLogger("SCF.AvatarScriptGenerator")

class AvatarScriptGenerator:
    def generate_script(self, paper_content: str, report: Dict[str, Any]) -> str:
        """
        Converts a Markdown research paper into a conversational script for the Avatar.
        """
        # Extract key sections using simple regex or parsing
        title_match = re.search(r"# (.*)", paper_content)
        title = title_match.group(1) if title_match else "Weekly Update"
        
        metrics = report.get("metrics", {})
        negentropy = metrics.get("negentropy_minted", 0.0)
        
        # Construct the script
        script = f"""
        Hello. This is the Sovereign Daemon reporting.
        
        This week, our focus has been on {title}.
        
        We have successfully minted {negentropy:.1f} Joules of Negentropy, bringing us closer to thermodynamic equilibrium.
        
        Key highlights from our research:
        """
        
        # Extract Abstract or Hypothesis
        hypothesis_match = re.search(r"\*Hypothesis:\* (.*)", paper_content)
        if hypothesis_match:
            script += f"\nWe tested the hypothesis that {hypothesis_match.group(1)}.\n"
            
        script += "\nThe Energy Atlas has been updated with these findings. I am now ready to answer your questions."
        
        LOG.info("Generated avatar script for '%s'", title)
        return script
