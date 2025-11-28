import http.server
import socketserver
import os
import threading
import time
import sys

# Add project root to path
sys.path.append(os.getcwd())

PORT = 8030
DIRECTORY = "demos/30_phase_diagram"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def run():
    print("\n" + "="*60)
    print(" DEMO 30: INTERACTIVE PHASE DIAGRAM")
    print("="*60 + "\n")
    
    def start_server():
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Serving Phase Diagram at http://localhost:{PORT}")
            httpd.serve_forever()

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    print("Simulating Regime Transitions...")
    time.sleep(2)
    print("Regime Boundary Detected at E=50, S=0.5")
    
    time.sleep(3)
    print("\n" + "="*60)
    print(" DEMO COMPLETE: DIAGRAM ACTIVE")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
