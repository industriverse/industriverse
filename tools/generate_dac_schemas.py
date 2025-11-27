import os
import json
from jinja2 import Environment, FileSystemLoader

# Adjust paths relative to this script
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "capsules", "factory", "templates")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "dac_schemas")
os.makedirs(OUT_DIR, exist_ok=True)

# Ensure template dir exists (it might not if we just created the file structure)
if not os.path.exists(TEMPLATES_DIR):
    os.makedirs(TEMPLATES_DIR, exist_ok=True)

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
# We need to make sure the template file exists before running this.
# template = env.get_template("dac_schema_template.jinja2")

# Dynamic generation for all domains
DOMAINS = [
    "fusion", "grid", "wafer", "apparel", "battery",
    "motor", "magnet", "cnc", "chassis", "microgrid",
    "casting", "heat", "chem", "polymer", "metal",
    "pipeline", "qctherm", "failure",
    "robotics", "matflow", "workforce", "schedule",
    "amrsafety", "conveyor", "assembly",
    "electronics", "pcbmfg", "sensorint",
    "surface", "lifecycle",
]

def get_capsule_spec(domain):
    capsule_id = f"{domain}_v1"
    
    # Default controls
    controls = [
        {"id": "param_1", "type": "Slider", "label": "Parameter 1", "bind": "controls.p1", "props": {"min": 0, "max": 100, "step": 1}},
        {"id": "run", "type": "Button", "label": "Run Simulation", "bind": "actions.run", "props": {}}
    ]
    
    # Custom overrides for specific domains
    if domain == "fusion":
        controls = [
            {"id":"target_beta","type":"Slider","label":"Target β","bind":"controls.target_beta","props":{"min":0,"max":2,"step":0.01}},
            {"id":"ignite","type":"Button","label":"Ignite","bind":"actions.ignite","props":{}}
        ]
    
    return {
        "capsule_id": capsule_id,
        "title": f"{domain.capitalize()} Control (v1)",
        "description": f"Physics-driven control for {domain}",
        "utid_pattern": f"urn:utid:{domain}:{{node}}:{{nonce}}",
        "energy_prior": f"{domain}_v1",
        "tnn_class": f"tnn.{domain}_tnn.{domain.capitalize()}TNN",
        "controls": controls,
        "visualizer": {"type": "ReactorGauge", "config": {}}, # Default visualizer
        "gesture_map": {"run": "THUMBS_UP"}
    }

CAPSULE_SPECS = [get_capsule_spec(d) for d in DOMAINS]

def generate():
    try:
        template = env.get_template("dac_schema_template.jinja2")
        for spec in CAPSULE_SPECS:
            out_path = os.path.join(OUT_DIR, f"{spec['capsule_id']}.json")
            rendered = template.render(**spec)
            with open(out_path, "w") as f:
                f.write(rendered)
            print("Wrote", out_path)
    except Exception as e:
        print(f"Error generating schemas: {e}")

if __name__ == "__main__":
    generate()
