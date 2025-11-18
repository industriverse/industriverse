"""
AI Shield v2: Thermodynamic Cybersecurity

Physics-based security primitives that cannot be spoofed, hidden, or bypassed.

Core Principle:
Every digital system emits thermodynamic signatures (energy, entropy, heat, power).
These signatures are fundamentally physical and obey conservation laws.
Violations indicate attacks, intrusions, or system compromise.

Architecture:
- Thermodynamic Primitives: PUFs, baseline validators, consistency checkers
- Security Sensors: Power, thermal, entropy, timing, EM emission monitors
- Threat Analyzers: Information leakage, side-channel detection, attack correlation
- Defensive Orchestration: Automated mitigation via capsule deployment
- Proof Network: Immutable audit trails and compliance evidence

Integration with Industriverse:
- Unified Registry → Security Event Registry
- Protocol Connector → Threat Intelligence Fabric
- AR/VR Integration → Immersive Threat Visualization
- Integration Orchestrator → Security Operations Kernel
- Capsule Lifecycle → Defensive Capsule Orchestrator

Week 20-22 Roadmap:
Week 20: Security primitives (PUF, power analysis, cold boot, entropy)
Week 21: Domain extensions (quantum, grid, financial, swarm)
Week 22: Production release (SOC dashboard, compliance, deployment)
"""

from .thermodynamic_primitives.puf import (
    ThermodynamicPUF,
    PUFSignature,
    get_thermodynamic_puf
)

from .sensors.power_analysis_detector import (
    PowerAnalysisDetector,
    get_power_analysis_detector
)

from .sensors.thermal_security_monitor import (
    ThermalSecurityMonitor,
    get_thermal_security_monitor
)

from .analyzers.information_leakage_analyzer import (
    InformationLeakageAnalyzer,
    get_information_leakage_analyzer
)

from .security_event_registry import (
    SecurityEventRegistry,
    get_security_event_registry
)

__all__ = [
    "ThermodynamicPUF",
    "PUFSignature",
    "get_thermodynamic_puf",
    "PowerAnalysisDetector",
    "get_power_analysis_detector",
    "ThermalSecurityMonitor",
    "get_thermal_security_monitor",
    "InformationLeakageAnalyzer",
    "get_information_leakage_analyzer",
    "SecurityEventRegistry",
    "get_security_event_registry"
]
