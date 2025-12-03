import ast
import unittest
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ModelEval")

class TestModelEvaluation(unittest.TestCase):
    """
    Evaluation Suite for GenN and TNN.
    """
    
    def test_ast_correctness(self):
        """
        Verifies that 'generated' code is syntactically valid Python.
        """
        logger.info("🧪 Testing AST Correctness...")
        
        # Mock GenN output (In real life, this comes from the model)
        generated_code_samples = [
            "def optimize_grid(): return True",
            "import os; print(os.getcwd())",
            "x = [i**2 for i in range(10)]"
        ]
        
        for i, code in enumerate(generated_code_samples):
            try:
                ast.parse(code)
                logger.info(f"   ✅ Sample {i} is valid Python.")
            except SyntaxError as e:
                self.fail(f"Sample {i} failed AST parsing: {e}")

    def test_resource_usage_prediction(self):
        """
        Verifies that TNN predicts energy usage within reasonable bounds.
        """
        logger.info("🧪 Testing Resource Usage Prediction...")
        
        # Mock TNN output (In real life, this comes from the model)
        # We expect energy cost in Joules to be positive and reasonable
        predicted_joules = [10.5, 0.01, 100.0] 
        
        for j in predicted_joules:
            self.assertGreaterEqual(j, 0.0, "Predicted energy cannot be negative")
            self.assertLess(j, 10000.0, "Predicted energy exceeds safety threshold")
            logger.info(f"   ✅ Prediction {j}J is within bounds.")

if __name__ == "__main__":
    unittest.main()
