"""
Energy Atlas Service (EAS)
Central registry and storage for energy maps

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import json
import time
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum


class EnergyMapStatus(Enum):
    """Energy map status enumeration"""
    PENDING = "pending"
    REGISTERED = "registered"
    VALIDATED = "validated"
    ARCHIVED = "archived"
    FAILED = "failed"


@dataclass
class EnergyMapMetadata:
    """Metadata for an energy map"""
    utid: str
    dataset_name: str
    shape: Tuple[int, ...]
    formula: str
    timestep: int
    energy_range: Tuple[float, float]
    energy_mean: float
    energy_std: float
    file_size: int  # bytes
    storage_path: str
    status: str = "pending"
    created_at: float = field(default_factory=time.time)
    validated_at: Optional[float] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class EnergyMapQuery:
    """Query parameters for energy maps"""
    dataset_name: Optional[str] = None
    min_shape: Optional[Tuple[int, ...]] = None
    max_shape: Optional[Tuple[int, ...]] = None
    min_energy: Optional[float] = None
    max_energy: Optional[float] = None
    status: Optional[str] = None
    limit: int = 100


class EnergyAtlasService:
    """
    Energy Atlas Service (EAS)
    
    Central registry for energy maps with:
    - UTID-based registration
    - Metadata indexing
    - Array storage and retrieval
    - Event emission
    """
    
    def __init__(
        self,
        storage_dir: Optional[Path] = None,
        metadata_file: Optional[Path] = None
    ):
        """
        Initialize Energy Atlas Service
        
        Args:
            storage_dir: Directory for energy map storage
            metadata_file: Path to metadata JSON file
        """
        self.storage_dir = storage_dir or Path.home() / "industriverse_data" / "energy_maps"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata_file = metadata_file or self.storage_dir / "metadata.json"
        
        # Energy map registry (utid -> metadata)
        self.registry: Dict[str, EnergyMapMetadata] = {}
        
        # Event handlers
        self.event_handlers: Dict[str, List] = {}
        
        # Load existing registry
        self._load_registry()
        
        print(f"✅ Energy Atlas Service initialized")
        print(f"  Storage: {self.storage_dir}")
        print(f"  Maps registered: {len(self.registry)}")
    
    def _load_registry(self):
        """Load registry from metadata file"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)
                for item in data:
                    # Convert shape tuple from list
                    if 'shape' in item and isinstance(item['shape'], list):
                        item['shape'] = tuple(item['shape'])
                    if 'energy_range' in item and isinstance(item['energy_range'], list):
                        item['energy_range'] = tuple(item['energy_range'])
                    
                    metadata = EnergyMapMetadata(**item)
                    self.registry[metadata.utid] = metadata
            
            print(f"📂 Loaded {len(self.registry)} energy maps from registry")
    
    def _save_registry(self):
        """Save registry to metadata file"""
        data = []
        for metadata in self.registry.values():
            item = asdict(metadata)
            # Convert tuples to lists for JSON serialization
            if 'shape' in item:
                item['shape'] = list(item['shape'])
            if 'energy_range' in item:
                item['energy_range'] = list(item['energy_range'])
            data.append(item)
        
        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def register_energy_map(
        self,
        utid: str,
        energy_array: np.ndarray,
        dataset_name: str,
        formula: str,
        timestep: int,
        metadata: Optional[Dict] = None
    ) -> EnergyMapMetadata:
        """
        Register a new energy map
        
        Args:
            utid: Unique identifier (UTID)
            energy_array: Energy map array
            dataset_name: Name of source dataset
            formula: Energy formula used
            timestep: Timestep of the data
            metadata: Additional metadata
            
        Returns:
            Energy map metadata
        """
        # Calculate statistics
        energy_range = (float(energy_array.min()), float(energy_array.max()))
        energy_mean = float(energy_array.mean())
        energy_std = float(energy_array.std())
        
        # Save array to disk
        storage_path = self.storage_dir / f"{utid}.npz"
        np.savez_compressed(
            storage_path,
            energy=energy_array,
            dataset_name=dataset_name,
            formula=formula,
            timestep=timestep
        )
        
        file_size = storage_path.stat().st_size
        
        # Create metadata
        map_metadata = EnergyMapMetadata(
            utid=utid,
            dataset_name=dataset_name,
            shape=energy_array.shape,
            formula=formula,
            timestep=timestep,
            energy_range=energy_range,
            energy_mean=energy_mean,
            energy_std=energy_std,
            file_size=file_size,
            storage_path=str(storage_path),
            status="registered",
            metadata=metadata or {}
        )
        
        # Add to registry
        self.registry[utid] = map_metadata
        
        # Save registry
        self._save_registry()
        
        # Emit event
        self._emit_event("energy_map.created", {
            "utid": utid,
            "dataset_name": dataset_name,
            "shape": energy_array.shape,
            "timestamp": time.time()
        })
        
        print(f"✅ Registered energy map: {utid}")
        print(f"  Dataset: {dataset_name}")
        print(f"  Shape: {energy_array.shape}")
        print(f"  Formula: {formula}")
        
        return map_metadata
    
    def get_energy_map(self, utid: str) -> Optional[Tuple[np.ndarray, EnergyMapMetadata]]:
        """
        Retrieve energy map by UTID
        
        Args:
            utid: Energy map UTID
            
        Returns:
            Tuple of (energy_array, metadata) or None if not found
        """
        if utid not in self.registry:
            print(f"❌ Energy map not found: {utid}")
            return None
        
        metadata = self.registry[utid]
        
        # Load array from disk
        try:
            data = np.load(metadata.storage_path)
            energy_array = data['energy']
            return (energy_array, metadata)
        except Exception as e:
            print(f"❌ Error loading energy map {utid}: {e}")
            return None
    
    def query_energy_maps(self, query: EnergyMapQuery) -> List[EnergyMapMetadata]:
        """
        Query energy maps by criteria
        
        Args:
            query: Query parameters
            
        Returns:
            List of matching energy map metadata
        """
        results = []
        
        for metadata in self.registry.values():
            # Filter by dataset name
            if query.dataset_name and metadata.dataset_name != query.dataset_name:
                continue
            
            # Filter by shape
            if query.min_shape and any(s < m for s, m in zip(metadata.shape, query.min_shape)):
                continue
            if query.max_shape and any(s > m for s, m in zip(metadata.shape, query.max_shape)):
                continue
            
            # Filter by energy range
            if query.min_energy and metadata.energy_mean < query.min_energy:
                continue
            if query.max_energy and metadata.energy_mean > query.max_energy:
                continue
            
            # Filter by status
            if query.status and metadata.status != query.status:
                continue
            
            results.append(metadata)
            
            # Limit results
            if len(results) >= query.limit:
                break
        
        return results
    
    def validate_energy_map(self, utid: str) -> bool:
        """
        Validate an energy map
        
        Args:
            utid: Energy map UTID
            
        Returns:
            True if validation successful
        """
        if utid not in self.registry:
            return False
        
        metadata = self.registry[utid]
        
        # Load and validate array
        result = self.get_energy_map(utid)
        if not result:
            metadata.status = "failed"
            self._save_registry()
            return False
        
        energy_array, _ = result
        
        # Validation checks
        if energy_array.size == 0:
            metadata.status = "failed"
            self._save_registry()
            return False
        
        if not np.isfinite(energy_array).all():
            metadata.status = "failed"
            self._save_registry()
            return False
        
        # Mark as validated
        metadata.status = "validated"
        metadata.validated_at = time.time()
        self._save_registry()
        
        # Emit event
        self._emit_event("energy_map.validated", {
            "utid": utid,
            "timestamp": time.time()
        })
        
        print(f"✅ Validated energy map: {utid}")
        
        return True
    
    def archive_energy_map(self, utid: str) -> bool:
        """
        Archive an energy map
        
        Args:
            utid: Energy map UTID
            
        Returns:
            True if archival successful
        """
        if utid not in self.registry:
            return False
        
        metadata = self.registry[utid]
        metadata.status = "archived"
        self._save_registry()
        
        print(f"📦 Archived energy map: {utid}")
        
        return True
    
    def delete_energy_map(self, utid: str) -> bool:
        """
        Delete an energy map
        
        Args:
            utid: Energy map UTID
            
        Returns:
            True if deletion successful
        """
        if utid not in self.registry:
            return False
        
        metadata = self.registry[utid]
        
        # Delete file
        storage_path = Path(metadata.storage_path)
        if storage_path.exists():
            storage_path.unlink()
        
        # Remove from registry
        del self.registry[utid]
        self._save_registry()
        
        print(f"🗑️  Deleted energy map: {utid}")
        
        return True
    
    def register_event_handler(self, event_type: str, handler):
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def _emit_event(self, event_type: str, event_data: Dict):
        """Emit an event to registered handlers"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event_data)
                except Exception as e:
                    print(f"❌ Error in event handler for {event_type}: {e}")
    
    def get_statistics(self) -> Dict:
        """Get energy atlas statistics"""
        if not self.registry:
            return {
                "total_maps": 0,
                "total_size": 0,
                "avg_size": 0,
                "status_counts": {}
            }
        
        total_size = sum(m.file_size for m in self.registry.values())
        avg_size = total_size / len(self.registry)
        
        status_counts = {}
        for metadata in self.registry.values():
            status = metadata.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_maps": len(self.registry),
            "total_size": total_size,
            "avg_size": avg_size,
            "status_counts": status_counts
        }
    
    def get_dataset_statistics(self) -> Dict[str, Dict]:
        """Get statistics by dataset"""
        dataset_stats = {}
        
        for metadata in self.registry.values():
            dataset = metadata.dataset_name
            if dataset not in dataset_stats:
                dataset_stats[dataset] = {
                    "count": 0,
                    "total_size": 0,
                    "shapes": set()
                }
            
            dataset_stats[dataset]["count"] += 1
            dataset_stats[dataset]["total_size"] += metadata.file_size
            dataset_stats[dataset]["shapes"].add(metadata.shape)
        
        # Convert sets to lists for JSON serialization
        for dataset in dataset_stats:
            dataset_stats[dataset]["shapes"] = [list(s) for s in dataset_stats[dataset]["shapes"]]
        
        return dataset_stats
