from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class OBMIHandler(BaseHTTPRequestHandler ):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {'status': 'healthy', 'service': 'OBMI Mock', 'version': '1.0'}
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {'result': 'success', 'score': 0.95}
        self.wfile.write(json.dumps(response).encode())

print('OBMI Mock Service starting on port 8000...')
server = HTTPServer(('localhost', 8000), OBMIHandler)
server.serve_forever()
