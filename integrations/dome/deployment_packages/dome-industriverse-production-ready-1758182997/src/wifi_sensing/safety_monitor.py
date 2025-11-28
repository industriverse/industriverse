import time
import json
from typing import Dict, List
from enum import Enum

class SafetyLevel(Enum):
    SAFE = "SAFE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"

class IndustrialSafetyMonitor:
    """Real-time safety monitoring for industrial environments"""
    
    def __init__(self):
        self.safety_zones = {
            "machinery_area": {"max_workers": 2, "motion_threshold": 0.3},
            "loading_dock": {"max_workers": 5, "motion_threshold": 0.4},
            "restricted_zone": {"max_workers": 0, "motion_threshold": 0.1}
        }
        self.active_alerts = []
        self.compliance_log = []
        
    def analyze_safety_event(self, event: Dict) -> Dict:
        """Analyze sensing event for safety implications"""
        safety_assessment = {
            "timestamp": time.time(),
            "event_id": event.get("timestamp", 0),
            "safety_level": SafetyLevel.SAFE,
            "alerts": [],
            "compliance_status": "COMPLIANT",
            "recommended_actions": []
        }
        
        motion_level = event.get("confidence", 0)
        event_type = event.get("type", "unknown")
        
        # Safety analysis logic
        if motion_level > 0.8:
            safety_assessment["safety_level"] = SafetyLevel.CRITICAL
            safety_assessment["alerts"].append("HIGH_MOTION_DETECTED")
            safety_assessment["recommended_actions"].append("IMMEDIATE_INSPECTION_REQUIRED")
            
        elif motion_level > 0.5:
            safety_assessment["safety_level"] = SafetyLevel.WARNING
            safety_assessment["alerts"].append("ELEVATED_MOTION")
            safety_assessment["recommended_actions"].append("MONITOR_CLOSELY")
            
        # OSHA compliance checks
        if "worker_motion" in event_type and motion_level > 0.7:
            safety_assessment["compliance_status"] = "VIOLATION"
            safety_assessment["alerts"].append("OSHA_SAFETY_VIOLATION")
            
        return safety_assessment
    
    def generate_safety_report(self, events: List[Dict]) -> Dict:
        """Generate comprehensive safety report"""
        report = {
            "report_id": f"safety-{int(time.time())}",
            "timestamp": time.time(),
            "total_events": len(events),
            "safety_summary": {
                "safe_events": 0,
                "warning_events": 0,
                "critical_events": 0,
                "emergency_events": 0
            },
            "compliance_score": 0.0,
            "violations": [],
            "recommendations": []
        }
        
        for event in events:
            assessment = self.analyze_safety_event(event)
            
            if assessment["safety_level"] == SafetyLevel.SAFE:
                report["safety_summary"]["safe_events"] += 1
            elif assessment["safety_level"] == SafetyLevel.WARNING:
                report["safety_summary"]["warning_events"] += 1
            elif assessment["safety_level"] == SafetyLevel.CRITICAL:
                report["safety_summary"]["critical_events"] += 1
            elif assessment["safety_level"] == SafetyLevel.EMERGENCY:
                report["safety_summary"]["emergency_events"] += 1
                
            if assessment["compliance_status"] == "VIOLATION":
                report["violations"].append(assessment)
        
        # Calculate compliance score
        total_events = len(events)
        violation_count = len(report["violations"])
        report["compliance_score"] = max(0, (total_events - violation_count) / max(1, total_events) * 100)
        
        # Generate recommendations
        if report["compliance_score"] < 95:
            report["recommendations"].append("INCREASE_SAFETY_TRAINING")
        if report["safety_summary"]["critical_events"] > 0:
            report["recommendations"].append("IMMEDIATE_SAFETY_AUDIT")
            
        return report

def test_safety_monitoring():
    """Test industrial safety monitoring"""
    print("🛡️ INDUSTRIAL SAFETY MONITORING TEST")
    print("=" * 50)
    
    monitor = IndustrialSafetyMonitor()
    
    # Test safety events
    test_events = [
        {"type": "worker_motion", "confidence": 0.3, "timestamp": time.time()},
        {"type": "worker_motion", "confidence": 0.8, "timestamp": time.time()},  # Critical
        {"type": "machinery_vibration", "confidence": 0.6, "timestamp": time.time()},  # Warning
        {"type": "worker_motion", "confidence": 0.9, "timestamp": time.time()},  # Violation
        {"type": "normal_activity", "confidence": 0.2, "timestamp": time.time()}
    ]
    
    # Analyze individual events
    print("📋 INDIVIDUAL SAFETY ASSESSMENTS:")
    for i, event in enumerate(test_events):
        assessment = monitor.analyze_safety_event(event)
        print(f"   Event {i+1}: {assessment['safety_level'].value} - {', '.join(assessment['alerts'])}")
    
    # Generate comprehensive report
    report = monitor.generate_safety_report(test_events)
    
    print(f"\n📊 SAFETY REPORT:")
    print(f"   Report ID: {report['report_id']}")
    print(f"   Total Events: {report['total_events']}")
    print(f"   Safe Events: {report['safety_summary']['safe_events']}")
    print(f"   Warning Events: {report['safety_summary']['warning_events']}")
    print(f"   Critical Events: {report['safety_summary']['critical_events']}")
    print(f"   Compliance Score: {report['compliance_score']:.1f}%")
    print(f"   Violations: {len(report['violations'])}")
    print(f"   Recommendations: {', '.join(report['recommendations'])}")
    
    return report

if __name__ == "__main__":
    report = test_safety_monitoring()
    print("✅ Safety monitoring complete!")
