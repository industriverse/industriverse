"""
Digital Twin Diplomacy Package for the Overseer System.

This package provides components for managing negotiations between overlapping digital twins
with conflicting goals, ensuring optimal resource allocation and conflict resolution.

Author: Manus AI
Date: May 25, 2025
"""

from .digital_twin_diplomacy_service import DigitalTwinDiplomacyService
from .twin_negotiation_agent import TwinNegotiationAgent
from .capsule_shadow_manager import CapsuleShadowManager
from .diplomacy_models import (
    NegotiationSession, NegotiationProposal, NegotiationAgreement,
    ShadowCapsule, DiplomacyPolicy, ResourceConflict, ConflictResolution
)
