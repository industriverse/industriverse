from flask import Flask, jsonify
import time
import random

app = Flask(__name__)

# Mock System State
system_state = {
    "status": "ONLINE",
    "mode": "AUTONOMOUS",
    "uptime_seconds": 0,
    "start_time": time.time()
}

@app.route('/api/status', methods=['GET'])
def get_status():
    system_state['uptime_seconds'] = time.time() - system_state['start_time']
    return jsonify(system_state)

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    # Mock real-time metrics
    return jsonify({
        "power_w": random.uniform(100, 200),
        "temp_c": random.uniform(40, 60),
        "entropy_rate": random.uniform(0.1, 0.5)
    })

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    return jsonify([
        {"id": 1, "level": "INFO", "message": "System started successfully"},
        {"id": 2, "level": "WARNING", "message": "Slight temp increase detected"}
    ])

if __name__ == '__main__':
    print("🏭 Dark Factory OS - Local Dashboard Starting...")
    app.run(host='0.0.0.0', port=8080)
