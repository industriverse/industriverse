from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import glob

app = FastAPI(title="Empeiria Haus Bridge", version="1.0.0")

# Enable CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "data/research/raw"
CONTROL_FILE = "data/datahub/control.json"
VAULT_DIR = "examples/client_deliverables"

@app.get("/status")
def get_status():
    """Returns the current status of the Daemon."""
    # Check if daemon process is running (simplified check)
    # In production, we'd check the PID file or process list.
    # For now, we assume it's running if the control file exists.
    status = "UNKNOWN"
    if os.path.exists(CONTROL_FILE):
        status = "RUNNING"
    
    return {"status": status, "persona": "research_lead"} # Mock persona for now

@app.get("/metrics")
def get_metrics():
    """Returns the latest research metrics (Entropy, Safety)."""
    try:
        files = sorted(glob.glob(os.path.join(DATA_DIR, "*.json")), reverse=True)
        if not files:
            return {"entropy": 1.0, "safety": 1.0, "mastery_stage": "OBSERVATION"}
        
        with open(files[0], 'r') as f:
            data = json.load(f)
            metrics = data.get("metrics", {})
            return {
                "entropy": metrics.get("entropy", 1.0),
                "safety": metrics.get("safety_score", 1.0),
                "mastery_stage": data.get("mastery_stage", "UNKNOWN")
            }
    except Exception as e:
        return {"error": str(e)}

@app.get("/vault")
def get_vault_items():
    """Returns a list of generated Value Artifacts."""
    items = []
    if os.path.exists(VAULT_DIR):
        for f in os.listdir(VAULT_DIR):
            if not f.startswith("."):
                items.append(f)
    return {"items": items}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
