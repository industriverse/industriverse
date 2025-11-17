"""
3D Gaussian Splatting Trainer for Shadow Twins

Trains photorealistic 3DGS models from Shadow Twin point clouds.

Architecture:
    Point Cloud (.ply) → 3DGS Training → Trained Model → .spx Export

Training Pipeline:
    1. Load point cloud + camera poses (COLMAP)
    2. Initialize 3D Gaussians from point cloud
    3. Optimize Gaussian parameters (position, covariance, color, opacity)
    4. Densify/prune Gaussians during training
    5. Export to .spx format (Reall3DViewer native)

Performance:
    - Training time: ~30 min per asset (GPU-accelerated)
    - Model size: ~10-50 MB (compressed .spx)
    - Rendering: ≥30 fps at 1080p
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TrainingConfig:
    """3DGS training configuration"""
    iterations: int = 30000
    save_iterations: list = None
    test_iterations: list = None
    resolution: int = 1  # 1, 2, 4, or 8
    sh_degree: int = 3  # Spherical harmonics degree
    white_background: bool = False
    use_gpu: bool = True
    data_device: str = "cuda"  # "cuda" or "cpu"
    
    # Learning rates
    position_lr_init: float = 0.00016
    position_lr_final: float = 0.0000016
    position_lr_max_steps: int = 30000
    feature_lr: float = 0.0025
    opacity_lr: float = 0.05
    scaling_lr: float = 0.005
    rotation_lr: float = 0.001
    
    # Densification
    densify_from_iter: int = 500
    densify_until_iter: int = 15000
    densify_grad_threshold: float = 0.0002
    densification_interval: int = 100
    
    # Optimization
    lambda_dssim: float = 0.2  # SSIM loss weight
    percent_dense: float = 0.01
    
    def __post_init__(self):
        if self.save_iterations is None:
            self.save_iterations = [7000, 30000]
        if self.test_iterations is None:
            self.test_iterations = [7000, 30000]


@dataclass
class TrainingOutput:
    """3DGS training output"""
    model_path: str
    iteration: int
    point_count: int
    training_time_seconds: float
    final_loss: float


class GaussianSplattingTrainer:
    """
    Trains 3D Gaussian Splatting models from Shadow Twin point clouds.
    
    Uses the official Gaussian Splatting implementation:
    https://github.com/graphdeco-inria/gaussian-splatting
    
    Workflow:
        1. Prepare COLMAP dataset structure
        2. Run 3DGS training
        3. Export trained model
        4. Convert to .spx format (Reall3DViewer)
    """
    
    def __init__(
        self,
        gaussian_splatting_repo: str = "/opt/gaussian-splatting",
        output_dir: str = "/tmp/shadow_twin_3dgs",
        gsbox_executable: str = "gsbox"  # For .spx conversion
    ):
        self.gs_repo = Path(gaussian_splatting_repo)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.gsbox_executable = gsbox_executable
        
        # Verify Gaussian Splatting repo exists
        if not self.gs_repo.exists():
            logger.warning(f"Gaussian Splatting repo not found at {self.gs_repo}")
            logger.warning("Clone from: https://github.com/graphdeco-inria/gaussian-splatting")
        
        logger.info(f"GaussianSplattingTrainer initialized")
        logger.info(f"GS repo: {self.gs_repo}")
        logger.info(f"Output dir: {self.output_dir}")
    
    def train_from_shadow_twin(
        self,
        shadow_twin_id: str,
        pointcloud_path: str,
        sparse_reconstruction_path: Optional[str] = None,
        config: Optional[TrainingConfig] = None
    ) -> TrainingOutput:
        """
        Train 3DGS model from Shadow Twin point cloud.
        
        Args:
            shadow_twin_id: Unique Shadow Twin identifier
            pointcloud_path: Path to .ply point cloud
            sparse_reconstruction_path: Path to COLMAP sparse reconstruction (optional)
            config: Training configuration
            
        Returns:
            TrainingOutput with model path and metadata
        """
        if config is None:
            config = TrainingConfig()
        
        logger.info(f"Training 3DGS model for Shadow Twin: {shadow_twin_id}")
        
        # Prepare dataset directory
        dataset_dir = self.output_dir / shadow_twin_id / "dataset"
        dataset_dir.mkdir(parents=True, exist_ok=True)
        
        # Create COLMAP dataset structure
        self._prepare_colmap_dataset(
            dataset_dir,
            pointcloud_path,
            sparse_reconstruction_path
        )
        
        # Run 3DGS training
        model_path = self.output_dir / shadow_twin_id / "model"
        model_path.mkdir(parents=True, exist_ok=True)
        
        training_output = self._run_training(
            dataset_dir,
            model_path,
            config
        )
        
        logger.info(f"Training complete: {training_output.model_path}")
        
        return training_output
    
    def export_to_spx(
        self,
        shadow_twin_id: str,
        model_path: str,
        iteration: int = 30000
    ) -> str:
        """
        Export trained 3DGS model to .spx format (Reall3DViewer native).
        
        Uses gsbox tool: https://github.com/gotoeasy/gsbox
        
        Args:
            shadow_twin_id: Unique Shadow Twin identifier
            model_path: Path to trained 3DGS model
            iteration: Training iteration to export
            
        Returns:
            Path to exported .spx file
        """
        logger.info(f"Exporting model to .spx format...")
        
        # Find .ply file in model directory
        ply_path = Path(model_path) / f"point_cloud/iteration_{iteration}/point_cloud.ply"
        
        if not ply_path.exists():
            raise FileNotFoundError(f"Model not found: {ply_path}")
        
        # Output .spx path
        spx_path = self.output_dir / shadow_twin_id / f"{shadow_twin_id}.spx"
        
        # Convert .ply to .spx using gsbox
        cmd = [
            self.gsbox_executable,
            "p2x",
            "-i", str(ply_path),
            "-o", str(spx_path)
        ]
        
        logger.info(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
        logger.info(f"Exported to: {spx_path}")
        
        return str(spx_path)
    
    def _prepare_colmap_dataset(
        self,
        dataset_dir: Path,
        pointcloud_path: str,
        sparse_reconstruction_path: Optional[str]
    ):
        """
        Prepare COLMAP dataset structure for 3DGS training.
        
        Expected structure:
            dataset/
            ├── images/          (optional, for photogrammetry)
            └── sparse/
                └── 0/
                    ├── cameras.bin
                    ├── images.bin
                    └── points3D.bin
        """
        logger.info("Preparing COLMAP dataset structure...")
        
        sparse_dir = dataset_dir / "sparse" / "0"
        sparse_dir.mkdir(parents=True, exist_ok=True)
        
        if sparse_reconstruction_path:
            # Copy COLMAP sparse reconstruction
            import shutil
            
            src_dir = Path(sparse_reconstruction_path)
            for file in ["cameras.bin", "images.bin", "points3D.bin"]:
                src_file = src_dir / file
                if src_file.exists():
                    shutil.copy(src_file, sparse_dir / file)
                    logger.info(f"Copied {file}")
        else:
            # Create minimal COLMAP structure from point cloud only
            logger.warning("No sparse reconstruction provided, creating minimal structure")
            self._create_minimal_colmap(sparse_dir, pointcloud_path)
        
        logger.info("COLMAP dataset prepared")
    
    def _create_minimal_colmap(self, sparse_dir: Path, pointcloud_path: str):
        """
        Create minimal COLMAP structure when no camera poses available.
        
        This is a fallback for LiDAR/CAD data without images.
        Creates a single virtual camera looking at the point cloud.
        """
        import struct
        import numpy as np
        
        # Read point cloud to get bounding box
        try:
            import open3d as o3d
            pcd = o3d.io.read_point_cloud(pointcloud_path)
            points = np.asarray(pcd.points)
            
            # Calculate bounding box center
            bbox_center = points.mean(axis=0)
            bbox_size = points.max(axis=0) - points.min(axis=0)
            camera_distance = np.linalg.norm(bbox_size) * 2
            
        except ImportError:
            logger.error("open3d not installed. Install with: pip install open3d")
            raise
        
        # Create cameras.bin (single SIMPLE_PINHOLE camera)
        cameras_path = sparse_dir / "cameras.bin"
        with open(cameras_path, 'wb') as f:
            # Header: num_cameras
            f.write(struct.pack('Q', 1))
            
            # Camera: camera_id, model, width, height, params
            f.write(struct.pack('I', 1))  # camera_id
            f.write(struct.pack('i', 0))  # model (SIMPLE_PINHOLE)
            f.write(struct.pack('Q', 1920))  # width
            f.write(struct.pack('Q', 1080))  # height
            f.write(struct.pack('d', 1000.0))  # focal length
            f.write(struct.pack('d', 960.0))  # cx
            f.write(struct.pack('d', 540.0))  # cy
        
        # Create images.bin (single virtual image)
        images_path = sparse_dir / "images.bin"
        with open(images_path, 'wb') as f:
            # Header: num_images
            f.write(struct.pack('Q', 1))
            
            # Image: image_id, qw, qx, qy, qz, tx, ty, tz, camera_id, name
            f.write(struct.pack('I', 1))  # image_id
            
            # Quaternion (identity rotation)
            f.write(struct.pack('d', 1.0))  # qw
            f.write(struct.pack('d', 0.0))  # qx
            f.write(struct.pack('d', 0.0))  # qy
            f.write(struct.pack('d', 0.0))  # qz
            
            # Translation (camera position)
            f.write(struct.pack('d', bbox_center[0]))  # tx
            f.write(struct.pack('d', bbox_center[1]))  # ty
            f.write(struct.pack('d', bbox_center[2] + camera_distance))  # tz
            
            f.write(struct.pack('I', 1))  # camera_id
            
            # Image name (null-terminated string)
            name = "virtual_image.jpg\x00"
            f.write(name.encode())
            
            # Num points (0)
            f.write(struct.pack('Q', 0))
        
        # Create points3D.bin (copy from input point cloud)
        # For simplicity, we'll create an empty file (3DGS will initialize from point cloud)
        points3d_path = sparse_dir / "points3D.bin"
        with open(points3d_path, 'wb') as f:
            # Header: num_points
            f.write(struct.pack('Q', 0))
        
        logger.info("Created minimal COLMAP structure")
    
    def _run_training(
        self,
        dataset_dir: Path,
        model_path: Path,
        config: TrainingConfig
    ) -> TrainingOutput:
        """
        Run 3DGS training.
        
        Calls train.py from Gaussian Splatting repo.
        """
        import time
        
        logger.info("Starting 3DGS training...")
        start_time = time.time()
        
        # Build training command
        train_script = self.gs_repo / "train.py"
        
        cmd = [
            "python", str(train_script),
            "-s", str(dataset_dir),
            "-m", str(model_path),
            "--iterations", str(config.iterations),
            "--save_iterations"] + [str(i) for i in config.save_iterations] + [
            "--test_iterations"] + [str(i) for i in config.test_iterations] + [
            "--resolution", str(config.resolution),
            "--sh_degree", str(config.sh_degree),
            "--data_device", config.data_device,
            "--position_lr_init", str(config.position_lr_init),
            "--position_lr_final", str(config.position_lr_final),
            "--position_lr_max_steps", str(config.position_lr_max_steps),
            "--feature_lr", str(config.feature_lr),
            "--opacity_lr", str(config.opacity_lr),
            "--scaling_lr", str(config.scaling_lr),
            "--rotation_lr", str(config.rotation_lr),
            "--densify_from_iter", str(config.densify_from_iter),
            "--densify_until_iter", str(config.densify_until_iter),
            "--densify_grad_threshold", str(config.densify_grad_threshold),
            "--densification_interval", str(config.densification_interval),
            "--lambda_dssim", str(config.lambda_dssim),
            "--percent_dense", str(config.percent_dense)
        ]
        
        if config.white_background:
            cmd.append("--white_background")
        
        logger.info(f"Running: {' '.join(cmd)}")
        
        # Run training
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Training failed: {result.stderr}")
            raise RuntimeError(f"3DGS training failed: {result.stderr}")
        
        training_time = time.time() - start_time
        
        logger.info(f"Training completed in {training_time:.1f}s")
        
        # Parse training output for final loss
        final_loss = self._parse_final_loss(result.stdout)
        
        # Count Gaussians in final model
        point_count = self._count_gaussians(model_path, config.iterations)
        
        return TrainingOutput(
            model_path=str(model_path),
            iteration=config.iterations,
            point_count=point_count,
            training_time_seconds=training_time,
            final_loss=final_loss
        )
    
    def _parse_final_loss(self, stdout: str) -> float:
        """Parse final loss from training output"""
        # Look for last "Loss:" line
        for line in reversed(stdout.split('\n')):
            if "Loss:" in line:
                try:
                    loss_str = line.split("Loss:")[1].split()[0]
                    return float(loss_str)
                except (IndexError, ValueError):
                    pass
        return 0.0
    
    def _count_gaussians(self, model_path: Path, iteration: int) -> int:
        """Count number of Gaussians in trained model"""
        ply_path = model_path / f"point_cloud/iteration_{iteration}/point_cloud.ply"
        
        if not ply_path.exists():
            return 0
        
        try:
            import open3d as o3d
            pcd = o3d.io.read_point_cloud(str(ply_path))
            return len(pcd.points)
        except ImportError:
            logger.error("open3d not installed. Install with: pip install open3d")
            return 0


# Example usage
if __name__ == "__main__":
    trainer = GaussianSplattingTrainer()
    
    # Train from Shadow Twin point cloud
    output = trainer.train_from_shadow_twin(
        shadow_twin_id="motor_001",
        pointcloud_path="/tmp/shadow_twin_pointclouds/motor_001/pointcloud.ply",
        sparse_reconstruction_path="/tmp/shadow_twin_pointclouds/motor_001/sparse/0"
    )
    
    print(f"Model saved to: {output.model_path}")
    print(f"Training time: {output.training_time_seconds:.1f}s")
    print(f"Final loss: {output.final_loss:.4f}")
    print(f"Gaussian count: {output.point_count}")
    
    # Export to .spx
    spx_path = trainer.export_to_spx(
        shadow_twin_id="motor_001",
        model_path=output.model_path,
        iteration=output.iteration
    )
    
    print(f"Exported to: {spx_path}")
