import logging
from src.rdr.ingestion import PhysicsDataPreparation
from src.rdr.reasoning import PhysicsContentReasoning

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Batch1Ingestion")

BATCH_1_SOURCES = [
    {
        "title": "DeepSeek-Math-V2",
        "url": "https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/main/DeepSeekMath_V2.pdf",
        "type": "Model Paper",
        "domain": "Mathematics/AI",
        "summary": "A specialized LLM for mathematical reasoning, achieving SOTA on math benchmarks via large-scale synthetic data and RL."
    },
    {
        "title": "OLMo 3",
        "url": "https://allenai.org/blog/olmo3",
        "type": "Model Blog",
        "domain": "Open Science/AI",
        "summary": "A fully open 32B parameter model with open weights, data, and training code. Features OlmoTrace for transparency and RLVR for reasoning."
    },
    {
        "title": "Fara-7B",
        "url": "https://www.microsoft.com/en-us/research/publication/fara-7b-an-efficient-agentic-model-for-computer-use/",
        "type": "Model Paper",
        "domain": "Agentic AI/Computer Use",
        "summary": "An efficient 7B agentic model for computer use (CUA), trained on FaraGen synthetic data to perceive screens and execute actions."
    }
]

def ingest_batch():
    logger.info("Starting Batch 1 Ingestion...")
    
    reasoning_engine = PhysicsContentReasoning(llm_model=None) # Mock LLM
    
    for source in BATCH_1_SOURCES:
        logger.info(f"Processing: {source['title']} ({source['url']})")
        
        # 1. Mock Ingestion (Text Extraction)
        # In a real scenario, we'd use read_url_content or PDF parsers here.
        # For now, we use the summary.
        content = source['summary']
        
        # 2. Reasoning (Perspective Extraction)
        # We manually inject the perspectives based on our research
        perspectives = {}
        if "DeepSeek" in source['title']:
            perspectives = {
                "Mechanism": "Reinforcement Learning on Synthetic Math Data",
                "Application": "Formal Proof Generation, Equation Solving",
                "Method": "Group Relative Policy Optimization (GRPO)"
            }
        elif "OLMo" in source['title']:
            perspectives = {
                "Mechanism": "RLVR (Reinforcement Learning with Verifiable Rewards)",
                "Application": "Transparent Reasoning, Source Tracing",
                "Method": "Full Stack Open Source (Weights + Data)"
            }
        elif "Fara" in source['title']:
            perspectives = {
                "Mechanism": "Visual Perception (Screenshots) -> Action Coordinates",
                "Application": "Computer Use Automation, Simulation Driving",
                "Method": "FaraGen Synthetic Trajectory Generation"
            }
            
        logger.info(f"  > Extracted Perspectives: {perspectives}")
        
        # 3. Update Knowledge Graph (Mock)
        logger.info(f"  > Added node '{source['title']}' to RDR Knowledge Graph.")
        logger.info(f"  > Linked '{source['title']}' to domain '{source['domain']}'.")
        
    logger.info("Batch 1 Ingestion Complete.")

if __name__ == "__main__":
    ingest_batch()
