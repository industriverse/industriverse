import random

class ThermodynamicTranslator:
    """
    Maps thermodynamic energy signatures to semantic tags/meanings.
    """
    def __init__(self):
        # Simple rule-based mapping for demo purposes
        self.rules = [
            {"condition": lambda e: e["Entropy"] > 2.0, "tag": "High_Disorder", "severity": "WARNING"},
            {"condition": lambda e: e["dE_dt_volatility"] > 500, "tag": "Rapid_Flux", "severity": "CRITICAL"},
            {"condition": lambda e: e["E_total"] == 0, "tag": "Dead_Signal", "severity": "ERROR"},
            {"condition": lambda e: e["E_total"] > 1000 and e["Entropy"] < 0.5, "tag": "High_Efficiency", "severity": "INFO"}
        ]

    def translate(self, energy_vector):
        """
        Args:
            energy_vector (dict): Output from PowerTraceConverter.
        Returns:
            list: List of semantic tags.
        """
        tags = []
        for rule in self.rules:
            if rule["condition"](energy_vector):
                tags.append({
                    "tag": rule["tag"],
                    "severity": rule["severity"],
                    "vector_snapshot": energy_vector
                })
        
        if not tags:
            tags.append({"tag": "Nominal_State", "severity": "INFO", "vector_snapshot": energy_vector})
            
        return tags

class NarrativeEngine:
    """
    Generates human-readable incident reports from semantic tags.
    """
    def generate_report(self, node_id, tags):
        """
        Args:
            node_id (str): ID of the monitored node.
            tags (list): List of tags from ThermodynamicTranslator.
        Returns:
            str: A natural language report.
        """
        report_lines = [f"--- Incident Report for Node: {node_id} ---"]
        
        severity_map = {"INFO": "ℹ️", "WARNING": "⚠️", "CRITICAL": "🚨", "ERROR": "❌"}
        
        for item in tags:
            icon = severity_map.get(item["severity"], "•")
            tag_name = item["tag"].replace("_", " ")
            
            # Template-based generation
            if item["tag"] == "High_Disorder":
                desc = "System is exhibiting high entropic variance, suggesting internal instability or unauthorized encryption activity."
            elif item["tag"] == "Rapid_Flux":
                desc = "Sudden spike in power volatility detected. Possible surge or rapid load change."
            elif item["tag"] == "Dead_Signal":
                desc = "Zero energy signature received. Sensor may be offline or severed."
            elif item["tag"] == "High_Efficiency":
                desc = "System operating at peak efficiency with low entropy waste."
            else:
                desc = "System state is within nominal parameters."
                
            report_lines.append(f"{icon} [{item['severity']}] {tag_name}: {desc}")
            
        return "\n".join(report_lines)
