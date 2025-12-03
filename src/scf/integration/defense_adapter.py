from typing import Dict, Any, List
from src.desktop.scds_forensics import SCDSForensicsSuite
from src.desktop.scds_network import SCDSNetworkSuite
from src.social.spi_advanced import SPIAdvancedSuite
from src.mobile.advanced.gps_defense import GPSDefenseStack

class SovereignDefenseAdapter:
    """
    The Shield of the Sovereign Code Foundry.
    Integrates SCDS (Desktop), SPI (Social), and GPS Defense into the generation loop.
    Ensures that code is generated and deployed only in safe, verified environments.
    """
    def __init__(self):
        print("🛡️ [SCF DEFENSE] Initializing Sovereign Defense Suites...")
        self.scds_forensics = SCDSForensicsSuite()
        self.scds_network = SCDSNetworkSuite()
        self.spi = SPIAdvancedSuite()
        self.gps = GPSDefenseStack()
        
    def check_environment_integrity(self) -> Dict[str, Any]:
        """
        Checks the physical and digital integrity of the host environment.
        """
        forensics_events = self.scds_forensics.run_scan()
        network_events = self.scds_network.run_network_audit()
        gps_events = self.gps.scan_location()
        
        integrity_score = 1.0
        threats = []
        
        for e in forensics_events:
            integrity_score -= 0.1
            threats.append(f"FORENSICS: {e.details['msg']}")
            
        for e in network_events:
            integrity_score -= 0.1
            threats.append(f"NETWORK: {e.details['msg']}")
            
        for e in gps_events:
            integrity_score -= 0.2
            threats.append(f"GPS: {e.details['msg']}")
            
        return {
            "integrity_score": max(0.0, integrity_score),
            "threats": threats,
            "safe_to_deploy": integrity_score > 0.8
        }
        
    def verify_social_safety(self, proposed_content: str) -> Dict[str, Any]:
        """
        Checks if the proposed content/agent violates Social Physics laws.
        (e.g. will it cause entropy collapse or impossible virality?)
        """
        # In a real system, we'd simulate the content's effect.
        # Here we check current social weather to see if it's safe to launch.
        spi_events = self.spi.run_suite()
        
        risk_level = 0.0
        warnings = []
        
        for e in spi_events:
            risk_level += e.score
            warnings.append(f"SPI: {e.details['msg']}")
            
        return {
            "risk_level": risk_level,
            "warnings": warnings,
            "safe_to_launch": risk_level < 0.5
        }
