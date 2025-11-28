import http.server
import socketserver
import os
import threading
import time
import webbrowser

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def run():
    print("\n" + "="*60)
    print(" DEMO 11: CAPSULE PIN (WEB WIDGET)")
    print("="*60 + "\n")

    print(f"Serving demo at http://localhost:{PORT}")
    print("Opening browser...")

    # Start server in a thread
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        # Open browser automatically
        # webbrowser.open(f"http://localhost:{PORT}") # Disabled for headless env, but good for real demo
        
        print("Server running. Press Ctrl+C to stop (simulated for 5 seconds).")
        
        # Run for 5 seconds then exit
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.start()
        
        time.sleep(5)
        
        print("Shutting down server...")
        httpd.shutdown()
        server_thread.join()

    print("\n" + "="*60)
    print(" DEMO COMPLETE: WIDGET SERVED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
