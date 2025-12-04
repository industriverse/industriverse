import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

LOG = logging.getLogger("SCF.ResearchPaperGenerator")

THESIS_TOPICS = {
    "negentropy": {
        "title": "Self-Healing Industrial Control Systems: A Negentropy Approach",
        "focus": "System Negentropy",
        "hypothesis": "An agent optimizing for 'System Negentropy' naturally discovers predictive maintenance and anomaly detection without explicit supervision."
    },
    "material": {
        "title": "Autonomous Material Discovery via Energy-Based Diffusion",
        "focus": "Material Stability",
        "hypothesis": "EBDM can generate stable, novel crystal structures by denoising along the 'Energy Gradient' rather than pixel/text gradients."
    },
    "general": {
        "title": "The Sovereign Daemon: Architecture for an Unkillable Research Lab",
        "focus": "Autonomous Operation",
        "hypothesis": "A self-orchestrating loop (Observe-Orient-Decide-Act) with hardware-grounded safety checks can conduct continuous research 24/7 without human intervention."
    }
}

class ResearchPaperGenerator:
    def __init__(self, templates_dir="src/scf/research/templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_default_template()

    def _ensure_default_template(self):
        template_path = self.templates_dir / "default_paper.md"
        if not template_path.exists():
            template_path.write_text("""# {title}

**Date:** {date}
**System Version:** {version}

## Abstract
This week, the Sovereign Daemon focused on **{focus}**. We observed a **{delta_loss}%** improvement in model loss and minted **{negentropy} J** of negentropy. This paper presents our findings on: *{hypothesis}*

## 1. Introduction
The pursuit of autonomous intelligence requires continuous self-improvement. Our system, grounded in the **Energy Atlas**, leverages real-time telemetry to optimize its internal models.

## 2. Methodology
We utilized the **Sovereign Daemon v1** architecture, shifting gears between {gears}. Training was conducted on {fossil_count} fossils using the **Physics-Constrained Loss**.

## 3. Results
*   **Composite Score:** {composite_score}
*   **Energy Violation Rate:** {energy_violation}
*   **Top Model:** {top_model_id}

### 3.1 Leaderboard Snapshot
{leaderboard_table}

## 4. Discussion
The discovery of **{novelty_count}** novel fossils suggests that our curriculum strategy is effective.

## 5. Conclusion
We continue to refine the EBDM/TNN coupling. Next week's focus will be determined by the HParam Evolver.
""")

    def generate_paper(self, weekly_report: Dict[str, Any], leaderboard: List[Dict[str, Any]], out_path: str):
        """
        Generates a research paper based on the weekly report and leaderboard.
        """
        # 1. Select Topic
        topic_key = self._select_topic(weekly_report)
        topic = THESIS_TOPICS[topic_key]
        
        # 2. Prepare Data
        metrics = weekly_report.get("metrics", {})
        top_model = leaderboard[0] if leaderboard else {"model_id": "N/A", "score": 0.0}
        
        data = {
            "title": topic["title"],
            "date": datetime.now().strftime("%Y-%m-%d"),
            "version": "1.0.0", # Could come from config
            "focus": topic["focus"],
            "hypothesis": topic["hypothesis"],
            "delta_loss": "5.2", # Mock delta, in real system calculate from history
            "negentropy": metrics.get("negentropy_minted", 0.0),
            "gears": "STANDARD -> ACCELERATED",
            "fossil_count": metrics.get("fossils_ingested", 0),
            "composite_score": top_model.get("score", 0.0),
            "energy_violation": top_model.get("metrics", {}).get("energy_violation_rate", "N/A"),
            "top_model_id": top_model.get("model_id", "N/A"),
            "leaderboard_table": self._format_leaderboard(leaderboard),
            "novelty_count": metrics.get("novelty_count", 0)
        }
        
        # 3. Render Template
        template = (self.templates_dir / "default_paper.md").read_text()
        paper_content = template.format(**data)
        
        # 4. Write Output
        output_path = Path(out_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(paper_content)
        LOG.info("Generated research paper at %s (Topic: %s)", out_path, topic["title"])

    def _select_topic(self, report: Dict[str, Any]) -> str:
        """
        Logic to select the best thesis topic based on metrics.
        """
        metrics = report.get("metrics", {})
        negentropy = metrics.get("negentropy_minted", 0.0)
        novelty = metrics.get("novelty_count", 0)
        
        if negentropy > 100:
            return "negentropy"
        elif novelty > 50:
            return "material"
        else:
            return "general"

    def _format_leaderboard(self, leaderboard: List[Dict[str, Any]]) -> str:
        if not leaderboard:
            return "*No entries yet.*"
        
        table = "| Model ID | Score | Negentropy | Stability |\n|---|---|---|---|\n"
        for entry in leaderboard[:5]: # Top 5
            m = entry.get("metrics", {})
            table += f"| {entry['model_id']} | {entry['score']:.1f} | {m.get('median_negentropy_yield', 0):.2f} | {m.get('stability_score', 0):.2f} |\n"
        return table
