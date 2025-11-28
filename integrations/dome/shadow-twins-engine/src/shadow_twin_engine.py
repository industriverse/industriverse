from flask import Flask, request, jsonify
import requests
import json
import time
from datetime import datetime, timedelta
import threading

app = Flask(__name__)

# Configuration
DOME_ENDPOINT = "http://172.17.0.3:8080"
M2N2_ENDPOINT = "http://localhost:8500"
OBMI_ENDPOINT = "http://localhost:8081"

class ShadowTwinEngine:
    def __init__(self ):
        self.predictions = {}
        self.interventions = {}
        self.running = True
        
    def predict_failure(self, asset_data):
        """Core prediction logic using OBMI quantum operators"""
        try:
            # Get quantum enhancement from OBMI
            obmi_response = requests.post(f"{OBMI_ENDPOINT}/enhance", 
                                        json={"data": asset_data}, timeout=5)
            
            if obmi_response.status_code == 200:
                enhanced_data = obmi_response.json()
                
                # Use M2N2 for evolution-based prediction
                m2n2_response = requests.post(f"{M2N2_ENDPOINT}/evolve",
                                            json={"input": enhanced_data}, timeout=5)
                
                if m2n2_response.status_code == 200:
                    evolution_result = m2n2_response.json()
                    
                    # Calculate failure probability
                    failure_risk = 1.0 - evolution_result.get('fitness_improvement', 0.25)
                    
                    return {
                        "failure_risk": min(failure_risk, 0.95),
                        "prediction_confidence": 0.85,
                        "time_to_failure_hours": 24 * (1 - failure_risk),
                        "recommended_actions": self._get_recommendations(failure_risk)
                    }
        except Exception as e:
            print(f"Prediction error: {e}")
            
        return {"failure_risk": 0.1, "prediction_confidence": 0.5}
    
    def _get_recommendations(self, risk):
        if risk > 0.8:
            return ["IMMEDIATE_SHUTDOWN", "EMERGENCY_MAINTENANCE"]
        elif risk > 0.5:
            return ["SCHEDULE_MAINTENANCE", "INCREASE_MONITORING"]
        else:
            return ["CONTINUE_NORMAL_OPERATION"]

engine = ShadowTwinEngine()

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Shadow Twin Engine 2.0',
        'version': '2.0.0',
        'dome_connected': check_connection(DOME_ENDPOINT),
        'm2n2_connected': check_connection(M2N2_ENDPOINT),
        'obmi_connected': check_connection(OBMI_ENDPOINT),
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json or {}
    asset_id = data.get('asset_id', 'unknown')
    
    prediction = engine.predict_failure(data)
    prediction['asset_id'] = asset_id
    prediction['timestamp'] = datetime.utcnow().isoformat()
    
    return jsonify(prediction)

def check_connection(endpoint):
    try:
        response = requests.get(f"{endpoint}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

if __name__ == '__main__':
    print("🔮 Shadow Twin Engine 2.0 Starting...")
    print(f"🏛️ Dome: {DOME_ENDPOINT}")
    print(f"🧬 M2N2: {M2N2_ENDPOINT}")
    print(f"⚛️ OBMI: {OBMI_ENDPOINT}")
    app.run(host='0.0.0.0', port=9000, debug=False)
