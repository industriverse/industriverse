import http.server
import socketserver
import os
import threading
import time
import sys

# Add project root to path
sys.path.append(os.getcwd())

PORT = 8035
DIRECTORY = "demos/35_attention_overlay"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def run():
    print("\n" + "="*60)
    print(" DEMO 35: ATTENTION VISUALIZATION OVERLAY")
    print("="*60 + "\n")
    
    def start_server():
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Serving Attention Overlay at http://localhost:{PORT}")
            httpd.serve_forever()

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    print("Simulating Attention Mechanism...")
    time.sleep(1)
    print("Attention Shift -> Turbine A (Entropy: 2.4)")
    time.sleep(1)
    print("Attention Shift -> Generator B (Entropy: 3.1)")
    
    time.sleep(3)
    print("\n" + "="*60)
    print(" DEMO COMPLETE: ATTENTION VISUALIZED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
