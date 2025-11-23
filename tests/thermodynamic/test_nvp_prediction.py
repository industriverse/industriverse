import unittest
from datetime import datetime, timedelta
from src.core.nvp.nvp_predictor import NVPPredictor
from src.core.nvp.schema import TelemetryVector

class TestNVPPredictor(unittest.TestCase):
    
    def setUp(self):
        self.predictor = NVPPredictor(context_window=5)
        self.node_id = "test_gpu_01"
        
    def test_prediction_flow(self):
        # Feed some data with a rising temperature trend
        base_time = datetime.now()
        
        for i in range(5):
            vec = TelemetryVector(
                timestamp=base_time + timedelta(seconds=i),
                node_id=self.node_id,
                voltage=1.0,
                current=10.0,
                temperature_c=40.0 + i * 2.0, # Rising 2C per second
                utilization=0.5,
                error_rate=0.0
            )
            self.predictor.add_observation(vec)
            
        # Predict 1 second ahead
        result = self.predictor.predict_next(horizon_seconds=1.0)
        
        # Expect temperature to be around 40 + 4*2 + 2 = 50C
        # Allow for noise
        self.assertTrue(48.0 <= result.predicted_vector.temperature_c <= 52.0)
        
        # Check failure probability (should be low at 50C)
        self.assertTrue(result.failure_probability < 0.1)
        
    def test_high_temp_failure_risk(self):
         # Feed data near critical temp
        base_time = datetime.now()
        for i in range(5):
            vec = TelemetryVector(
                timestamp=base_time + timedelta(seconds=i),
                node_id=self.node_id,
                voltage=1.0,
                current=10.0,
                temperature_c=80.0 + i * 2.0, # Rising to 88C
                utilization=0.8,
                error_rate=0.0
            )
            self.predictor.add_observation(vec)
            
        result = self.predictor.predict_next(horizon_seconds=1.0)
        # Temp should be ~90C, failure prob should be high (>0.5)
        self.assertTrue(result.predicted_vector.temperature_c > 85.0)
        self.assertTrue(result.failure_probability > 0.5)

if __name__ == '__main__':
    unittest.main()
