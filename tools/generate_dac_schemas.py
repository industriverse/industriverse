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

CAPSULE_SPECS = [
    {
        "capsule_id":"fusion_v1",
        "title":"Fusion Control (v1)",
        "description":"MHD-driven fusion coil control",
        "utid_pattern":"urn:utid:fusion:{node}:{nonce}",
        "energy_prior":"fusion_v1",
        "tnn_class":"tnn.fusion_tnn.FusionHamiltonianTNN",
        "controls":[
            {"id":"target_beta","type":"Slider","label":"Target β","bind":"controls.target_beta","props":{"min":0,"max":2,"step":0.01}},
            {"id":"ignite","type":"Button","label":"Ignite","bind":"actions.ignite","props":{}}
        ],
        "visualizer":{"type":"PlasmaVisualizer","config":{"mode":"toroid","show_field_lines":True}},
        "gesture_map":{"ignite":"THUMBS_UP"}
    }
]

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
