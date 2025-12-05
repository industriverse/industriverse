import os
import json
import time

class DataRoomBuilder:
    """
    Automates the creation of an Investor Data Room.
    Aggregates ROI reports, Metrics, and Tech Docs.
    """
    def __init__(self, output_dir: str = "investor_data_room"):
        self.output_dir = output_dir

    def build_data_room(self):
        """
        Generate the folder structure and index.
        """
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 1. Create Index
        index_content = f"""# 📂 Sovereign Intelligence Data Room
**Generated**: {time.strftime("%Y-%m-%d")}

## Contents
1. [Financials](./financials)
2. [Technology](./technology)
3. [Legal](./legal)

---
*Confidential - For Investor Use Only*
"""
        with open(os.path.join(self.output_dir, "INDEX.md"), "w") as f:
            f.write(index_content)
            
        # 2. Create Subdirectories
        os.makedirs(os.path.join(self.output_dir, "financials"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "technology"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "legal"), exist_ok=True)
        
        # 3. Add Mock Files
        with open(os.path.join(self.output_dir, "financials", "roi_summary.csv"), "w") as f:
            f.write("Client,Savings,ROI\nAcme,10000,2.5x")
            
        print(f"📁 Data Room built at: {self.output_dir}")
        return self.output_dir
