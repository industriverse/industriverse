import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class PortalGenerator:
    def __init__(self):
        pass

    def generate_portal(self, client_config, output_dir):
        logger.info(f"Generating portal for {client_config['client_name']}...")
        
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{client_name} | Industrial Portal</title>
    <style>
        body {{
            background-color: {bg_color};
            color: {text_color};
            font-family: sans-serif;
            margin: 0;
            padding: 0;
        }}
        .header {{
            background-color: {primary_color};
            padding: 20px;
            display: flex;
            align-items: center;
        }}
        .logo {{
            font-size: 1.5rem;
            font-weight: bold;
            margin-right: 20px;
        }}
        .content {{
            padding: 40px;
        }}
        .card {{
            background: rgba(255,255,255,0.1);
            border: 1px solid {primary_color};
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">{client_name}</div>
        <div>Powered by Industriverse</div>
    </div>
    <div class="content">
        <h1>Welcome, {client_name} Operator</h1>
        <div class="card">
            <h2>Active Nodes</h2>
            <p>3 Nodes Online</p>
        </div>
        <div class="card">
            <h2>System Status</h2>
            <p>All systems nominal.</p>
        </div>
    </div>
</body>
</html>
        """
        
        html_content = html_template.format(
            client_name=client_config['client_name'],
            primary_color=client_config['theme']['primary'],
            bg_color=client_config['theme']['background'],
            text_color=client_config['theme']['text']
        )
        
        output_path = os.path.join(output_dir, "index.html")
        with open(output_path, "w") as f:
            f.write(html_content)
            
        logger.info(f"Portal generated at: {output_path}")
        return output_path

def run():
    print("\n" + "="*60)
    print(" DEMO 12: WHITE LABEL PARTNER PORTAL")
    print("="*60 + "\n")

    generator = PortalGenerator()
    output_dir = os.path.dirname(os.path.abspath(__file__))

    # Client Configuration
    client_config = {
        "client_name": "Acme Heavy Industries",
        "theme": {
            "primary": "#ff6600", # Orange
            "background": "#1a1a1a",
            "text": "#ffffff"
        }
    }

    print("--- Client Configuration ---")
    print(json.dumps(client_config, indent=2))

    print("\n--- Generating Portal ---")
    path = generator.generate_portal(client_config, output_dir)

    print(f"\nSUCCESS: Generated {path}")
    print("(You can open this file in a browser to see the branded portal)")

    print("\n" + "="*60)
    print(" DEMO COMPLETE: PORTAL GENERATED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
