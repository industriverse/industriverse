import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.evolution.temporal_story_weaver import TemporalStoryWeaver
from src.marketing.narrative_feedback import NarrativeFeedbackLoop
from src.marketing.narrative_feedback import NarrativeFeedbackLoop
from src.meta.skill_hydrator import SkillHydrator
from src.economics.product_factory import ProductFactory

def run_verification():
    print("############################################################")
    print("#   PHASE 128: CRITICAL MISSING PIECES VERIFICATION        #")
    print("############################################################")

    # 1. Story Weaver
    print("\n📜 Testing Temporal Story Weaver...")
    weaver = TemporalStoryWeaver()
    mock_log = [{
        'experiment': 'Model_Quantization',
        'winner': 'B',
        'details': {
            'A': type('obj', (object,), {'roi': 10, 'latency_ms': 100})(),
            'B': type('obj', (object,), {'roi': 12, 'latency_ms': 80})()
        }
    }]
    story = weaver.weave_story(mock_log)
    if "Epoch 1" in story:
        print("✅ Story Weaver Passed.")
    else:
        print("❌ Story Weaver Failed.")

    # 2. Narrative Feedback
    print("\n👂 Testing Narrative Feedback...")
    loop = NarrativeFeedbackLoop()
    signals = loop.ingest_market_signals()
    plan = {'weights': {'optimization': 0.5, 'agents': 0.5}}
    new_plan = loop.adjust_evolution_plan(plan, signals)
    if new_plan['weights']['optimization'] > 0.5:
        print("✅ Narrative Feedback Passed.")
    else:
        print("❌ Narrative Feedback Failed.")

    # 3. Skill Hydrator
    print("\n🎓 Testing Skill Hydrator...")
    hydrator = SkillHydrator()
    capsule = hydrator.ingest_knowledge("https://github.com/test/repo")
    if capsule['status'] == 'READY':
        print("✅ Skill Hydrator Passed.")
    else:
        print("❌ Skill Hydrator Failed.")

    # 4. Product Factory
    print("\n🏭 Testing Product Factory...")
    factory = ProductFactory()
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../docs/products/product_catalog.md'))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    factory.generate_product_catalog(output_path)
    if os.path.exists(output_path):
        print("✅ Product Factory Passed.")
    else:
        print("❌ Product Factory Failed.")

if __name__ == "__main__":
    run_verification()
