from flask import Flask, request, jsonify
from datetime import datetime
import uuid
import logging
import os
from physics_engine import ProductionPhysicsEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize physics engine
physics_engine = ProductionPhysicsEngine(
    obmi_endpoint=os.getenv('OBMI_ENDPOINT', 'http://host.docker.internal:8081' ),
    m2n2_endpoint=os.getenv('M2N2_ENDPOINT', 'http://host.docker.internal:8500' ),
    well_path=os.getenv('THE_WELL_BASE_PATH', '/Users/industriverse/temp-datasets/the-well')
)

@app.route('/health', methods=['GET'])
def health_check():
    """Production health check"""
    try:
        system_status = physics_engine.get_system_status()
        
        return jsonify({
            'service': 'Shadow Twins Engine 2.0',
            'status': 'healthy',
            'version': '2.0.0-production',
            'timestamp': datetime.utcnow().isoformat(),
            'physics_engine': system_status,
            'integrations': {
                'dome_platform': 'available',
                'obmi_quantum': 'connected',
                'm2n2_evolution': 'connected',
                'well_datasets': len(system_status['available_datasets'])
            },
            'capabilities': [
                'thermal_stress_analysis',
                'vibration_analysis',
                'failure_prediction',
                'autonomous_intervention',
                'well_data_enhancement'
            ]
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/materials', methods=['GET'])
def get_materials():
    """Get available materials and their properties"""
    try:
        return jsonify({
            'materials': physics_engine.materials,
            'count': len(physics_engine.materials),
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict_failure():
    """Production failure prediction"""
    try:
        data = request.get_json()
        asset_id = data.get('asset_id', str(uuid.uuid4()))
        
        # Extract sensor data
        temperature = data.get('temperature', 20)
        vibration = data.get('vibration', 0)
        material = data.get('material', 'steel')
        frequency = data.get('frequency', 50)
        
        # Get prediction
        prediction = physics_engine.predict_failure(
            temperature=temperature,
            vibration=vibration,
            material=material,
            frequency=frequency
        )
        
        # Add metadata
        prediction['asset_id'] = asset_id
        prediction['timestamp'] = datetime.utcnow().isoformat()
        prediction['analysis_type'] = 'comprehensive_physics_well_enhanced'
        
        # Log prediction
        risk_level = "high" if prediction.get('failure_risk', 0) > 0.5 else "medium" if prediction.get('failure_risk', 0) > 0.2 else "low"
        logger.info(f"Prediction completed for {asset_id}: {risk_level} risk")
        
        return jsonify(prediction)
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        return jsonify({'error': str(e)}), 500

# OBMI Integration
from real_obmi_integration import RealOBMIIntegration
real_obmi = RealOBMIIntegration(os.getenv('OBMI_ENDPOINT', 'http://host.docker.internal:8000' ))

@app.route('/obmi/test', methods=['GET'])
def test_obmi():
    """Test OBMI connection"""
    try:
        import requests
        response = requests.get('http://host.docker.internal:8000/health', timeout=2 )
        return jsonify({
            'obmi_status': 'connected',
            'service': response.json().get('service'),
            'endpoint': 'http://host.docker.internal:8000'
        } )
    except Exception as e:
        return jsonify({'obmi_status': 'failed', 'error': str(e)}), 500

@app.route('/obmi/proof-score', methods=['POST'])
def obmi_proof_score():
    """Calculate OBMI proof score"""
    try:
        data = request.get_json()
        confidence = data.get('confidence', 0.75)
        fidelity = data.get('fidelity', 0.85)
        result = real_obmi.calculate_proof_score(confidence, fidelity)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/obmi/proof-value', methods=['POST'])
def obmi_proof_value():
    """Calculate OBMI proof value"""
    try:
        data = request.get_json()
        profit_usd = data.get('profit_usd', 1000)
        confidence = data.get('confidence', 0.75)
        processing_time = data.get('processing_time', 2.5)
        result = real_obmi.calculate_proof_value(profit_usd, confidence, processing_time)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Shadow Twins Engine 2.0 - Production Mode with The Well Integration")
    app.run(host='0.0.0.0', port=9000, debug=False)
