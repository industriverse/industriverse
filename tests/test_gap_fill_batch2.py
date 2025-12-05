import pytest
from src.scf.marketplace.onboarding_pipeline import OnboardingPipeline
from src.scf.capsules.storefront import CapsuleStorefront
from src.scf.models.ebdm_micro_factory import EBDMMicroFactory

def test_onboarding():
    pipeline = OnboardingPipeline()
    profile = pipeline.onboard_client("Acme Corp", "Manufacturing")
    
    assert profile.name == "Acme Corp"
    assert profile.api_key.startswith("sk_live_")
    assert profile.fossilizer_config["industry"] == "Manufacturing"

def test_storefront():
    store = CapsuleStorefront()
    capsules = store.list_capsules()
    assert len(capsules) >= 2
    
    success = store.purchase_capsule("cli_123", "cap_energy_opt")
    assert success == True
    assert len(store.purchases) == 1

def test_micro_factory():
    factory = EBDMMicroFactory()
    model_id = factory.create_micro_model("cli_123", "hvac")
    assert "ebdm_micro_cli_123_hvac" in model_id
