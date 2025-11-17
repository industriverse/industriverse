"""
ASAL Integration Module for Meta-Learning and Global Policy Distribution.

Week 11 deliverable - Complete ASAL integration with:
- UX Genome Collector (pattern extraction from all users)
- ASAL Policy Generator (GIP generation and distribution)
- REST API (genome and policy management)
"""

from .ux_genome_collector import (
    UXGenomeCollector,
    UXGenome,
    GenomeEvidence,
    GenomeType,
    ux_genome_collector
)

from .asal_policy_generator import (
    ASALPolicyGenerator,
    GlobalInteractionPolicy,
    PolicyDistributionResult,
    PolicyType,
    PolicyPriority,
    asal_policy_generator
)

__all__ = [
    # Genome collection
    "UXGenomeCollector",
    "UXGenome",
    "GenomeEvidence",
    "GenomeType",
    "ux_genome_collector",
    
    # Policy generation
    "ASALPolicyGenerator",
    "GlobalInteractionPolicy",
    "PolicyDistributionResult",
    "PolicyType",
    "PolicyPriority",
    "asal_policy_generator"
]
