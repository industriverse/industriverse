import json
import os
import sys
import shutil
import time

def ingest_request(brief_path):
    """
    Ingests a Client Brief and sets up the project environment.
    """
    if not os.path.exists(brief_path):
        print(f"❌ Error: Brief not found at {brief_path}")
        return

    try:
        with open(brief_path, 'r') as f:
            brief = json.load(f)
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in {brief_path}")
        return

    client_name = brief.get("client_name", "UnknownClient").replace(" ", "_")
    project_code = brief.get("project_code", "PROJ-000")
    persona = brief.get("preferred_persona", "research_lead")

    print(f"🚀 Ingesting Request for {client_name} ({project_code})...")

    # 1. Create Project Directory
    project_dir = f"projects/{client_name}/{project_code}"
    os.makedirs(project_dir, exist_ok=True)
    os.makedirs(f"{project_dir}/data", exist_ok=True)
    os.makedirs(f"{project_dir}/artifacts", exist_ok=True)
    os.makedirs(f"{project_dir}/logs", exist_ok=True)

    # 2. Generate Project Config
    config = {
        "project_id": project_code,
        "client": client_name,
        "created_at": time.time(),
        "active_persona": persona,
        "daemon_config": {
            "sampling_rate": 0.1,
            "research_mode": True,
            "output_dir": f"{project_dir}/data"
        },
        "constraints": brief.get("constraints", {})
    }

    with open(f"{project_dir}/project_config.json", 'w') as f:
        json.dump(config, f, indent=4)

    # 3. Copy Brief to Project Folder
    shutil.copy(brief_path, f"{project_dir}/original_brief.json")

    print(f"✅ Project Initialized: {project_dir}")
    print(f"   - Config: {project_dir}/project_config.json")
    print(f"   - Persona: {persona}")
    print(f"   - Ready for Orchestration.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest_request.py <path_to_brief.json>")
    else:
        ingest_request(sys.argv[1])
