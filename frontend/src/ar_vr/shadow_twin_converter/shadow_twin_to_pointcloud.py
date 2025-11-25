"""
Shadow Twin to Point Cloud Converter

Converts Shadow Twin sensor data (LiDAR, photogrammetry, CAD) into 3D point clouds
for Gaussian Splatting training.

Architecture:
    Shadow Twin Data → Point Cloud (.ply) → COLMAP SfM → 3DGS Training

Supported Input Sources:
    1. LiDAR scans (.las, .laz, .pcd)
    2. Multi-view images (JPEG, PNG) → COLMAP photogrammetry
    3. CAD models (.obj, .stl, .ply) → Point cloud sampling
    4. Sensor fusion (combine multiple sources)
"""

import os
import json
import numpy as np
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ShadowTwinData:
    """Shadow Twin data structure"""
    shadow_twin_id: str
    asset_type: str  # e.g., "motor", "pump", "conveyor"
    data_source: str  # "lidar", "images", "cad", "fusion"
    data_path: str
    metadata: Dict


@dataclass
class PointCloudOutput:
    """Point cloud output structure"""
    ply_path: str
    camera_poses_path: Optional[str]  # For photogrammetry
    sparse_reconstruction_path: Optional[str]  # COLMAP output
    point_count: int
    bounding_box: Tuple[np.ndarray, np.ndarray]  # (min, max)


class ShadowTwinPointCloudConverter:
    """
    Converts Shadow Twin data to point clouds for 3D Gaussian Splatting.
    
    Workflow:
        1. Load Shadow Twin data (LiDAR/images/CAD)
        2. Convert to point cloud format
        3. Run COLMAP (if photogrammetry)
        4. Export .ply for 3DGS training
    """
    
    def __init__(
        self,
        output_dir: str = "/tmp/shadow_twin_pointclouds",
        colmap_executable: str = "colmap",
        use_gpu: bool = True
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.colmap_executable = colmap_executable
        self.use_gpu = use_gpu
        
        logger.info(f"ShadowTwinPointCloudConverter initialized")
        logger.info(f"Output directory: {self.output_dir}")
    
    def convert(self, shadow_twin: ShadowTwinData) -> PointCloudOutput:
        """
        Convert Shadow Twin data to point cloud.
        
        Args:
            shadow_twin: Shadow Twin data structure
            
        Returns:
            PointCloudOutput with paths and metadata
        """
        logger.info(f"Converting Shadow Twin: {shadow_twin.shadow_twin_id}")
        logger.info(f"Data source: {shadow_twin.data_source}")
        
        if shadow_twin.data_source == "lidar":
            return self._convert_lidar(shadow_twin)
        elif shadow_twin.data_source == "images":
            return self._convert_images_colmap(shadow_twin)
        elif shadow_twin.data_source == "cad":
            return self._convert_cad(shadow_twin)
        elif shadow_twin.data_source == "fusion":
            return self._convert_fusion(shadow_twin)
        else:
            raise ValueError(f"Unsupported data source: {shadow_twin.data_source}")
    
    def _convert_lidar(self, shadow_twin: ShadowTwinData) -> PointCloudOutput:
        """
        Convert LiDAR scan to point cloud.
        
        Supports: .las, .laz (LAStools), .pcd (PCL)
        """
        logger.info("Converting LiDAR scan to point cloud...")
        
        lidar_path = Path(shadow_twin.data_path)
        output_path = self.output_dir / shadow_twin.shadow_twin_id / "pointcloud.ply"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check file format
        if lidar_path.suffix in ['.las', '.laz']:
            # Use laspy to read LAS/LAZ files
            try:
                import laspy
                
                # Read LAS file
                las = laspy.read(str(lidar_path))
                points = np.vstack((las.x, las.y, las.z)).T
                
                # Get colors if available
                if hasattr(las, 'red'):
                    colors = np.vstack((
                        las.red / 65535.0,
                        las.green / 65535.0,
                        las.blue / 65535.0
                    )).T
                else:
                    # Default gray color
                    colors = np.ones_like(points) * 0.5
                
                # Write PLY file
                self._write_ply(output_path, points, colors)
                
                logger.info(f"Converted {len(points)} LiDAR points to PLY")
                
            except ImportError:
                logger.error("laspy not installed. Install with: pip install laspy")
                raise
                
        elif lidar_path.suffix == '.pcd':
            # Use open3d to read PCD files
            try:
                import open3d as o3d
                
                # Read PCD file
                pcd = o3d.io.read_point_cloud(str(lidar_path))
                
                # Write PLY file
                o3d.io.write_point_cloud(str(output_path), pcd)
                
                points = np.asarray(pcd.points)
                logger.info(f"Converted {len(points)} PCD points to PLY")
                
            except ImportError:
                logger.error("open3d not installed. Install with: pip install open3d")
                raise
        else:
            raise ValueError(f"Unsupported LiDAR format: {lidar_path.suffix}")
        
        # Calculate bounding box
        bbox_min = points.min(axis=0)
        bbox_max = points.max(axis=0)
        
        return PointCloudOutput(
            ply_path=str(output_path),
            camera_poses_path=None,
            sparse_reconstruction_path=None,
            point_count=len(points),
            bounding_box=(bbox_min, bbox_max)
        )
    
    def _convert_images_colmap(self, shadow_twin: ShadowTwinData) -> PointCloudOutput:
        """
        Convert multi-view images to point cloud using COLMAP photogrammetry.
        
        COLMAP Pipeline:
            1. Feature extraction
            2. Feature matching
            3. Sparse reconstruction (SfM)
            4. Export point cloud
        """
        logger.info("Converting images to point cloud using COLMAP...")
        
        images_dir = Path(shadow_twin.data_path)
        output_dir = self.output_dir / shadow_twin.shadow_twin_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        database_path = output_dir / "database.db"
        sparse_dir = output_dir / "sparse"
        sparse_dir.mkdir(exist_ok=True)
        
        # Step 1: Feature extraction
        logger.info("Step 1/4: Extracting features...")
        cmd = [
            self.colmap_executable, "feature_extractor",
            "--database_path", str(database_path),
            "--image_path", str(images_dir),
            "--ImageReader.single_camera", "1",
            "--ImageReader.camera_model", "SIMPLE_PINHOLE"
        ]
        if not self.use_gpu:
            cmd.extend(["--SiftExtraction.use_gpu", "0"])
        
        subprocess.run(cmd, check=True)
        
        # Step 2: Feature matching
        logger.info("Step 2/4: Matching features...")
        cmd = [
            self.colmap_executable, "exhaustive_matcher",
            "--database_path", str(database_path)
        ]
        if not self.use_gpu:
            cmd.extend(["--SiftMatching.use_gpu", "0"])
        
        subprocess.run(cmd, check=True)
        
        # Step 3: Sparse reconstruction (SfM)
        logger.info("Step 3/4: Running sparse reconstruction...")
        cmd = [
            self.colmap_executable, "mapper",
            "--database_path", str(database_path),
            "--image_path", str(images_dir),
            "--output_path", str(sparse_dir)
        ]
        if not self.use_gpu:
            cmd.extend(["--Mapper.ba_global_use_pba", "0"])
        
        subprocess.run(cmd, check=True)
        
        # Step 4: Export point cloud
        logger.info("Step 4/4: Exporting point cloud...")
        ply_path = output_dir / "pointcloud.ply"
        cmd = [
            self.colmap_executable, "model_converter",
            "--input_path", str(sparse_dir / "0"),
            "--output_path", str(ply_path),
            "--output_type", "PLY"
        ]
        
        subprocess.run(cmd, check=True)
        
        # Read point cloud to get stats
        points, colors = self._read_ply(ply_path)
        bbox_min = points.min(axis=0)
        bbox_max = points.max(axis=0)
        
        logger.info(f"COLMAP reconstruction complete: {len(points)} points")
        
        return PointCloudOutput(
            ply_path=str(ply_path),
            camera_poses_path=str(sparse_dir / "0" / "images.bin"),
            sparse_reconstruction_path=str(sparse_dir / "0"),
            point_count=len(points),
            bounding_box=(bbox_min, bbox_max)
        )
    
    def _convert_cad(self, shadow_twin: ShadowTwinData) -> PointCloudOutput:
        """
        Convert CAD model to point cloud by sampling surface.
        
        Supports: .obj, .stl, .ply
        """
        logger.info("Converting CAD model to point cloud...")
        
        try:
            import open3d as o3d
            
            cad_path = Path(shadow_twin.data_path)
            output_path = self.output_dir / shadow_twin.shadow_twin_id / "pointcloud.ply"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Read mesh
            mesh = o3d.io.read_triangle_mesh(str(cad_path))
            
            # Sample points from mesh surface
            num_points = 100000  # Adjust based on model complexity
            pcd = mesh.sample_points_uniformly(number_of_points=num_points)
            
            # Write PLY file
            o3d.io.write_point_cloud(str(output_path), pcd)
            
            points = np.asarray(pcd.points)
            bbox_min = points.min(axis=0)
            bbox_max = points.max(axis=0)
            
            logger.info(f"Sampled {len(points)} points from CAD model")
            
            return PointCloudOutput(
                ply_path=str(output_path),
                camera_poses_path=None,
                sparse_reconstruction_path=None,
                point_count=len(points),
                bounding_box=(bbox_min, bbox_max)
            )
            
        except ImportError:
            logger.error("open3d not installed. Install with: pip install open3d")
            raise
    
    def _convert_fusion(self, shadow_twin: ShadowTwinData) -> PointCloudOutput:
        """
        Fuse multiple data sources into single point cloud.
        
        Combines: LiDAR + images + CAD
        """
        logger.info("Fusing multiple data sources...")
        
        try:
            import open3d as o3d
            
            # Load metadata for fusion sources
            fusion_config = json.loads(shadow_twin.metadata.get("fusion_config", "{}"))
            sources = fusion_config.get("sources", [])
            
            # Collect point clouds from all sources
            point_clouds = []
            
            for source in sources:
                source_type = source["type"]
                source_path = source["path"]
                
                # Create temporary Shadow Twin for each source
                temp_twin = ShadowTwinData(
                    shadow_twin_id=f"{shadow_twin.shadow_twin_id}_{source_type}",
                    asset_type=shadow_twin.asset_type,
                    data_source=source_type,
                    data_path=source_path,
                    metadata={}
                )
                
                # Convert source to point cloud
                output = self.convert(temp_twin)
                pcd = o3d.io.read_point_cloud(output.ply_path)
                point_clouds.append(pcd)
            
            # Merge point clouds
            merged_pcd = point_clouds[0]
            for pcd in point_clouds[1:]:
                merged_pcd += pcd
            
            # Downsample if too many points
            if len(merged_pcd.points) > 500000:
                logger.info(f"Downsampling from {len(merged_pcd.points)} points...")
                merged_pcd = merged_pcd.voxel_down_sample(voxel_size=0.01)
                logger.info(f"Downsampled to {len(merged_pcd.points)} points")
            
            # Write merged point cloud
            output_path = self.output_dir / shadow_twin.shadow_twin_id / "pointcloud.ply"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            o3d.io.write_point_cloud(str(output_path), merged_pcd)
            
            points = np.asarray(merged_pcd.points)
            bbox_min = points.min(axis=0)
            bbox_max = points.max(axis=0)
            
            logger.info(f"Fused {len(sources)} sources into {len(points)} points")
            
            return PointCloudOutput(
                ply_path=str(output_path),
                camera_poses_path=None,
                sparse_reconstruction_path=None,
                point_count=len(points),
                bounding_box=(bbox_min, bbox_max)
            )
            
        except ImportError:
            logger.error("open3d not installed. Install with: pip install open3d")
            raise
    
    def _write_ply(self, path: Path, points: np.ndarray, colors: np.ndarray):
        """Write point cloud to PLY file"""
        with open(path, 'wb') as f:
            # Write PLY header
            f.write(b"ply\n")
            f.write(b"format binary_little_endian 1.0\n")
            f.write(f"element vertex {len(points)}\n".encode())
            f.write(b"property float x\n")
            f.write(b"property float y\n")
            f.write(b"property float z\n")
            f.write(b"property uchar red\n")
            f.write(b"property uchar green\n")
            f.write(b"property uchar blue\n")
            f.write(b"end_header\n")
            
            # Write point data
            for point, color in zip(points, colors):
                # Position (float32)
                f.write(point.astype(np.float32).tobytes())
                # Color (uint8)
                color_uint8 = (color * 255).astype(np.uint8)
                f.write(color_uint8.tobytes())
    
    def _read_ply(self, path: Path) -> Tuple[np.ndarray, np.ndarray]:
        """Read point cloud from PLY file"""
        try:
            import open3d as o3d
            
            pcd = o3d.io.read_point_cloud(str(path))
            points = np.asarray(pcd.points)
            colors = np.asarray(pcd.colors)
            
            return points, colors
            
        except ImportError:
            logger.error("open3d not installed. Install with: pip install open3d")
            raise


# Example usage
if __name__ == "__main__":
    # Example: Convert LiDAR scan
    converter = ShadowTwinPointCloudConverter()
    
    shadow_twin = ShadowTwinData(
        shadow_twin_id="motor_001",
        asset_type="motor",
        data_source="lidar",
        data_path="/path/to/lidar_scan.las",
        metadata={}
    )
    
    output = converter.convert(shadow_twin)
    print(f"Point cloud saved to: {output.ply_path}")
    print(f"Point count: {output.point_count}")
    print(f"Bounding box: {output.bounding_box}")
