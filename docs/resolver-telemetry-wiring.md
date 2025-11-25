# Resolver → Twin Sync Telemetry Wiring (Phase 4 glue)

Goal: ensure capsule_resolver emits the contract defined in `shadow-twin-telemetry-contract.md` using the TelemetryEmitter.

## Components
- `capsule_resolver.CapsuleResolver` now accepts `emitter` and calls `_emit` on status/proof/credit events.
- `twin_sync.emitter.TelemetryEmitter` logs or forwards to a sink (websocket/bus).
- UI subscribes to topics: `capsule.status`, `capsule.proof`, `capsule.credit_flow`.

## Integration Steps
1) Instantiate `TelemetryEmitter` with a sink that publishes to `twin_sync` websocket or message bus.
2) Pass emitter into `CapsuleResolver`.
3) Ensure sandbox execution returns telemetry fields: `latency_ms`, `proof_hash`, `entropy_delta`, `timestamp`, `execution_cost`, `author_split`, `executor_split`, `mesh_split`, `balance_after`.
4) Map emitted events to UI widgets (ReactorGauge, TruthSigil, Constellation, EnergyField) per telemetry contract.
5) For production bus, use `BusEmitter` with Kafka/NATS publish function; ensure topics mirror telemetry contract.

## Reliability
- Add retry/backoff on emit failures in production wiring.
- Use event ids for de-duplication when wired to bus.
