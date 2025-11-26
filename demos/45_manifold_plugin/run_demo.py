import http.server
import socketserver
import os
import threading
import time
import sys

# Add project root to path
sys.path.append(os.getcwd())

PORT = 8045
DIRECTORY = "demos/45_manifold_plugin"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def run():
    print("\n" + "="*60)
    print(" DEMO 45: MANIFOLD EXPLORER REACT PLUGIN")
    print("="*60 + "\n")
    
    def start_server():
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Serving Plugin at http://localhost:{PORT}")
            httpd.serve_forever()

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    print("Simulating Component Mount...")
    time.sleep(1)
    print("Component Mounted. WebGL Context Initialized.")
    print("User Interaction: Zoom In -> Cluster Selected.")
    
    time.sleep(3)
    print("\n" + "="*60)
    print(" DEMO COMPLETE: PLUGIN RENDERED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
