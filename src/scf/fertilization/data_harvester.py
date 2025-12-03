import json
import os
import logging
from typing import List, Dict, Any
from src.datahub.value_vault import ValueVault

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DataHarvester")

class DataHarvester:
    """
    Harvests 'Code Fossils' from the ValueVault and transforms them into 
    training datasets for the Generator Network (GenN).
    """
    def __init__(self):
        self.value_vault = ValueVault()
        self.dataset_dir = "data/scf/datasets"
        os.makedirs(self.dataset_dir, exist_ok=True)

    def harvest(self, output_filename: str = "gen_n_train.jsonl") -> int:
        """
        Extracts approved code evolutions and saves them as a JSONL dataset.
        Returns the number of samples harvested.
        """
        logger.info("🌾 Starting Data Harvest...")
        
        # 1. Retrieve all secrets (fossils) from the vault
        # In a real impl, we would query by type/tag, but ValueVault is simple for now
        all_fossils = self.value_vault.retrieve_all_secrets()
        
        # 2. Filter and Transform
        dataset = []
        for fossil in all_fossils:
            if self._is_valid_training_sample(fossil):
                sample = self._transform_to_training_format(fossil)
                dataset.append(sample)
                
        # 3. Save to Disk
        output_path = os.path.join(self.dataset_dir, output_filename)
        self._save_dataset(dataset, output_path)
        
        logger.info(f"✅ Harvest Complete. Saved {len(dataset)} samples to {output_path}")
        return len(dataset)

    def _is_valid_training_sample(self, fossil: Dict[str, Any]) -> bool:
        """
        Determines if a fossil is high-quality enough for training.
        """
        # Must be a code evolution event
        if fossil.get("type") != "CODE_EVOLUTION":
            return False
            
        # Must be APPROVED by the Review Engine
        if fossil.get("verdict") != "APPROVE":
            return False
            
        # Optional: Check for high score
        feedback = fossil.get("feedback", {})
        if feedback.get("score", 0) < 0.7:
            return False
            
        return True

    def _transform_to_training_format(self, fossil: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts a fossil into an Instruction Tuning format (e.g., Alpaca).
        """
        return {
            "instruction": str(fossil.get("intent")),
            "input": "", # Context could go here if we stored it fully
            "output": str(fossil.get("code_snippet")),
            "metadata": {
                "timestamp": fossil.get("timestamp"),
                "score": fossil.get("feedback", {}).get("score")
            }
        }

    def _save_dataset(self, dataset: List[Dict[str, Any]], path: str):
        """
        Writes the dataset to a JSONL file.
        """
        with open(path, 'w') as f:
            for entry in dataset:
                f.write(json.dumps(entry) + '\n')

if __name__ == "__main__":
    harvester = DataHarvester()
    harvester.harvest()
