import json
import random
import time
from dataclasses import dataclass

@dataclass
class MarketingPost:
    brand: str
    platform: str
    text: str
    image_prompt: str
    hashtags: list

class ContentEngine:
    """
    The Bridge between Code and Culture.
    Takes raw telemetry -> Generates Brand-Aligned Content.
    """
    
    def __init__(self):
        self.brands = {
            "EMPEIRIA": {
                "voice": "Academic, Visionary, Calm",
                "visual_token": "white marble, gold lines, architectural void, 8k"
            },
            "INDUSTRIVERSE": {
                "voice": "Technical, Urgent, Cyberpunk",
                "visual_token": "dark industrial, neon blue, carbon fiber, schematic"
            },
            "THERMODYNASTY": {
                "voice": "Financial, Liquid, Sophisticated",
                "visual_token": "liquid copper, emerald green, luxury financial data"
            }
        }

    def generate_content(self, event_type: str, data: dict) -> MarketingPost:
        """
        Router logic to decide which Brand handles which Event.
        """
        if event_type == "SPI_BOTNET_DETECTED":
            return self._create_empeiria_post(data)
        elif event_type == "SCDS_THREAT_BLOCKED":
            return self._create_industriverse_post(data)
        elif event_type == "NEGENTROPY_MINTED":
            return self._create_thermodynasty_post(data)
        else:
            return self._create_generic_post(data)

    def _create_empeiria_post(self, data) -> MarketingPost:
        # Empeiria: The Researcher
        score = data.get('coordination_score', 0.0)
        topic = data.get('topic', 'Unknown')
        
        text = (
            f"Anomaly Detected. \n"
            f"Our sensors indicate a non-physical coordination spike (Score: {score:.2f}) "
            f"surrounding the topic '{topic}'. \n"
            f"The laws of social physics suggest artificial amplification. \n"
            f"We are observing."
        )
        
        prompt = (
            f"Abstract data visualization of a social network entropy collapse, "
            f"{self.brands['EMPEIRIA']['visual_token']}, minimalist"
        )
        
        return MarketingPost(
            brand="Empeiria Haus",
            platform="X/LinkedIn",
            text=text,
            image_prompt=prompt,
            hashtags=["#SocialPhysics", "#Empeiria", "#Truth"]
        )

    def _create_industriverse_post(self, data) -> MarketingPost:
        # Industriverse: The Defender
        threat = data.get('threat_type', 'Unknown')
        module = data.get('module', 'SCDS-Core')
        
        text = (
            f"🛡️ THREAT NEUTRALIZED.\n"
            f"VECTOR: {threat.upper()}\n"
            f"MODULE: {module}\n"
            f"STATUS: BLOCKED via Thermodynamic Signature.\n"
            f"System Integrity: 100%."
        )
        
        prompt = (
            f"Holographic wireframe of a laptop blocking a red cyber attack, "
            f"{self.brands['INDUSTRIVERSE']['visual_token']}, volumetric fog"
        )
        
        return MarketingPost(
            brand="Industriverse",
            platform="X",
            text=text,
            image_prompt=prompt,
            hashtags=["#CyberSecurity", "#SCDS", "#Industriverse", "#SecOps"]
        )

    def _create_thermodynasty_post(self, data) -> MarketingPost:
        # Thermodynasty: The Banker
        amount = data.get('amount', 0)
        asset = data.get('asset_class', 'Compute')
        
        text = (
            f"Liquidity Event Confirmed.\n"
            f"+{amount} Negentropy Credits minted.\n"
            f"Underlying Asset: {asset}.\n"
            f"The economy of physics is now live."
        )
        
        prompt = (
            f"Liquid copper coins flowing into a digital glass ledger, "
            f"{self.brands['THERMODYNASTY']['visual_token']}, macro photography"
        )
        
        return MarketingPost(
            brand="Thermodynasty",
            platform="X",
            text=text,
            image_prompt=prompt,
            hashtags=["#DePIN", "#Negentropy", "#Thermodynasty", "#Yield"]
        )

    def _create_generic_post(self, data) -> MarketingPost:
        return MarketingPost("System", "Log", str(data), "Abstract tech", [])

# --- Verification / Demo ---
if __name__ == "__main__":
    engine = ContentEngine()
    
    print("--- 1. Simulating SPI Botnet Event ---")
    post1 = engine.generate_content("SPI_BOTNET_DETECTED", {"coordination_score": 0.98, "topic": "Election"})
    print(f"BRAND: {post1.brand}")
    print(f"TEXT: {post1.text}")
    print(f"PROMPT: {post1.image_prompt}\n")
    
    print("--- 2. Simulating SCDS Threat Event ---")
    post2 = engine.generate_content("SCDS_THREAT_BLOCKED", {"threat_type": "CryptoMiner", "module": "Thermal-01"})
    print(f"BRAND: {post2.brand}")
    print(f"TEXT: {post2.text}")
    print(f"PROMPT: {post2.image_prompt}\n")
    
    print("--- 3. Simulating Economy Event ---")
    post3 = engine.generate_content("NEGENTROPY_MINTED", {"amount": 500, "asset_class": "Idle GPU"})
    print(f"BRAND: {post3.brand}")
    print(f"TEXT: {post3.text}")
    print(f"PROMPT: {post3.image_prompt}\n")
