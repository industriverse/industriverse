from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class OBMIHandler(BaseHTTPRequestHandler ):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        if self.path == '/health':
            response = {'status': 'healthy', 'service': 'OBMI Mock', 'version': '1.0'}
        elif self.path == '/kernel/execute':
            response = {'result': 'success', 'status': 'executed'}
        else:
            response = {'status': 'healthy', 'service': 'OBMI Mock', 'version': '1.0'}
            
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8')) if content_length > 0 else {}
            
            if self.path == '/kernel/execute':
                response = {
                    'result': 'success',
                    'output': 'OBMI quantum calculation completed',
                    'score': 0.95,
                    'status': 'executed'
                }
            else:
                material = data.get('material', 'unknown')
                score = 0.95 if material in ['titanium', 'steel', 'aluminum'] else 0.75
                
                response = {
                    'result': 'success', 
                    'score': score,
                    'material': material,
                    'timestamp': '2025-09-24T15:30:00Z'
                }
        except Exception as e:
            response = {'result': 'error', 'score': 0.0, 'error': str(e)}
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

print('OBMI Mock Service starting on port 8000...')
server = HTTPServer(('localhost', 8000), OBMIHandler)
server.serve_forever()
