"""
Proof-of-Insight Ledger

Blockchain-inspired immutable ledger for tracking:
- Insight creation and validation
- UTID minting and ownership
- Citation and usage events
- Revenue generation and distribution
- Provenance and attribution

Architecture:
- Merkle tree structure for tamper detection
- Block-based storage with cryptographic hashing
- Event sourcing pattern for complete audit trail
- Multi-signature validation for high-value insights
- Integration with RDR Engine for automatic recording
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import hashlib
import json
from collections import defaultdict
import secrets


class EventType(Enum):
    """Types of ledger events"""
    INSIGHT_CREATED = "insight_created"
    INSIGHT_VALIDATED = "insight_validated"
    UTID_MINTED = "utid_minted"
    UTID_TRANSFERRED = "utid_transferred"
    INSIGHT_CITED = "insight_cited"
    INSIGHT_PURCHASED = "insight_purchased"
    REVENUE_DISTRIBUTED = "revenue_distributed"
    PROOF_SCORE_UPDATED = "proof_score_updated"


class ValidationMethod(Enum):
    """Methods of insight validation"""
    PEER_REVIEW = "peer_review"
    COMPUTATIONAL = "computational"  # MSEP simulation
    CROSS_REFERENCE = "cross_reference"
    CITATION_COUNT = "citation_count"
    EXPERIMENTAL = "experimental"
    CONSENSUS = "consensus"  # Multi-validator agreement


@dataclass
class LedgerEvent:
    """Single event in the Proof-of-Insight ledger"""
    event_id: str
    event_type: EventType
    timestamp: datetime

    # Core data
    insight_id: str
    utid: Optional[str] = None

    # Participants
    creator_id: Optional[str] = None  # Original insight creator
    validator_id: Optional[str] = None  # Validator (person/system)
    from_owner: Optional[str] = None  # For transfers
    to_owner: Optional[str] = None  # For transfers

    # Validation details
    validation_method: Optional[ValidationMethod] = None
    proof_score: Optional[float] = None
    confidence: Optional[float] = None

    # Economic data
    transaction_amount: Optional[float] = None  # In credits
    revenue_share: Optional[Dict[str, float]] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Provenance
    source_papers: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)

    # Block reference
    block_hash: Optional[str] = None
    block_number: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for hashing/serialization"""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['timestamp'] = self.timestamp.isoformat()
        if self.validation_method:
            data['validation_method'] = self.validation_method.value
        return data

    def compute_hash(self) -> str:
        """Compute cryptographic hash of event"""
        event_data = self.to_dict()
        # Sort keys for deterministic hashing
        serialized = json.dumps(event_data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()


@dataclass
class LedgerBlock:
    """Block containing multiple events (blockchain-style)"""
    block_number: int
    timestamp: datetime
    events: List[LedgerEvent]

    # Blockchain fields
    previous_hash: str
    merkle_root: str
    nonce: str  # For tamper detection

    # Metadata
    validator_signatures: Dict[str, str] = field(default_factory=dict)

    def compute_merkle_root(self) -> str:
        """Compute Merkle root of all events in block"""
        if not self.events:
            return hashlib.sha256(b"empty").hexdigest()

        # Get all event hashes
        hashes = [event.compute_hash() for event in self.events]

        # Build Merkle tree
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])  # Duplicate last if odd

            new_level = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i+1]
                new_hash = hashlib.sha256(combined.encode()).hexdigest()
                new_level.append(new_hash)

            hashes = new_level

        return hashes[0]

    def compute_block_hash(self) -> str:
        """Compute hash of entire block"""
        block_data = {
            'block_number': self.block_number,
            'timestamp': self.timestamp.isoformat(),
            'previous_hash': self.previous_hash,
            'merkle_root': self.merkle_root,
            'nonce': self.nonce,
        }
        serialized = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify block integrity"""
        # Check Merkle root matches events
        computed_root = self.compute_merkle_root()
        return computed_root == self.merkle_root


@dataclass
class InsightOwnership:
    """Current ownership state of an insight UTID"""
    utid: str
    insight_id: str
    current_owner: str

    # Ownership history
    ownership_history: List[Dict[str, Any]] = field(default_factory=list)

    # Economic data
    total_revenue_generated: float = 0.0
    total_citations: int = 0
    total_purchases: int = 0

    # Validation state
    proof_score: float = 0.0
    validation_count: int = 0
    validation_methods: Set[str] = field(default_factory=set)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_transaction: Optional[datetime] = None


class ProofOfInsightLedger:
    """
    Proof-of-Insight Ledger

    Immutable ledger for tracking insight lifecycle:
    - Creation and validation
    - UTID minting and ownership
    - Citation and usage
    - Revenue generation

    Provides:
    - Complete audit trail
    - Tamper detection via Merkle trees
    - Ownership verification
    - Revenue attribution
    """

    def __init__(self):
        # Block storage
        self.blocks: List[LedgerBlock] = []
        self.pending_events: List[LedgerEvent] = []

        # Indexes for fast lookup
        self.events_by_insight: Dict[str, List[LedgerEvent]] = defaultdict(list)
        self.events_by_utid: Dict[str, List[LedgerEvent]] = defaultdict(list)
        self.events_by_creator: Dict[str, List[LedgerEvent]] = defaultdict(list)

        # Ownership tracking
        self.utid_ownership: Dict[str, InsightOwnership] = {}

        # Configuration
        self.events_per_block = 100  # Events before creating new block

        # Genesis block
        self._create_genesis_block()

    def _create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_event = LedgerEvent(
            event_id="genesis-event",
            event_type=EventType.INSIGHT_CREATED,
            timestamp=datetime.now(),
            insight_id="genesis",
            creator_id="system",
            metadata={'note': 'Proof-of-Insight Ledger initialized'}
        )

        genesis_block = LedgerBlock(
            block_number=0,
            timestamp=datetime.now(),
            events=[genesis_event],
            previous_hash="0" * 64,
            merkle_root="",
            nonce=secrets.token_hex(16)
        )

        genesis_block.merkle_root = genesis_block.compute_merkle_root()
        self.blocks.append(genesis_block)

    def record_insight_creation(
        self,
        insight_id: str,
        creator_id: str,
        source_papers: List[str],
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LedgerEvent:
        """Record insight creation event"""
        event = LedgerEvent(
            event_id=f"create-{insight_id}-{secrets.token_hex(4)}",
            event_type=EventType.INSIGHT_CREATED,
            timestamp=datetime.now(),
            insight_id=insight_id,
            creator_id=creator_id,
            confidence=confidence,
            source_papers=source_papers,
            metadata=metadata or {}
        )

        self._add_event(event)
        return event

    def record_validation(
        self,
        insight_id: str,
        validator_id: str,
        validation_method: ValidationMethod,
        proof_score: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LedgerEvent:
        """Record insight validation event"""
        event = LedgerEvent(
            event_id=f"validate-{insight_id}-{secrets.token_hex(4)}",
            event_type=EventType.INSIGHT_VALIDATED,
            timestamp=datetime.now(),
            insight_id=insight_id,
            validator_id=validator_id,
            validation_method=validation_method,
            proof_score=proof_score,
            metadata=metadata or {}
        )

        self._add_event(event)

        # Update ownership if UTID exists
        utid = self._get_utid_for_insight(insight_id)
        if utid and utid in self.utid_ownership:
            ownership = self.utid_ownership[utid]
            ownership.validation_count += 1
            ownership.validation_methods.add(validation_method.value)
            ownership.proof_score = max(ownership.proof_score, proof_score)

        return event

    def record_utid_minting(
        self,
        insight_id: str,
        utid: str,
        creator_id: str,
        proof_score: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LedgerEvent:
        """Record UTID minting event"""
        event = LedgerEvent(
            event_id=f"mint-{utid}-{secrets.token_hex(4)}",
            event_type=EventType.UTID_MINTED,
            timestamp=datetime.now(),
            insight_id=insight_id,
            utid=utid,
            creator_id=creator_id,
            proof_score=proof_score,
            metadata=metadata or {}
        )

        self._add_event(event)

        # Create ownership record
        self.utid_ownership[utid] = InsightOwnership(
            utid=utid,
            insight_id=insight_id,
            current_owner=creator_id,
            proof_score=proof_score,
            ownership_history=[{
                'owner': creator_id,
                'from': 'minting',
                'timestamp': datetime.now().isoformat(),
                'event': 'initial_mint'
            }]
        )

        return event

    def record_utid_transfer(
        self,
        utid: str,
        from_owner: str,
        to_owner: str,
        transaction_amount: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LedgerEvent:
        """Record UTID ownership transfer"""
        event = LedgerEvent(
            event_id=f"transfer-{utid}-{secrets.token_hex(4)}",
            event_type=EventType.UTID_TRANSFERRED,
            timestamp=datetime.now(),
            insight_id=self.utid_ownership[utid].insight_id,
            utid=utid,
            from_owner=from_owner,
            to_owner=to_owner,
            transaction_amount=transaction_amount,
            metadata=metadata or {}
        )

        self._add_event(event)

        # Update ownership
        if utid in self.utid_ownership:
            ownership = self.utid_ownership[utid]
            ownership.current_owner = to_owner
            ownership.last_transaction = datetime.now()
            ownership.ownership_history.append({
                'owner': to_owner,
                'from': from_owner,
                'timestamp': datetime.now().isoformat(),
                'amount': transaction_amount
            })

            if transaction_amount:
                ownership.total_purchases += 1

        return event

    def record_citation(
        self,
        insight_id: str,
        citing_paper_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LedgerEvent:
        """Record insight citation event"""
        event = LedgerEvent(
            event_id=f"cite-{insight_id}-{secrets.token_hex(4)}",
            event_type=EventType.INSIGHT_CITED,
            timestamp=datetime.now(),
            insight_id=insight_id,
            utid=self._get_utid_for_insight(insight_id),
            citations=[citing_paper_id],
            metadata=metadata or {}
        )

        self._add_event(event)

        # Update citation count
        utid = self._get_utid_for_insight(insight_id)
        if utid and utid in self.utid_ownership:
            self.utid_ownership[utid].total_citations += 1

        return event

    def record_revenue_distribution(
        self,
        utid: str,
        total_amount: float,
        revenue_share: Dict[str, float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> LedgerEvent:
        """Record revenue distribution event"""
        event = LedgerEvent(
            event_id=f"revenue-{utid}-{secrets.token_hex(4)}",
            event_type=EventType.REVENUE_DISTRIBUTED,
            timestamp=datetime.now(),
            insight_id=self.utid_ownership[utid].insight_id,
            utid=utid,
            transaction_amount=total_amount,
            revenue_share=revenue_share,
            metadata=metadata or {}
        )

        self._add_event(event)

        # Update total revenue
        if utid in self.utid_ownership:
            self.utid_ownership[utid].total_revenue_generated += total_amount

        return event

    def _add_event(self, event: LedgerEvent):
        """Add event to pending pool and create block if needed"""
        self.pending_events.append(event)

        # Update indexes
        self.events_by_insight[event.insight_id].append(event)
        if event.utid:
            self.events_by_utid[event.utid].append(event)
        if event.creator_id:
            self.events_by_creator[event.creator_id].append(event)

        # Create block if threshold reached
        if len(self.pending_events) >= self.events_per_block:
            self._create_block()

    def _create_block(self):
        """Create new block from pending events"""
        if not self.pending_events:
            return

        previous_block = self.blocks[-1]
        previous_hash = previous_block.compute_block_hash()

        new_block = LedgerBlock(
            block_number=len(self.blocks),
            timestamp=datetime.now(),
            events=self.pending_events.copy(),
            previous_hash=previous_hash,
            merkle_root="",
            nonce=secrets.token_hex(16)
        )

        # Compute Merkle root
        new_block.merkle_root = new_block.compute_merkle_root()

        # Update event block references
        block_hash = new_block.compute_block_hash()
        for event in new_block.events:
            event.block_hash = block_hash
            event.block_number = new_block.block_number

        self.blocks.append(new_block)
        self.pending_events.clear()

    def force_block_creation(self):
        """Force creation of block with pending events"""
        self._create_block()

    def _get_utid_for_insight(self, insight_id: str) -> Optional[str]:
        """Get UTID for insight if it exists"""
        for utid, ownership in self.utid_ownership.items():
            if ownership.insight_id == insight_id:
                return utid
        return None

    def get_insight_history(self, insight_id: str) -> List[LedgerEvent]:
        """Get complete history for an insight"""
        return self.events_by_insight.get(insight_id, [])

    def get_utid_history(self, utid: str) -> List[LedgerEvent]:
        """Get complete history for a UTID"""
        return self.events_by_utid.get(utid, [])

    def get_creator_insights(self, creator_id: str) -> List[LedgerEvent]:
        """Get all insights created by a user"""
        return self.events_by_creator.get(creator_id, [])

    def verify_ownership(self, utid: str, claimed_owner: str) -> bool:
        """Verify UTID ownership"""
        if utid not in self.utid_ownership:
            return False
        return self.utid_ownership[utid].current_owner == claimed_owner

    def get_ownership_info(self, utid: str) -> Optional[InsightOwnership]:
        """Get ownership information"""
        return self.utid_ownership.get(utid)

    def verify_chain_integrity(self) -> Tuple[bool, List[str]]:
        """Verify integrity of entire blockchain"""
        errors = []

        # Check genesis block
        if not self.blocks:
            return False, ["No genesis block"]

        if self.blocks[0].previous_hash != "0" * 64:
            errors.append("Invalid genesis block")

        # Check each block
        for i in range(1, len(self.blocks)):
            current_block = self.blocks[i]
            previous_block = self.blocks[i-1]

            # Verify previous hash
            expected_previous_hash = previous_block.compute_block_hash()
            if current_block.previous_hash != expected_previous_hash:
                errors.append(f"Block {i}: Invalid previous hash")

            # Verify Merkle root
            if not current_block.verify_integrity():
                errors.append(f"Block {i}: Invalid Merkle root")

            # Verify block number
            if current_block.block_number != i:
                errors.append(f"Block {i}: Invalid block number")

        return len(errors) == 0, errors

    def get_statistics(self) -> Dict[str, Any]:
        """Get ledger statistics"""
        total_events = sum(len(block.events) for block in self.blocks) + len(self.pending_events)

        event_type_counts = defaultdict(int)
        for block in self.blocks:
            for event in block.events:
                event_type_counts[event.event_type.value] += 1
        for event in self.pending_events:
            event_type_counts[event.event_type.value] += 1

        total_revenue = sum(ownership.total_revenue_generated for ownership in self.utid_ownership.values())
        total_citations = sum(ownership.total_citations for ownership in self.utid_ownership.values())

        return {
            'total_blocks': len(self.blocks),
            'total_events': total_events,
            'pending_events': len(self.pending_events),
            'total_utids': len(self.utid_ownership),
            'event_types': dict(event_type_counts),
            'total_revenue_tracked': total_revenue,
            'total_citations_tracked': total_citations,
            'average_proof_score': sum(o.proof_score for o in self.utid_ownership.values()) / len(self.utid_ownership) if self.utid_ownership else 0,
        }

    def export_ledger(self, start_block: int = 0, end_block: Optional[int] = None) -> Dict[str, Any]:
        """Export ledger data for archival/backup"""
        if end_block is None:
            end_block = len(self.blocks)

        return {
            'ledger_version': '1.0',
            'export_timestamp': datetime.now().isoformat(),
            'blocks': [
                {
                    'block_number': block.block_number,
                    'timestamp': block.timestamp.isoformat(),
                    'previous_hash': block.previous_hash,
                    'merkle_root': block.merkle_root,
                    'block_hash': block.compute_block_hash(),
                    'events': [event.to_dict() for event in block.events]
                }
                for block in self.blocks[start_block:end_block]
            ],
            'pending_events': [event.to_dict() for event in self.pending_events],
            'statistics': self.get_statistics()
        }


# Global ledger instance
_proof_ledger: Optional[ProofOfInsightLedger] = None


def get_proof_ledger() -> ProofOfInsightLedger:
    """Get or create global Proof-of-Insight ledger"""
    global _proof_ledger
    if _proof_ledger is None:
        _proof_ledger = ProofOfInsightLedger()
    return _proof_ledger
