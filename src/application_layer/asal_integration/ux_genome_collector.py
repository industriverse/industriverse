"""
UX Genome Collector for ASAL Meta-Learning.

This module collects UX interaction patterns across all users and capsules
to generate "UX Genomes" - reusable patterns that ASAL can learn from and
distribute globally. Week 11 deliverable.

Key Concepts:
- UX Genome: A reusable interaction pattern (e.g., "power users prefer compact layouts")
- Genome Collection: Aggregate patterns from all users
- Pattern Extraction: Identify common behaviors across user archetypes
- ASAL Integration: Feed genomes to ASAL for policy generation

Architecture:
  Individual BVs → Genome Collector → UX Genomes → ASAL
                                                      ↓
                                            Global Interaction Policy (GIP)
                                                      ↓
                                            Distributed to all devices
"""

import logging
import json
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from collections import defaultdict
from enum import Enum
import asyncio
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GenomeType(Enum):
    """Types of UX genomes."""
    LAYOUT_PREFERENCE = "layout_preference"
    DENSITY_PREFERENCE = "density_preference"
    INTERACTION_PATTERN = "interaction_pattern"
    NAVIGATION_PATTERN = "navigation_pattern"
    ERROR_PATTERN = "error_pattern"
    ENGAGEMENT_PATTERN = "engagement_pattern"
    DEVICE_ADAPTATION = "device_adaptation"
    TEMPORAL_PATTERN = "temporal_pattern"


@dataclass
class UXGenome:
    """
    A UX Genome represents a reusable interaction pattern.
    
    Example: "Advanced users with error_rate < 0.05 prefer compact layouts
    with 5 columns and minimal animations."
    """
    genome_id: str
    genome_type: str
    genome_name: str
    description: str
    
    # Pattern definition
    user_archetype: str  # novice, intermediate, proficient, advanced, power_user
    conditions: Dict[str, Any]  # Conditions that trigger this pattern
    ux_configuration: Dict[str, Any]  # Recommended UX settings
    
    # Evidence
    sample_size: int  # Number of users exhibiting this pattern
    confidence: float  # Statistical confidence (0-1)
    effectiveness_score: float  # How well this pattern works (0-1)
    
    # Metadata
    discovered_at: str
    last_updated: str
    version: str = "1.0"
    
    # ASAL integration
    asal_policy_id: Optional[str] = None  # Linked ASAL policy


@dataclass
class GenomeEvidence:
    """Evidence supporting a genome pattern."""
    user_id: str
    behavioral_vector: Dict[str, Any]
    ux_configuration: Dict[str, Any]
    effectiveness_metrics: Dict[str, float]
    timestamp: str


class UXGenomeCollector:
    """
    UX Genome Collector that aggregates patterns across all users.
    
    Analyzes behavioral vectors and UX configurations to identify
    reusable patterns that can be distributed globally via ASAL.
    
    Key Functions:
    - Collect evidence from individual users
    - Extract common patterns across archetypes
    - Generate UX Genomes
    - Feed genomes to ASAL for policy generation
    """
    
    def __init__(self):
        """Initialize the UX Genome Collector."""
        self.genomes: Dict[str, UXGenome] = {}
        self.evidence: Dict[str, List[GenomeEvidence]] = defaultdict(list)
        self.archetype_patterns: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        logger.info("UXGenomeCollector initialized")
    
    async def collect_evidence(
        self,
        user_id: str,
        behavioral_vector: Dict[str, Any],
        ux_configuration: Dict[str, Any],
        effectiveness_metrics: Dict[str, float]
    ):
        """
        Collect evidence from a single user's interaction.
        
        Args:
            user_id: User identifier
            behavioral_vector: User's BV
            ux_configuration: UX config that was applied
            effectiveness_metrics: How well it worked
        """
        archetype = behavioral_vector.get("expertise_level", "intermediate")
        
        evidence = GenomeEvidence(
            user_id=user_id,
            behavioral_vector=behavioral_vector,
            ux_configuration=ux_configuration,
            effectiveness_metrics=effectiveness_metrics,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Store evidence by archetype
        self.evidence[archetype].append(evidence)
        
        logger.info(
            f"Collected evidence from {user_id} ({archetype}): "
            f"effectiveness={effectiveness_metrics.get('engagement_score', 0):.2f}"
        )
    
    async def extract_patterns(
        self,
        min_sample_size: int = 10,
        min_confidence: float = 0.7
    ) -> List[UXGenome]:
        """
        Extract common patterns from collected evidence.
        
        Args:
            min_sample_size: Minimum users needed to form a pattern
            min_confidence: Minimum confidence threshold
        
        Returns:
            List of discovered UX Genomes
        """
        discovered_genomes = []
        
        # Analyze each archetype separately
        for archetype, evidence_list in self.evidence.items():
            if len(evidence_list) < min_sample_size:
                logger.info(f"Insufficient evidence for {archetype} ({len(evidence_list)} < {min_sample_size})")
                continue
            
            # Extract layout preferences
            layout_genome = self._extract_layout_preference(
                archetype, evidence_list, min_confidence
            )
            if layout_genome:
                discovered_genomes.append(layout_genome)
            
            # Extract density preferences
            density_genome = self._extract_density_preference(
                archetype, evidence_list, min_confidence
            )
            if density_genome:
                discovered_genomes.append(density_genome)
            
            # Extract interaction patterns
            interaction_genome = self._extract_interaction_pattern(
                archetype, evidence_list, min_confidence
            )
            if interaction_genome:
                discovered_genomes.append(interaction_genome)
            
            # Extract error patterns
            error_genome = self._extract_error_pattern(
                archetype, evidence_list, min_confidence
            )
            if error_genome:
                discovered_genomes.append(error_genome)
        
        # Store discovered genomes
        for genome in discovered_genomes:
            self.genomes[genome.genome_id] = genome
        
        logger.info(f"Extracted {len(discovered_genomes)} UX genomes")
        
        return discovered_genomes
    
    def _extract_layout_preference(
        self,
        archetype: str,
        evidence_list: List[GenomeEvidence],
        min_confidence: float
    ) -> Optional[UXGenome]:
        """Extract layout preference pattern for an archetype."""
        # Aggregate layout preferences
        layout_counts = defaultdict(int)
        effectiveness_by_layout = defaultdict(list)
        
        for evidence in evidence_list:
            layout = evidence.ux_configuration.get("layout_type")
            if layout:
                layout_counts[layout] += 1
                effectiveness = evidence.effectiveness_metrics.get("engagement_score", 0)
                effectiveness_by_layout[layout].append(effectiveness)
        
        if not layout_counts:
            return None
        
        # Find most common layout
        most_common_layout = max(layout_counts.items(), key=lambda x: x[1])
        layout_type, count = most_common_layout
        
        # Calculate confidence (proportion of users)
        confidence = count / len(evidence_list)
        
        if confidence < min_confidence:
            return None
        
        # Calculate average effectiveness
        avg_effectiveness = (
            sum(effectiveness_by_layout[layout_type]) / len(effectiveness_by_layout[layout_type])
            if effectiveness_by_layout[layout_type] else 0
        )
        
        # Get typical configuration for this layout
        typical_config = self._get_typical_config(
            evidence_list,
            lambda e: e.ux_configuration.get("layout_type") == layout_type
        )
        
        genome_id = self._generate_genome_id(
            GenomeType.LAYOUT_PREFERENCE.value,
            archetype,
            layout_type
        )
        
        genome = UXGenome(
            genome_id=genome_id,
            genome_type=GenomeType.LAYOUT_PREFERENCE.value,
            genome_name=f"{archetype.title()} Layout Preference",
            description=f"{archetype} users prefer {layout_type} layout",
            user_archetype=archetype,
            conditions={
                "expertise_level": archetype
            },
            ux_configuration={
                "layout_type": layout_type,
                "grid_columns": typical_config.get("grid_columns", 3),
                "card_size": typical_config.get("card_size", "medium")
            },
            sample_size=count,
            confidence=confidence,
            effectiveness_score=avg_effectiveness,
            discovered_at=datetime.utcnow().isoformat(),
            last_updated=datetime.utcnow().isoformat()
        )
        
        logger.info(
            f"Discovered layout genome: {archetype} → {layout_type} "
            f"(confidence={confidence:.2f}, effectiveness={avg_effectiveness:.2f})"
        )
        
        return genome
    
    def _extract_density_preference(
        self,
        archetype: str,
        evidence_list: List[GenomeEvidence],
        min_confidence: float
    ) -> Optional[UXGenome]:
        """Extract data density preference pattern."""
        # Aggregate density preferences
        density_values = []
        effectiveness_scores = []
        
        for evidence in evidence_list:
            density = evidence.ux_configuration.get("data_density")
            if density:
                density_values.append(density)
                effectiveness = evidence.effectiveness_metrics.get("engagement_score", 0)
                effectiveness_scores.append(effectiveness)
        
        if not density_values:
            return None
        
        # Calculate average density
        avg_density = sum(density_values) / len(density_values)
        optimal_density = round(avg_density)  # Round to nearest level
        
        # Calculate confidence (how consistent is this preference)
        density_variance = sum((d - avg_density) ** 2 for d in density_values) / len(density_values)
        confidence = 1.0 / (1.0 + density_variance)  # Lower variance = higher confidence
        
        if confidence < min_confidence:
            return None
        
        # Calculate average effectiveness
        avg_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores)
        
        genome_id = self._generate_genome_id(
            GenomeType.DENSITY_PREFERENCE.value,
            archetype,
            str(optimal_density)
        )
        
        genome = UXGenome(
            genome_id=genome_id,
            genome_type=GenomeType.DENSITY_PREFERENCE.value,
            genome_name=f"{archetype.title()} Density Preference",
            description=f"{archetype} users prefer density level {optimal_density}",
            user_archetype=archetype,
            conditions={
                "expertise_level": archetype
            },
            ux_configuration={
                "data_density": optimal_density
            },
            sample_size=len(density_values),
            confidence=confidence,
            effectiveness_score=avg_effectiveness,
            discovered_at=datetime.utcnow().isoformat(),
            last_updated=datetime.utcnow().isoformat()
        )
        
        logger.info(
            f"Discovered density genome: {archetype} → level {optimal_density} "
            f"(confidence={confidence:.2f}, effectiveness={avg_effectiveness:.2f})"
        )
        
        return genome
    
    def _extract_interaction_pattern(
        self,
        archetype: str,
        evidence_list: List[GenomeEvidence],
        min_confidence: float
    ) -> Optional[UXGenome]:
        """Extract interaction pattern (animations, haptic, etc.)."""
        # Aggregate interaction preferences
        animation_prefs = []
        haptic_prefs = []
        
        for evidence in evidence_list:
            config = evidence.ux_configuration
            if "animation_speed" in config:
                animation_prefs.append(config["animation_speed"])
            if "haptic_feedback" in config:
                haptic_prefs.append(config["haptic_feedback"])
        
        if not animation_prefs:
            return None
        
        # Find most common animation speed
        from collections import Counter
        animation_counter = Counter(animation_prefs)
        most_common_animation = animation_counter.most_common(1)[0]
        animation_speed, count = most_common_animation
        
        confidence = count / len(animation_prefs)
        
        if confidence < min_confidence:
            return None
        
        # Determine haptic preference (if available)
        haptic_enabled = (
            sum(haptic_prefs) / len(haptic_prefs) > 0.5
            if haptic_prefs else False
        )
        
        genome_id = self._generate_genome_id(
            GenomeType.INTERACTION_PATTERN.value,
            archetype,
            animation_speed
        )
        
        genome = UXGenome(
            genome_id=genome_id,
            genome_type=GenomeType.INTERACTION_PATTERN.value,
            genome_name=f"{archetype.title()} Interaction Pattern",
            description=f"{archetype} users prefer {animation_speed} animations",
            user_archetype=archetype,
            conditions={
                "expertise_level": archetype
            },
            ux_configuration={
                "animation_speed": animation_speed,
                "haptic_feedback": haptic_enabled
            },
            sample_size=count,
            confidence=confidence,
            effectiveness_score=0.0,  # Not directly measurable
            discovered_at=datetime.utcnow().isoformat(),
            last_updated=datetime.utcnow().isoformat()
        )
        
        logger.info(
            f"Discovered interaction genome: {archetype} → {animation_speed} "
            f"(confidence={confidence:.2f})"
        )
        
        return genome
    
    def _extract_error_pattern(
        self,
        archetype: str,
        evidence_list: List[GenomeEvidence],
        min_confidence: float
    ) -> Optional[UXGenome]:
        """Extract error pattern (when users make mistakes)."""
        # Analyze error rates and corresponding configurations
        high_error_configs = []
        low_error_configs = []
        
        for evidence in evidence_list:
            bv = evidence.behavioral_vector
            proficiency = bv.get("proficiency_indicators", {})
            error_rate = proficiency.get("error_rate", 0)
            
            if error_rate > 0.10:
                high_error_configs.append(evidence.ux_configuration)
            elif error_rate < 0.05:
                low_error_configs.append(evidence.ux_configuration)
        
        if len(low_error_configs) < 5:
            return None  # Need enough low-error examples
        
        # Find common characteristics of low-error configs
        low_error_density = [
            c.get("data_density", 3) for c in low_error_configs
        ]
        optimal_density = sum(low_error_density) / len(low_error_density)
        
        genome_id = self._generate_genome_id(
            GenomeType.ERROR_PATTERN.value,
            archetype,
            "low_error"
        )
        
        genome = UXGenome(
            genome_id=genome_id,
            genome_type=GenomeType.ERROR_PATTERN.value,
            genome_name=f"{archetype.title()} Error Reduction Pattern",
            description=f"Configuration that minimizes errors for {archetype} users",
            user_archetype=archetype,
            conditions={
                "expertise_level": archetype,
                "error_rate": {"max": 0.05}
            },
            ux_configuration={
                "data_density": round(optimal_density),
                "confirmation_dialogs": True,
                "show_help_text": True
            },
            sample_size=len(low_error_configs),
            confidence=0.8,  # Conservative
            effectiveness_score=0.95,  # Low error = high effectiveness
            discovered_at=datetime.utcnow().isoformat(),
            last_updated=datetime.utcnow().isoformat()
        )
        
        logger.info(
            f"Discovered error pattern genome: {archetype} → density {round(optimal_density)}"
        )
        
        return genome
    
    def _get_typical_config(
        self,
        evidence_list: List[GenomeEvidence],
        filter_fn
    ) -> Dict[str, Any]:
        """Get typical configuration from filtered evidence."""
        filtered = [e for e in evidence_list if filter_fn(e)]
        
        if not filtered:
            return {}
        
        # Aggregate common values
        grid_columns = [
            e.ux_configuration.get("grid_columns", 3)
            for e in filtered
        ]
        card_sizes = [
            e.ux_configuration.get("card_size", "medium")
            for e in filtered
        ]
        
        from collections import Counter
        
        return {
            "grid_columns": round(sum(grid_columns) / len(grid_columns)),
            "card_size": Counter(card_sizes).most_common(1)[0][0]
        }
    
    def _generate_genome_id(
        self,
        genome_type: str,
        archetype: str,
        variant: str
    ) -> str:
        """Generate unique genome ID."""
        content = f"{genome_type}_{archetype}_{variant}"
        hash_value = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"genome_{hash_value}"
    
    def get_genome(self, genome_id: str) -> Optional[UXGenome]:
        """Get a specific genome."""
        return self.genomes.get(genome_id)
    
    def get_genomes_by_archetype(self, archetype: str) -> List[UXGenome]:
        """Get all genomes for a specific archetype."""
        return [
            g for g in self.genomes.values()
            if g.user_archetype == archetype
        ]
    
    def get_all_genomes(self) -> List[UXGenome]:
        """Get all discovered genomes."""
        return list(self.genomes.values())
    
    async def export_genomes_for_asal(self) -> List[Dict[str, Any]]:
        """
        Export genomes in ASAL-compatible format.
        
        Returns:
            List of genome dictionaries for ASAL ingestion
        """
        asal_genomes = []
        
        for genome in self.genomes.values():
            asal_genome = {
                "genome_id": genome.genome_id,
                "genome_type": genome.genome_type,
                "pattern_name": genome.genome_name,
                "description": genome.description,
                
                # Conditions (when to apply)
                "trigger_conditions": genome.conditions,
                
                # Actions (what to apply)
                "ux_actions": genome.ux_configuration,
                
                # Confidence metrics
                "sample_size": genome.sample_size,
                "confidence": genome.confidence,
                "effectiveness": genome.effectiveness_score,
                
                # Metadata
                "discovered_at": genome.discovered_at,
                "version": genome.version
            }
            
            asal_genomes.append(asal_genome)
        
        logger.info(f"Exported {len(asal_genomes)} genomes for ASAL")
        
        return asal_genomes


# Singleton instance
ux_genome_collector = UXGenomeCollector()
