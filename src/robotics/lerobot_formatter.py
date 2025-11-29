import os
import json
import shutil
from typing import List, Dict, Any

class LeRobotFormatter:
    """
    Converts raw Ego2Robot JSONL data into the standard LeRobot Dataset format.
    Ref: https://huggingface.co/docs/lerobot/
    """
    def __init__(self, input_dir="data/robotics/ego2robot_processed", output_dir="data/robotics/lerobot_dataset"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        
    def create_dataset_structure(self):
        """
        Creates the directory structure for a LeRobot dataset.
        """
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        
        os.makedirs(os.path.join(self.output_dir, "data"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "meta"), exist_ok=True)
        
        # Create dataset_info.json
        info = {
            "dataset_name": "egocentric_10k_robotics",
            "version": "1.0.0",
            "description": "Robotics dataset derived from Egocentric-10K human demonstrations.",
            "features": {
                "observation.state": {"dtype": "float32", "shape": [6], "names": ["lh_x", "lh_y", "lh_z", "rh_x", "rh_y", "rh_z"]},
                "action": {"dtype": "float32", "shape": [3], "names": ["x", "y", "z"]}
            }
        }
        with open(os.path.join(self.output_dir, "meta", "dataset_info.json"), 'w') as f:
            json.dump(info, f, indent=2)
            
        print(f"LeRobotFormatter: Initialized dataset at {self.output_dir}")

    def convert_all(self):
        """
        Reads all JSONL files and aggregates them into the dataset.
        """
        self.create_dataset_structure()
        
        jsonl_files = [f for f in os.listdir(self.input_dir) if f.endswith(".jsonl")]
        total_episodes = 0
        
        for f_name in jsonl_files:
            path = os.path.join(self.input_dir, f_name)
            with open(path, 'r') as f:
                episode_data = [json.loads(line) for line in f]
                
            # Save as a parquet or msgpack (Mock: just saving as JSON for now)
            # In real LeRobot, we would use `datasets` library to save as Parquet
            episode_path = os.path.join(self.output_dir, "data", f"episode_{total_episodes}.json")
            with open(episode_path, 'w') as f:
                json.dump(episode_data, f)
                
            total_episodes += 1
            
        print(f"LeRobotFormatter: Converted {total_episodes} episodes.")

if __name__ == "__main__":
    formatter = LeRobotFormatter()
    formatter.convert_all()
