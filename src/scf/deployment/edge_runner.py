import onnxruntime as ort
import numpy as np
import time
import argparse
import os

class EdgeRunner:
    def __init__(self, model_path):
        print(f"🚀 Initializing Edge Runtime...")
        print(f"   Model: {model_path}")
        
        # Load ONNX Model
        # In a real edge scenario, we might use specific providers (e.g., 'TensorrtExecutionProvider', 'CPUExecutionProvider')
        self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        print("   ✅ Model Loaded.")

    def predict(self, input_data):
        """
        Run inference.
        input_data: numpy array [Batch, Features]
        """
        return self.session.run([self.output_name], {self.input_name: input_data})[0]

    def benchmark(self, num_runs=1000):
        print(f"\n⏱️  Benchmarking ({num_runs} runs)...")
        
        # Dummy Input (Float32)
        dummy_input = np.random.randn(1, 4).astype(np.float32)
        
        # Warmup
        for _ in range(10):
            self.predict(dummy_input)
            
        start_time = time.time()
        for _ in range(num_runs):
            self.predict(dummy_input)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_latency = (total_time / num_runs) * 1000 # ms
        
        print(f"   Total Time: {total_time:.4f}s")
        print(f"   Avg Latency: {avg_latency:.4f} ms")
        print(f"   Throughput: {num_runs / total_time:.2f} inf/sec")
        return avg_latency

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="model_zoo/student.onnx", help="Path to ONNX model")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark")
    args = parser.parse_args()
    
    if not os.path.exists(args.model):
        print(f"❌ Model not found: {args.model}")
        exit(1)
        
    runner = EdgeRunner(args.model)
    
    if args.benchmark:
        runner.benchmark()
    else:
        # Single run test
        res = runner.predict(np.random.randn(1, 4).astype(np.float32))
        print(f"   Test Output: {res}")
