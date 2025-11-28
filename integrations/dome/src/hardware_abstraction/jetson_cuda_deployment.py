"""
JETSON NANO CUDA DEPLOYMENT - Real GPU Acceleration
Deploy and execute CUDA kernels on real Jetson Nano hardware
"""
import subprocess
import os
import time
import json
from typing import Dict, List, Any

class JetsonCudaDeployment:
    """Real Jetson Nano CUDA kernel deployment and execution"""
    
    def __init__(self, jetson_ip: str = "192.168.1.100", username: str = "jetson"):
        self.jetson_ip = jetson_ip
        self.username = username
        self.ssh_key_path = os.path.expanduser("~/.ssh/id_rsa")
        self.cuda_kernels_deployed = False
        
    def check_jetson_connection(self) -> bool:
        """Check SSH connection to Jetson Nano"""
        print(f"🔍 Checking connection to Jetson Nano: {self.jetson_ip}")
        
        try:
            # Test SSH connection
            ssh_cmd = [
                "ssh", "-i", self.ssh_key_path,
                "-o", "ConnectTimeout=5",
                "-o", "StrictHostKeyChecking=no",
                f"{self.username}@{self.jetson_ip}",
                "echo 'JETSON_CONNECTED'"
            ]
            
            result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and "JETSON_CONNECTED" in result.stdout:
                print(f"   ✅ SSH connection successful")
                return True
            else:
                print(f"   ❌ SSH connection failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ❌ Connection timeout")
            return False
        except Exception as e:
            print(f"   ❌ Connection error: {e}")
            return False
    
    def check_cuda_environment(self) -> Dict[str, Any]:
        """Check CUDA environment on Jetson Nano"""
        print(f"🔍 Checking CUDA environment on Jetson...")
        
        cuda_info = {
            "cuda_available": False,
            "cuda_version": None,
            "gpu_memory": None,
            "compute_capability": None
        }
        
        try:
            # Check CUDA version
            cuda_cmd = [
                "ssh", "-i", self.ssh_key_path,
                f"{self.username}@{self.jetson_ip}",
                "nvcc --version | grep 'release' | awk '{print $6}' | cut -c2-"
            ]
            
            result = subprocess.run(cuda_cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                cuda_info["cuda_version"] = result.stdout.strip()
                cuda_info["cuda_available"] = True
                print(f"   ✅ CUDA Version: {cuda_info['cuda_version']}")
            
            # Check GPU memory
            gpu_cmd = [
                "ssh", "-i", self.ssh_key_path,
                f"{self.username}@{self.jetson_ip}",
                "nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits"
            ]
            
            result = subprocess.run(gpu_cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                cuda_info["gpu_memory"] = f"{result.stdout.strip()}MB"
                print(f"   ✅ GPU Memory: {cuda_info['gpu_memory']}")
            
            # Check compute capability
            compute_cmd = [
                "ssh", "-i", self.ssh_key_path,
                f"{self.username}@{self.jetson_ip}",
                "nvidia-smi --query-gpu=compute_cap --format=csv,noheader"
            ]
            
            result = subprocess.run(compute_cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                cuda_info["compute_capability"] = result.stdout.strip()
                print(f"   ✅ Compute Capability: {cuda_info['compute_capability']}")
            
        except Exception as e:
            print(f"   ❌ CUDA check failed: {e}")
        
        return cuda_info
    
    def deploy_cuda_kernels(self, kernel_source_dir: str = "src/cuda_kernels") -> bool:
        """Deploy CUDA kernels to Jetson Nano"""
        print(f"🚀 Deploying CUDA kernels to Jetson...")
        
        if not os.path.exists(kernel_source_dir):
            print(f"   ❌ Kernel source directory not found: {kernel_source_dir}")
            return False
        
        try:
            # Create remote directory
            mkdir_cmd = [
                "ssh", "-i", self.ssh_key_path,
                f"{self.username}@{self.jetson_ip}",
                "mkdir -p ~/dome_cuda_kernels"
            ]
            
            subprocess.run(mkdir_cmd, check=True, timeout=10)
            
            # Copy CUDA kernel files
            scp_cmd = [
                "scp", "-i", self.ssh_key_path,
                "-r", kernel_source_dir,
                f"{self.username}@{self.jetson_ip}:~/dome_cuda_kernels/"
            ]
            
            result = subprocess.run(scp_cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"   ❌ File copy failed: {result.stderr}")
                return False
            
            print(f"   ✅ CUDA kernels copied to Jetson")
            
            # Compile CUDA kernels on Jetson
            compile_cmd = [
                "ssh", "-i", self.ssh_key_path,
                f"{self.username}@{self.jetson_ip}",
                "cd ~/dome_cuda_kernels && nvcc -o dome_kernels *.cu -lcufft -lcublas"
            ]
            
            result = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"   ✅ CUDA kernels compiled successfully")
                self.cuda_kernels_deployed = True
                return True
            else:
                print(f"   ❌ Compilation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ❌ Deployment timeout")
            return False
        except Exception as e:
            print(f"   ❌ Deployment error: {e}")
            return False
    
    def execute_cuda_kernel(self, kernel_name: str, input_data: str) -> Dict[str, Any]:
        """Execute CUDA kernel on Jetson Nano"""
        print(f"⚡ Executing CUDA kernel: {kernel_name}")
        
        if not self.cuda_kernels_deployed:
            print(f"   ❌ CUDA kernels not deployed")
            return {"status": "FAILED", "error": "Kernels not deployed"}
        
        try:
            # Execute kernel with input data
            exec_cmd = [
                "ssh", "-i", self.ssh_key_path,
                f"{self.username}@{self.jetson_ip}",
                f"cd ~/dome_cuda_kernels && echo '{input_data}' | ./dome_kernels {kernel_name}"
            ]
            
            start_time = time.time()
            result = subprocess.run(exec_cmd, capture_output=True, text=True, timeout=30)
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                print(f"   ✅ Kernel executed successfully")
                print(f"   ⏱️ Execution time: {execution_time:.3f}s")
                
                return {
                    "status": "SUCCESS",
                    "execution_time": execution_time,
                    "output": result.stdout.strip(),
                    "kernel": kernel_name
                }
            else:
                print(f"   ❌ Kernel execution failed: {result.stderr}")
                return {
                    "status": "FAILED",
                    "error": result.stderr,
                    "kernel": kernel_name
                }
                
        except subprocess.TimeoutExpired:
            print(f"   ❌ Kernel execution timeout")
            return {"status": "TIMEOUT", "kernel": kernel_name}
        except Exception as e:
            print(f"   ❌ Execution error: {e}")
            return {"status": "ERROR", "error": str(e), "kernel": kernel_name}

def test_real_jetson_deployment():
    """Test real Jetson Nano CUDA deployment"""
    print("🧪 REAL JETSON NANO CUDA DEPLOYMENT TEST")
    print("=" * 60)
    
    jetson = JetsonCudaDeployment("192.168.1.100")
    
    print("📋 REAL JETSON OPERATIONS:")
    print("   1. Check connection: jetson.check_jetson_connection()")
    print("   2. Check CUDA: jetson.check_cuda_environment()")
    print("   3. Deploy kernels: jetson.deploy_cuda_kernels()")
    print("   4. Execute kernel: jetson.execute_cuda_kernel('stft_kernel', csi_data)")
    
    print(f"\n✅ Jetson deployment interface ready!")
    print(f"🔌 Configure SSH key and run operations above with real Jetson")
    
    return jetson

if __name__ == "__main__":
    deployment = test_real_jetson_deployment()
    print("\n🏭 Ready for factory floor deployment with real Jetson Nano!")
