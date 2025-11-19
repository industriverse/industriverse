"""
I³ - Industrial Internet of Intelligence

Complete intelligence layer for white-label platform enabling:
- Deep research integration (RDR Engine)
- 3D knowledge graph visualization (Shadow Twin)
- Nano-simulation capabilities (MSEP.one)
- Thermodynamic knowledge operations (OBMI Operators)
- Proof-of-Insight validation
- UTID marketplace integration

Architecture:
- RDR Engine: Paper ingestion, 6D embeddings, insight discovery
- Shadow Twin: Real-time 3D force-directed graph backend
- MSEP Integration: Molecular/materials simulation interface
- OBMI Operators: 5 thermodynamic knowledge operators (AESP, QERO, PRIN, AIEO, AROE)

Integration Points:
- Widget layer: Research Explorer, Shadow Twin 3D widgets
- DAC layer: Full Discovery tier deployment
- Partner Portal: I³ feature gating and analytics
"""

from .rdr_engine import (
    RDREngine,
    Paper,
    Insight,
    Embedding6D,
    PaperSource,
    InsightType,
    get_rdr_engine,
)

from .shadow_twin_backend import (
    ShadowTwinBackend,
    Node,
    Edge,
    NodeType,
    EdgeType,
    get_shadow_twin,
)

from .msep_integration import (
    MSEPIntegration,
    SimulationType,
    SimulationParameters,
    SimulationResult,
    SimulationStatus,
    get_msep_integration,
)

from .obmi_operators import (
    OBMIOrchestrator,
    AESPOperator,
    QEROOperator,
    PRINOperator,
    AIEOOperator,
    AROEOperator,
    get_obmi_orchestrator,
)

__all__ = [
    # RDR Engine
    "RDREngine",
    "Paper",
    "Insight",
    "Embedding6D",
    "PaperSource",
    "InsightType",
    "get_rdr_engine",

    # Shadow Twin
    "ShadowTwinBackend",
    "Node",
    "Edge",
    "NodeType",
    "EdgeType",
    "get_shadow_twin",

    # MSEP Integration
    "MSEPIntegration",
    "SimulationType",
    "SimulationParameters",
    "SimulationResult",
    "SimulationStatus",
    "get_msep_integration",

    # OBMI Operators
    "OBMIOrchestrator",
    "AESPOperator",
    "QEROOperator",
    "PRINOperator",
    "AIEOOperator",
    "AROEOperator",
    "get_obmi_orchestrator",
]


def initialize_i3_platform():
    """
    Initialize complete I³ platform

    Sets up all intelligence layer components and their integrations
    """
    # Initialize RDR engine
    rdr = get_rdr_engine()

    # Initialize Shadow Twin
    shadow_twin = get_shadow_twin()

    # Initialize MSEP integration
    msep = get_msep_integration()

    # Initialize OBMI operators
    obmi = get_obmi_orchestrator()

    return {
        'rdr_engine': rdr,
        'shadow_twin': shadow_twin,
        'msep_integration': msep,
        'obmi_orchestrator': obmi,
        'status': 'initialized'
    }


def create_paper_to_visualization_pipeline():
    """
    Create complete pipeline: Paper → RDR → Shadow Twin → Visualization

    Example workflow:
    1. Ingest paper via RDR
    2. Generate 6D embedding
    3. Discover insights
    4. Add to Shadow Twin graph
    5. Run physics layout
    6. Stream to 3D widget
    """
    rdr = get_rdr_engine()
    shadow_twin = get_shadow_twin()

    def pipeline(paper_data: dict):
        # Step 1: Ingest paper
        from datetime import datetime

        paper = rdr.ingest_paper(
            title=paper_data['title'],
            authors=paper_data['authors'],
            abstract=paper_data['abstract'],
            source=PaperSource(paper_data.get('source', 'arxiv')),
            url=paper_data['url'],
            published_date=datetime.fromisoformat(paper_data['published_date']),
            keywords=paper_data.get('keywords', [])
        )

        # Step 2: Add to Shadow Twin
        paper_node = shadow_twin.add_node(
            node_id=paper.paper_id,
            node_type=NodeType.PAPER,
            label=paper.title,
            metadata={
                'authors': paper.authors,
                'source': paper.source,
                'citations': paper.citations
            }
        )

        # Step 3: Connect related papers
        for related_id in paper.related_papers:
            shadow_twin.add_edge(
                source=paper.paper_id,
                target=related_id,
                edge_type=EdgeType.RELATED,
                weight=1.0
            )

        # Step 4: Add insights as nodes
        insights = rdr.query_insights(min_confidence=0.7)
        for insight in insights:
            if paper.paper_id in insight.source_papers:
                insight_node = shadow_twin.add_node(
                    node_id=insight.insight_id,
                    node_type=NodeType.INSIGHT,
                    label=insight.text[:50] + "...",
                    metadata={
                        'confidence': insight.confidence,
                        'proof_score': insight.proof_score,
                        'utid': insight.utid
                    }
                )

                # Connect insight to paper
                shadow_twin.add_edge(
                    source=paper.paper_id,
                    target=insight.insight_id,
                    edge_type=EdgeType.SUPPORTS,
                    weight=insight.confidence
                )

        # Step 5: Run layout
        shadow_twin.run_layout(iterations=50)

        return {
            'paper': paper.to_dict(),
            'shadow_twin_state': shadow_twin.get_state(),
            'insights_discovered': len([i for i in insights if paper.paper_id in i.source_papers])
        }

    return pipeline


def create_simulation_validation_workflow():
    """
    Create workflow: Paper → MSEP Simulation → Validation → Insight Update

    Validates research findings through computational simulation
    """
    rdr = get_rdr_engine()
    msep = get_msep_integration()

    def workflow(paper_id: str, simulation_type: SimulationType):
        # Step 1: Extract simulation parameters from paper
        sim_id = msep.paper_to_simulation(paper_id, rdr, simulation_type)

        if not sim_id:
            return {'error': 'Could not extract simulation parameters'}

        # Step 2: Wait for simulation completion (in production, use async/webhook)
        result = msep.get_simulation_status(sim_id)

        # Step 3: Validate against paper
        validation = msep.validate_against_paper(sim_id, paper_id, rdr)

        # Step 4: Update insights based on validation
        insights = [i for i in rdr.insights.values() if paper_id in i.source_papers]

        for insight in insights:
            if validation['validated'] and validation['agreement_score'] > 0.8:
                # Boost proof score with simulation validation
                insight.proof_score = min(insight.proof_score * 1.2, 1.0)
                insight.validation_method = "msep-simulation"

                # Generate UTID if newly validated
                if not insight.utid and insight.proof_score >= 0.85:
                    insight.utid = rdr._generate_utid(insight.insight_id, insight.proof_score)
                    insight.validated = True

        return {
            'simulation_id': sim_id,
            'simulation_result': result.to_dict() if result else None,
            'validation': validation,
            'insights_updated': len(insights)
        }

    return workflow
