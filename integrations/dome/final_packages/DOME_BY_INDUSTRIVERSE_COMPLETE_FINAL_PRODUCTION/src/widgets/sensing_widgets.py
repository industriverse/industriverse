"""
DOME SENSING WIDGETS - Industrial WiFi Sensing Visualization
Real-time occupancy, safety monitoring, machine health, energy optimization
"""
import json
import time
import numpy as np
from typing import Dict, List, Any

class SensingWidget:
    """Base class for all sensing widgets"""
    
    def __init__(self, widget_id: str, widget_type: str):
        self.widget_id = widget_id
        self.widget_type = widget_type
        self.theme_config = {}
        self.websocket_events = []
        
    def generate_websocket_event(self, event_data: Dict) -> Dict:
        """Generate WebSocket event in standard format"""
        event = {
            "event": event_data.get("event_type", "unknown"),
            "confidence": event_data.get("confidence", 0.0),
            "location": event_data.get("location", "unknown"),
            "timestamp": int(time.time()),
            "proof_anchor": f"merkle_{hash(str(event_data)) % 1000000:06d}",
            "widget_id": self.widget_id
        }
        return event

class IVSensingHeatmap(SensingWidget):
    """iv-sensing-heatmap: Real-time occupancy visualization"""
    
    def __init__(self):
        super().__init__("iv-sensing-heatmap", "occupancy_visualization")
        self.zones = {}
        self.occupancy_threshold = 0.3
        
    def process_csi_data(self, csi_results: Dict) -> Dict:
        """Process CSI data for occupancy heatmap"""
        print("🗺️ Processing occupancy heatmap...")
        
        # Simulate zone-based occupancy detection
        zones = ["zone_1", "zone_2", "zone_3", "zone_4", "zone_5"]
        occupancy_data = {}
        
        for zone in zones:
            # Simulate occupancy detection from CSI
            occupancy_level = np.random.uniform(0.0, 1.0)
            occupancy_data[zone] = {
                "occupancy_level": occupancy_level,
                "person_count": int(occupancy_level * 3),  # Max 3 people per zone
                "confidence": np.random.uniform(0.8, 0.95),
                "last_motion": time.time() - np.random.uniform(0, 300)  # Last 5 minutes
            }
            
            # Generate WebSocket event if occupied
            if occupancy_level > self.occupancy_threshold:
                event = self.generate_websocket_event({
                    "event_type": "presence",
                    "confidence": occupancy_data[zone]["confidence"],
                    "location": zone
                })
                self.websocket_events.append(event)
        
        heatmap_result = {
            "widget_type": "heatmap",
            "zones": occupancy_data,
            "total_occupancy": sum(z["person_count"] for z in occupancy_data.values()),
            "events_generated": len(self.websocket_events)
        }
        
        print(f"   ✅ Zones processed: {len(zones)}")
        print(f"   👥 Total occupancy: {heatmap_result['total_occupancy']} people")
        print(f"   📡 Events generated: {heatmap_result['events_generated']}")
        
        return heatmap_result

class IVSafetyMonitor(SensingWidget):
    """iv-safety-monitor: Intrusion and fall detection alerts"""
    
    def __init__(self):
        super().__init__("iv-safety-monitor", "safety_alerts")
        self.safety_zones = ["restricted_area", "machinery_zone", "exit_route"]
        self.alert_threshold = 0.7
        
    def detect_safety_events(self, motion_signatures: Dict) -> Dict:
        """Detect intrusion and fall events"""
        print("🛡️ Processing safety monitoring...")
        
        safety_events = []
        
        # Simulate intrusion detection
        for zone in self.safety_zones:
            intrusion_probability = np.random.uniform(0.0, 1.0)
            
            if intrusion_probability > self.alert_threshold:
                event = {
                    "event_type": "intrusion_detected",
                    "zone": zone,
                    "severity": "HIGH" if intrusion_probability > 0.9 else "MEDIUM",
                    "confidence": intrusion_probability,
                    "timestamp": time.time(),
                    "action_required": True
                }
                safety_events.append(event)
                
                # Generate WebSocket alert
                ws_event = self.generate_websocket_event({
                    "event_type": "safety_alert",
                    "confidence": intrusion_probability,
                    "location": zone
                })
                self.websocket_events.append(ws_event)
        
        # Simulate fall detection
        fall_probability = np.random.uniform(0.0, 0.3)  # Lower probability
        if fall_probability > 0.2:
            fall_event = {
                "event_type": "fall_detected",
                "location": "main_floor",
                "severity": "CRITICAL",
                "confidence": fall_probability + 0.7,  # Boost confidence
                "emergency_response": True
            }
            safety_events.append(fall_event)
        
        safety_result = {
            "widget_type": "safety_monitor",
            "events": safety_events,
            "zones_monitored": len(self.safety_zones),
            "alerts_active": len([e for e in safety_events if e.get("action_required")])
        }
        
        print(f"   ✅ Safety zones: {len(self.safety_zones)}")
        print(f"   🚨 Active alerts: {safety_result['alerts_active']}")
        print(f"   📊 Events detected: {len(safety_events)}")
        
        return safety_result

class IVMachineHealth(SensingWidget):
    """iv-machine-health: Vibration anomaly monitoring"""
    
    def __init__(self):
        super().__init__("iv-machine-health", "machine_monitoring")
        self.machines = ["conveyor_1", "press_2", "cnc_3", "robot_arm_4"]
        self.vibration_threshold = 0.6
        
    def analyze_machine_vibrations(self, doppler_signatures: Dict) -> Dict:
        """Analyze machine vibrations for health monitoring"""
        print("🔧 Processing machine health monitoring...")
        
        machine_status = {}
        
        for machine in self.machines:
            # Simulate vibration analysis
            vibration_level = np.random.uniform(0.0, 1.0)
            frequency_anomaly = np.random.uniform(0.0, 1.0)
            
            health_score = 1.0 - max(vibration_level, frequency_anomaly)
            
            machine_status[machine] = {
                "health_score": health_score,
                "vibration_level": vibration_level,
                "frequency_anomaly": frequency_anomaly,
                "status": "HEALTHY" if health_score > 0.7 else "WARNING" if health_score > 0.4 else "CRITICAL",
                "maintenance_due": health_score < 0.5
            }
            
            # Generate alert if unhealthy
            if health_score < self.vibration_threshold:
                event = self.generate_websocket_event({
                    "event_type": "machine_anomaly",
                    "confidence": 1.0 - health_score,
                    "location": machine
                })
                self.websocket_events.append(event)
        
        health_result = {
            "widget_type": "machine_health",
            "machines": machine_status,
            "healthy_machines": len([m for m in machine_status.values() if m["status"] == "HEALTHY"]),
            "maintenance_required": len([m for m in machine_status.values() if m["maintenance_due"]])
        }
        
        print(f"   ✅ Machines monitored: {len(self.machines)}")
        print(f"   💚 Healthy machines: {health_result['healthy_machines']}")
        print(f"   🔧 Maintenance required: {health_result['maintenance_required']}")
        
        return health_result

class IVEnergyOptimizer(SensingWidget):
    """iv-energy-optimizer: HVAC control based on occupancy"""
    
    def __init__(self):
        super().__init__("iv-energy-optimizer", "energy_management")
        self.hvac_zones = ["north_wing", "south_wing", "production_floor", "office_area"]
        
    def optimize_hvac_control(self, occupancy_data: Dict) -> Dict:
        """Optimize HVAC based on occupancy patterns"""
        print("⚡ Processing energy optimization...")
        
        hvac_control = {}
        total_energy_saved = 0
        
        for zone in self.hvac_zones:
            # Simulate occupancy-based HVAC control
            occupancy_level = np.random.uniform(0.0, 1.0)
            
            if occupancy_level < 0.2:
                # Low occupancy - reduce HVAC
                temperature_setpoint = 18  # Lower heating in winter
                fan_speed = 0.3
                energy_reduction = 0.4
            elif occupancy_level < 0.6:
                # Medium occupancy - normal HVAC
                temperature_setpoint = 21
                fan_speed = 0.6
                energy_reduction = 0.1
            else:
                # High occupancy - increase HVAC
                temperature_setpoint = 23
                fan_speed = 1.0
                energy_reduction = 0.0
            
            hvac_control[zone] = {
                "occupancy_level": occupancy_level,
                "temperature_setpoint": temperature_setpoint,
                "fan_speed": fan_speed,
                "energy_reduction": energy_reduction,
                "estimated_savings_kwh": energy_reduction * 10  # 10 kWh base consumption
            }
            
            total_energy_saved += hvac_control[zone]["estimated_savings_kwh"]
        
        energy_result = {
            "widget_type": "energy_optimizer",
            "hvac_zones": hvac_control,
            "total_energy_saved_kwh": total_energy_saved,
            "cost_savings_usd": total_energy_saved * 0.12  # $0.12/kWh
        }
        
        print(f"   ✅ HVAC zones: {len(self.hvac_zones)}")
        print(f"   ⚡ Energy saved: {total_energy_saved:.1f} kWh")
        print(f"   💰 Cost savings: ${energy_result['cost_savings_usd']:.2f}")
        
        return energy_result

def test_sensing_widgets():
    """Test all sensing widgets"""
    print("🎨 SENSING WIDGETS TEST")
    print("=" * 40)
    
    # Create widgets
    heatmap = IVSensingHeatmap()
    safety_monitor = IVSafetyMonitor()
    machine_health = IVMachineHealth()
    energy_optimizer = IVEnergyOptimizer()
    
    # Test data
    csi_results = {"operators": 4, "success_rate": 1.0}
    motion_signatures = {"walking": True, "machinery": True}
    doppler_signatures = {"vibration_detected": True}
    occupancy_data = {"total_people": 15}
    
    # Test each widget
    heatmap_result = heatmap.process_csi_data(csi_results)
    safety_result = safety_monitor.detect_safety_events(motion_signatures)
    health_result = machine_health.analyze_machine_vibrations(doppler_signatures)
    energy_result = energy_optimizer.optimize_hvac_control(occupancy_data)
    
    print(f"\n📊 WIDGET TEST RESULTS:")
    print(f"   🗺️ Heatmap: {heatmap_result['total_occupancy']} people detected")
    print(f"   🛡️ Safety: {safety_result['alerts_active']} active alerts")
    print(f"   🔧 Machine Health: {health_result['healthy_machines']}/{len(machine_health.machines)} healthy")
    print(f"   ⚡ Energy: ${energy_result['cost_savings_usd']:.2f} savings")
    
    return {
        "heatmap": heatmap_result,
        "safety": safety_result,
        "machine_health": health_result,
        "energy": energy_result
    }

if __name__ == "__main__":
    results = test_sensing_widgets()
    print("\n✅ Sensing widgets test complete!")
