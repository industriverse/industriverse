import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.unification.unified_substrate_model import USMSignal, SignalType, USMEnergy, USMEntropy
from src.unification.signal_translator import SignalTranslator

class USMVerifier:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def assert_true(self, condition, message):
        if condition:
            print(f"   ✅ PASS: {message}")
            self.passed += 1
        else:
            print(f"   ❌ FAIL: {message}")
            self.failed += 1

    def run_tests(self):
        print("🔬 STARTING DEEP USM VERIFICATION 🔬")
        
        # Test 1: Energy Conversion Math
        print("\n[Test 1] Energy Conversion Fidelity")
        e = USMEnergy(joules=1e6, compute_flops=1e12) # 1 MJ + 1 TFLOP
        credits = e.to_negentropy_credits()
        self.assert_true(abs(credits - 2.0) < 0.001, f"Expected 2.0 Credits, got {credits}")

        # Test 2: Entropy Composition
        print("\n[Test 2] Entropy Composite Score")
        ent = USMEntropy(shannon_index=0.9, thermo_disorder=0.0, social_discord=0.0)
        score = ent.get_composite_score()
        self.assert_true(abs(score - 0.3) < 0.001, f"Expected 0.3 Score, got {score}")

        # Test 3: Signal Validation (Happy Path)
        print("\n[Test 3] Signal Validation (Valid)")
        sig = USMSignal(type=SignalType.THERMAL, source_id="TEST")
        self.assert_true(sig.validate(), "Valid signal should pass validation")

        # Test 4: Signal Validation (Future Timestamp)
        print("\n[Test 4] Signal Validation (Future Timestamp)")
        sig_future = USMSignal(type=SignalType.THERMAL, source_id="TEST")
        sig_future.timestamp = time.time() + 100 # Future
        self.assert_true(not sig_future.validate(), "Future signal should fail validation")

        # Test 5: SCDS Translation
        print("\n[Test 5] SCDS Translation Accuracy")
        scds_raw = {"severity": 0.75, "source": "FW"}
        sig_scds = SignalTranslator.from_scds(scds_raw)
        self.assert_true(sig_scds.type == SignalType.SECURITY, "Type should be SECURITY")
        self.assert_true(sig_scds.entropy_delta.shannon_index == 0.75, "Shannon Index should match Severity")

        # Test 6: SPI Translation
        print("\n[Test 6] SPI Translation Accuracy")
        spi_raw = {"sentiment_score": 0.1} # 0.9 Negativity
        sig_spi = SignalTranslator.from_spi(spi_raw)
        self.assert_true(sig_spi.type == SignalType.SOCIAL, "Type should be SOCIAL")
        self.assert_true(abs(sig_spi.entropy_delta.social_discord - 0.9) < 0.001, "Discord should be 1.0 - Sentiment")

        # Summary
        print(f"\n📊 RESULTS: {self.passed} Passed, {self.failed} Failed")
        if self.failed > 0:
            sys.exit(1)

if __name__ == "__main__":
    verifier = USMVerifier()
    verifier.run_tests()
