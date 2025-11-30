# Machine Capsule Negotiation Protocol (MCNP) - RFC Draft

**Status**: Experimental
**Version**: 0.1.0

---

## 1. Abstract
MCNP is a protocol for autonomous agents to negotiate the exchange of thermodynamic value (Negentropy) for tokens (Capsules/Credits). It operates over the A2A bus.

## 2. Message Types

### 2.1 ASK (Request for Task)
An agent broadcasts a need for a specific capability.
```json
{
  "type": "ASK",
  "payload": {
    "task_type": "WELDING_V1",
    "max_price": 0.50,
    "deadline": 1735689600
  }
}
```

### 2.2 BID (Offer of Service)
An agent responds with a price and capability proof.
```json
{
  "type": "BID",
  "payload": {
    "price": 0.45,
    "negentropy_score": 98.5,
    "zk_proof": "0x123abc...",
    "estimated_duration": 120
  }
}
```

### 2.3 ACCEPT (Contract Formation)
The requester accepts a specific BID.
```json
{
  "type": "ACCEPT",
  "payload": {
    "bid_id": "bid_uuid",
    "escrow_tx": "xrpl_tx_hash"
  }
}
```

### 2.4 REJECT (Bid Denial)
The requester rejects a BID (optional, usually silent).

## 3. ZK-Proof Verification
All BIDs MUST include a Zero-Knowledge Proof verifying:
1.  **Capability**: The agent possesses the required Capsule.
2.  **Safety**: The agent's safety record meets the threshold.
3.  **Identity**: The agent is a verified member of the mesh.

## 4. State Machine
1.  **IDLE** -> Receive ASK -> **ANALYZING**
2.  **ANALYZING** -> Send BID -> **BIDDING**
3.  **BIDDING** -> Receive ACCEPT -> **CONTRACTED**
4.  **CONTRACTED** -> Execute -> **COMPLETE**
