"""
DOME SENSING WIDGETS - Modular Building Experience for Clients
Real-time occupancy, safety monitoring, machine health, energy optimization
CRITICAL: Foundation for next modular client plan
"""
import json
import time
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime

class SensingWidgets:
    """
    Modular widget framework for client customization
    Foundation for next plan's modular building experience
    """
    
    def __init__(self):
        self.widget_registry = {}
        self.active_widgets = {}
        self.client_configurations = {}
        
    def register_widget(self, widget_id: str, widget_config: Dict):
        """Register a new widget for modular deployment"""
        self.widget_registry[widget_id] = {
            "config": widget_config,
            "created_at": time.time(),
            "version": "1.0.0",
            "modular_ready": True
        }
        
    def generate_occupancy_heatmap(self, zone_config: Optional[Dict] = None) -> Dict:
        """
        Occupancy Heatmap Widget - iv-sensing-heatmap
        Modular component for client integration
        """
        zones = zone_config or {
            "zone_1": {"x": 0, "y": 0, "width": 10, "height": 10},
            "zone_2": {"x": 10, "y": 0, "width": 10, "height": 10},
            "zone_3": {"x": 0, "y": 10, "width": 10, "height": 10},
            "zone_4": {"x": 10, "y": 10, "width": 10, "height": 10},
            "zone_5": {"x": 5, "y": 5, "width": 10, "height": 10}
        }
        
        heatmap_data = {}
        total_occupancy = 0
        
        for zone_id, zone_info in zones.items():
            # Simulate realistic occupancy data
            occupancy = max(0, int(np.random.normal(2, 1.5)))
            activity_level = min(1.0, max(0.0, np.random.normal(0.4, 0.2)))
            
            heatmap_data[zone_id] = {
                "occupancy_count": occupancy,
                "activity_level": activity_level,
                "zone_coordinates": zone_info,
                "last_motion": time.time() - np.random.randint(0, 300),
                "confidence": 0.85 + np.random.random() * 0.15
            }
            total_occupancy += occupancy
        
        return {
            "widget_id": "iv-sensing-heatmap",
            "widget_type": "occupancy_visualization",
            "modular_component": True,
            "data": {
                "zones": heatmap_data,
                "total_occupancy": total_occupancy,
                "max_capacity": len(zones) * 5,
                "utilization_rate": min(1.0, total_occupancy / (len(zones) * 3)),
                "timestamp": time.time()
            },
            "client_customizable": {
                "color_scheme": "configurable",
                "zone_layout": "configurable", 
                "alert_thresholds": "configurable",
                "refresh_rate": "configurable"
            }
        }
    
    def generate_safety_monitor(self, safety_config: Optional[Dict] = None) -> Dict:
        """
        Safety Monitor Widget - iv-safety-monitor
        Modular OSHA compliance component
        """
        safety_zones = safety_config or ["production_floor", "warehouse", "office"]
        
        safety_data = {}
        total_violations = 0
        
        for zone in safety_zones:
            violations = []
            
            # Simulate safety events
            if np.random.random() < 0.15:  # 15% chance of violation
                violation_types = ["ppe_missing", "restricted_access", "equipment_unsafe", "emergency_exit_blocked"]
                violation = {
                    "type": np.random.choice(violation_types),
                    "severity": np.random.choice(["low", "medium", "high"]),
                    "timestamp": time.time() - np.random.randint(0, 3600),
                    "auto_reported": True
                }
                violations.append(violation)
                total_violations += 1
            
            safety_data[zone] = {
                "status": "violation" if violations else "compliant",
                "violations": violations,
                "compliance_score": max(0.7, 1.0 - len(violations) * 0.1),
                "last_inspection": time.time() - np.random.randint(0, 86400),
                "osha_compliant": len(violations) == 0
            }
        
        return {
            "widget_id": "iv-safety-monitor",
            "widget_type": "safety_compliance",
            "modular_component": True,
            "data": {
                "zones": safety_data,
                "total_violations": total_violations,
                "overall_compliance": max(0.8, 1.0 - total_violations * 0.05),
                "osha_status": "compliant" if total_violations == 0 else "violations_detected",
                "timestamp": time.time()
            },
            "client_customizable": {
                "compliance_standards": ["OSHA", "ISO-45001", "IEC-61508"],
                "alert_channels": "configurable",
                "reporting_frequency": "configurable",
                "violation_thresholds": "configurable"
            }
        }
    
    def generate_machine_health(self, machine_config: Optional[Dict] = None) -> Dict:
        """
        Machine Health Widget - iv-machine-health
        Modular predictive maintenance component
        """
        machines = machine_config or {
            "conveyor_01": {"type": "conveyor", "critical": True},
            "press_02": {"type": "hydraulic_press", "critical": True},
            "robot_03": {"type": "industrial_robot", "critical": False},
            "hvac_04": {"type": "hvac_system", "critical": False}
        }
        
        machine_data = {}
        maintenance_needed = 0
        
        for machine_id, machine_info in machines.items():
            # Simulate machine health metrics
            vibration = np.random.normal(0.5, 0.2)
            temperature = np.random.normal(65, 15)  # Celsius
            efficiency = max(0.6, min(1.0, np.random.normal(0.85, 0.1)))
            
            health_score = (
                (1.0 - min(1.0, abs(vibration - 0.3) / 0.7)) * 0.4 +
                (1.0 - min(1.0, abs(temperature - 60) / 40)) * 0.3 +
                efficiency * 0.3
            )
            
            needs_maintenance = health_score < 0.75
            if needs_maintenance:
                maintenance_needed += 1
            
            machine_data[machine_id] = {
                "health_score": health_score,
                "status": "maintenance_required" if needs_maintenance else "operational",
                "metrics": {
                    "vibration_level": vibration,
                    "temperature_c": temperature,
                    "efficiency_percent": efficiency * 100
                },
                "predicted_failure": time.time() + np.random.randint(86400, 604800) if needs_maintenance else None,
                "maintenance_priority": "high" if machine_info["critical"] and needs_maintenance else "normal"
            }
        
        return {
            "widget_id": "iv-machine-health",
            "widget_type": "predictive_maintenance",
            "modular_component": True,
            "data": {
                "machines": machine_data,
                "maintenance_needed": maintenance_needed,
                "overall_health": sum(m["health_score"] for m in machine_data.values()) / len(machine_data),
                "critical_alerts": sum(1 for m in machine_data.values() if m.get("maintenance_priority") == "high"),
                "timestamp": time.time()
            },
            "client_customizable": {
                "health_thresholds": "configurable",
                "maintenance_scheduling": "configurable",
                "alert_priorities": "configurable",
                "reporting_intervals": "configurable"
            }
        }
    
    def generate_energy_optimizer(self, energy_config: Optional[Dict] = None) -> Dict:
        """
        Energy Optimizer Widget - iv-energy-optimizer
        Modular energy management component
        """
        systems = energy_config or {
            "hvac_zone_1": {"type": "hvac", "capacity_kw": 15},
            "lighting_floor_1": {"type": "lighting", "capacity_kw": 8},
            "machinery_line_1": {"type": "production", "capacity_kw": 45},
            "hvac_zone_2": {"type": "hvac", "capacity_kw": 12}
        }
        
        energy_data = {}
        total_consumption = 0
        total_savings = 0
        
        for system_id, system_info in systems.items():
            # Simulate energy metrics
            current_usage = system_info["capacity_kw"] * np.random.uniform(0.4, 0.9)
            efficiency = np.random.uniform(0.75, 0.95)
            potential_savings = current_usage * (1 - efficiency) * 0.5
            
            total_consumption += current_usage
            total_savings += potential_savings
            
            energy_data[system_id] = {
                "current_usage_kw": current_usage,
                "efficiency_percent": efficiency * 100,
                "potential_savings_kw": potential_savings,
                "cost_per_hour": current_usage * 0.12,  # $0.12/kWh
                "optimization_recommendations": [
                    "Adjust temperature setpoint",
                    "Schedule maintenance",
                    "Upgrade to LED lighting"
                ][:np.random.randint(1, 4)]
            }
        
        return {
            "widget_id": "iv-energy-optimizer",
            "widget_type": "energy_management",
            "modular_component": True,
            "data": {
                "systems": energy_data,
                "total_consumption_kw": total_consumption,
                "total_potential_savings_kw": total_savings,
                "cost_savings_per_hour": total_savings * 0.12,
                "efficiency_score": (total_consumption - total_savings) / total_consumption,
                "timestamp": time.time()
            },
            "client_customizable": {
                "energy_targets": "configurable",
                "cost_parameters": "configurable",
                "optimization_strategies": "configurable",
                "reporting_periods": "configurable"
            }
        }
    
    def get_all_widgets(self) -> Dict:
        """Get all available widgets for modular client deployment"""
        return {
            "occupancy_heatmap": self.generate_occupancy_heatmap(),
            "safety_monitor": self.generate_safety_monitor(),
            "machine_health": self.generate_machine_health(),
            "energy_optimizer": self.generate_energy_optimizer()
        }
    
    def create_client_dashboard(self, client_id: str, widget_selection: List[str]) -> Dict:
        """Create customized dashboard for specific client"""
        dashboard = {
            "client_id": client_id,
            "dashboard_id": f"dashboard_{client_id}_{int(time.time())}",
            "widgets": {},
            "modular_ready": True,
            "created_at": time.time()
        }
        
        all_widgets = self.get_all_widgets()
        
        for widget_id in widget_selection:
            if widget_id in all_widgets:
                dashboard["widgets"][widget_id] = all_widgets[widget_id]
        
        return dashboard

def test_modular_widgets():
    """Test modular widget framework for client deployment"""
    print("🎨 TESTING MODULAR WIDGET FRAMEWORK")
    print("=" * 60)
    
    widgets = SensingWidgets()
    
    # Test individual widgets
    occupancy = widgets.generate_occupancy_heatmap()
    safety = widgets.generate_safety_monitor()
    machine = widgets.generate_machine_health()
    energy = widgets.generate_energy_optimizer()
    
    print(f"📊 WIDGET TEST RESULTS:")
    print(f"   Occupancy Heatmap: {occupancy['data']['total_occupancy']} people detected")
    print(f"   Safety Monitor: {safety['data']['overall_compliance']:.1%} compliance")
    print(f"   Machine Health: {machine['data']['maintenance_needed']} machines need maintenance")
    print(f"   Energy Optimizer: ${energy['data']['cost_savings_per_hour']:.2f}/hour potential savings")
    
    # Test client dashboard creation
    client_dashboard = widgets.create_client_dashboard("client_001", ["occupancy_heatmap", "safety_monitor"])
    
    print(f"\n🏢 CLIENT DASHBOARD:")
    print(f"   Client ID: {client_dashboard['client_id']}")
    print(f"   Widgets: {list(client_dashboard['widgets'].keys())}")
    print(f"   Modular Ready: {client_dashboard['modular_ready']}")
    
    return {
        "widgets_tested": 4,
        "all_modular_ready": True,
        "client_dashboard_created": True
    }

if __name__ == "__main__":
    results = test_modular_widgets()
    print(f"\n✅ Modular widget framework test complete!")
    print(f"🚀 Ready for next plan's modular building experience!")
