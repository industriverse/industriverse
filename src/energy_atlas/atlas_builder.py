import h5py
import numpy as np
from typing import Dict, Any, Optional

class EnergyAtlas:
    """
    The Energy Atlas: A 4D Spatiotemporal Map of Industrial Energy.
    
    Stores:
    1. Planned Energy (from G-code): 3D Voxel Grid (x, y, z) -> Energy Density (J/mm^3)
    2. Observed Energy (from Video): 2D/3D Heatmap (x, y, t) -> Energy Flux (W/m^2)
    """
    
    def __init__(self, filepath: str, mode: str = 'a'):
        self.filepath = filepath
        self.f = h5py.File(filepath, mode)
        self._init_structure()

    def _init_structure(self):
        if 'planned' not in self.f:
            self.f.create_group('planned')
        if 'observed' not in self.f:
            self.f.create_group('observed')
        if 'metadata' not in self.f:
            self.f.create_group('metadata')

    def add_planned_voxel_grid(self, model_id: str, voxels: np.ndarray, metadata: Dict[str, Any]):
        """
        Add a 3D Energy Voxel Grid (from Slice100k).
        voxels: 3D numpy array where value = Energy (Joules)
        """
        grp = self.f['planned'].create_group(model_id)
        dset = grp.create_dataset('energy_voxels', data=voxels, compression="gzip")
        
        # Store metadata
        for k, v in metadata.items():
            grp.attrs[k] = v
            
    def add_observed_heatmap(self, video_id: str, heatmap: np.ndarray, metadata: Dict[str, Any]):
        """
        Add a 2D/3D Activity Heatmap (from Egocentric-10K).
        heatmap: 2D (x,y) or 3D (x,y,t) array where value = Activity/Energy
        """
        grp = self.f['observed'].create_group(video_id)
        dset = grp.create_dataset('activity_map', data=heatmap, compression="gzip")
        
        for k, v in metadata.items():
            grp.attrs[k] = v

    def close(self):
        self.f.close()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
