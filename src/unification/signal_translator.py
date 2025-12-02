from typing import Dict, Any
from src.unification.unified_substrate_model import USMSignal, SignalType, USMEnergy, USMEntropy

class SignalTranslator:
    """
    The Universal Translator.
    Converts domain-specific telemetry into Canonical USM Signals.
    """
    
    @staticmethod
    def from_scds(threat_data: Dict[str, Any]) -> USMSignal:
        """
        Converts SCDS Threat Data -> USMSignal (SECURITY).
        """
        severity = threat_data.get("severity", 0.0)
        entropy = USMEntropy(shannon_index=severity, thermo_disorder=0.0, social_discord=0.0)
        
        return USMSignal(
            type=SignalType.SECURITY,
            source_id=threat_data.get("source", "SCDS_CORE"),
            entropy_delta=entropy,
            raw_data=threat_data
        )

    @staticmethod
    def from_spi(sentiment_data: Dict[str, Any]) -> USMSignal:
        """
        Converts SPI Sentiment Data -> USMSignal (SOCIAL).
        """
        negativity = 1.0 - sentiment_data.get("sentiment_score", 0.5)
        entropy = USMEntropy(shannon_index=0.0, thermo_disorder=0.0, social_discord=negativity)
        
        return USMSignal(
            type=SignalType.SOCIAL,
            source_id="SPI_ENGINE",
            entropy_delta=entropy,
            raw_data=sentiment_data
        )

    @staticmethod
    def from_lithos(physics_data: Dict[str, Any]) -> USMSignal:
        """
        Converts LithOS Physics Data -> USMSignal (SCIENTIFIC/THERMAL).
        """
        energy = USMEnergy(joules=physics_data.get("energy_output", 0.0))
        entropy = USMEntropy(thermo_disorder=physics_data.get("stability_loss", 0.0))
        
        return USMSignal(
            type=SignalType.SCIENTIFIC,
            source_id="LITHOS_KERNEL",
            energy_delta=energy,
            entropy_delta=entropy,
            raw_data=physics_data
        )

# --- Verification ---
if __name__ == "__main__":
    # Test SCDS Translation
    scds_data = {"severity": 0.8, "source": "FIREWALL", "type": "DDOS"}
    sig1 = SignalTranslator.from_scds(scds_data)
    print(f"SCDS -> USM: Type={sig1.type.name}, Entropy={sig1.entropy_delta.shannon_index}")
    
    # Test SPI Translation
    spi_data = {"sentiment_score": 0.2} # Highly Negative
    sig2 = SignalTranslator.from_spi(spi_data)
    print(f"SPI -> USM: Type={sig2.type.name}, Discord={sig2.entropy_delta.social_discord}")
