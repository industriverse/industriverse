#!/usr/bin/env python3
"""
Autonomous Service Injector (ASI) - Core Module
Self-organizing service orchestration layer
"""

import json
import yaml
from typing import Dict, List, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import sys

# Import UTID Generator from DAC Factory
from src.core_ai_layer.dac_factory.utid_generator import UTIDGenerator


@dataclass
class ServiceManifest:
    """Service manifest structure"""
    service_id: str
    service_type: str
    endpoint: str
    protocol: str
    energy_cost: float = 0.0
    reliability: float = 1.0
    utid_seed: str = ""
    capabilities: List[str] = None
    status: str = "active"
    metadata: Dict = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.metadata is None:
            self.metadata = {}


class EventHandler:
    """Event handler for ASI events"""
    
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}
    
    def register(self, event_type: str, handler: Callable):
        """Register event handler"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    def emit(self, event_type: str, event_data: Dict):
        """Emit event to all registered handlers"""
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                try:
                    handler(event_data)
                except Exception as e:
                    print(f"Error in handler for {event_type}: {e}")


class ASICore:
    """Autonomous Service Injector Core"""
    
    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or Path.home() / 'industriverse_week3' / 'systems' / 'asi' / 'registry'
        self.registry_path.mkdir(parents=True, exist_ok=True)
        
        self.services: Dict[str, ServiceManifest] = {}
        self.event_handler = EventHandler()
        self.utid_gen = UTIDGenerator(namespace="industriverse")
        
        # Load existing registry
        self._load_registry()
        
        # Register default event handlers
        self._register_default_handlers()
    
    def _load_registry(self):
        """Load service registry from disk"""
        manifest_file = self.registry_path / 'service_manifest.json'
        
        if manifest_file.exists():
            with open(manifest_file, 'r') as f:
                data = json.load(f)
                for service_data in data:
                    manifest = ServiceManifest(**service_data)
                    self.services[manifest.service_id] = manifest
            
            print(f"Loaded {len(self.services)} services from registry")
    
    def _save_registry(self):
        """Save service registry to disk"""
        manifest_file = self.registry_path / 'service_manifest.json'
        
        services_data = [asdict(manifest) for manifest in self.services.values()]
        
        with open(manifest_file, 'w') as f:
            json.dump(services_data, f, indent=2)
    
    def _register_default_handlers(self):
        """Register default event handlers"""
        
        def on_energy_map_created(event_data: Dict):
            """Handle energy_map.created event"""
            print(f"[ASI] Energy map created: {event_data.get('utid')}")
            # TODO: Trigger LoRA training job
            # TODO: Schedule discovery_v16 runs
            # TODO: Create preview_capsule
        
        def on_service_registered(event_data: Dict):
            """Handle service.registered event"""
            print(f"[ASI] Service registered: {event_data.get('service_id')}")
        
        self.event_handler.register('energy_map.created', on_energy_map_created)
        self.event_handler.register('service.registered', on_service_registered)
    
    def register_service(self, manifest: ServiceManifest) -> str:
        """Register a new service"""
        
        # Generate UTID seed if not provided
        if not manifest.utid_seed:
            manifest.utid_seed = self.utid_gen.generate(
                entity_type="service",
                entity_name=manifest.service_id,
                version="v1"
            )
        
        # Add to registry
        self.services[manifest.service_id] = manifest
        
        # Save registry
        self._save_registry()
        
        # Emit event
        self.event_handler.emit('service.registered', asdict(manifest))
        
        return manifest.utid_seed
    
    def get_service(self, service_id: str) -> Optional[ServiceManifest]:
        """Get service by ID"""
        return self.services.get(service_id)
    
    def list_services(
        self,
        service_type: Optional[str] = None,
        status: str = "active"
    ) -> List[ServiceManifest]:
        """List services with optional filtering"""
        
        services = list(self.services.values())
        
        if service_type:
            services = [s for s in services if s.service_type == service_type]
        
        if status:
            services = [s for s in services if s.status == status]
        
        return services
    
    def create_job(self, job_type: str, job_spec: Dict) -> str:
        """Create a job for execution"""
        
        job_id = self.utid_gen.generate(
            entity_type="job",
            entity_name=job_type,
            version="v1",
            metadata=job_spec
        )
        
        print(f"[ASI] Created job: {job_id}")
        print(f"  Type: {job_type}")
        print(f"  Spec: {job_spec}")
        
        # TODO: Route job to appropriate service via TTF
        
        return job_id


# Example usage
if __name__ == "__main__":
    asi = ASICore()
    
    # Register OBMI service
    obmi_manifest = ServiceManifest(
        service_id="obmi-aesp-v1",
        service_type="grpc",
        endpoint="grpc://10.244.0.157:8080",
        protocol="grpc",
        energy_cost=0.12,
        reliability=0.98,
        capabilities=["quantum_validation", "epistemic_scoring"],
        metadata={"operator_type": "AESP"}
    )
    
    utid = asi.register_service(obmi_manifest)
    print(f"\nRegistered service with UTID: {utid}")
    
    # List services
    services = asi.list_services(service_type="grpc")
    print(f"\nFound {len(services)} gRPC services")
    
    # Simulate energy map created event
    asi.event_handler.emit('energy_map.created', {
        'utid': 'UTID:industriverse:energy_atlas:MHD_256:v1:abc123',
        'dataset_id': 'MHD_256'
    })
    
    print("\n" + "="*50)
    print("ASI Core initialized successfully")
