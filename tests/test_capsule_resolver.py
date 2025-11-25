from src.protocol_layer.protocols.capsule_resolver import CapsuleResolver
from src.protocol_layer.protocols.capsule_uri import parse_capsule_uri
from src.protocol_layer.protocols.credit_ledger import CreditLedger
from src.protocol_layer.protocols.registry import InMemoryRegistry
from src.protocol_layer.protocols.mesh_client import MockMeshClient
from src.protocol_layer.protocols.sandbox import DeterministicSandbox


def test_resolver_local_resolution_and_execution():
    registry = InMemoryRegistry()
    mesh = MockMeshClient()
    ledger = CreditLedger()
    sandbox = DeterministicSandbox()

    uri = parse_capsule_uri("capsule://fusion/mhd64/v4.1")
    registry.register(
        uri,
        {
            "utid": "fake",
            "credit_root": "root",
            "location": "/tmp/fake",
            "execution_cost": 1.0,
        },
    )

    resolver = CapsuleResolver(registry=registry, mesh_client=mesh, ledger=ledger, sandbox=sandbox)
    result = resolver.resolve(uri.to_uri())
    assert result.status == 200
    assert result.utid == "fake"


def test_resolver_mesh_resolution_fallback():
    registry = InMemoryRegistry()
    mesh = MockMeshClient()
    ledger = CreditLedger()
    sandbox = DeterministicSandbox()

    uri = parse_capsule_uri("capsule://fusion/mhd64/v4.1")
    mesh.register_remote(
        uri,
        {
            "utid": "mesh-utid",
            "credit_root": "root",
            "location": "/remote/fake",
            "execution_cost": 2.0,
        },
    )

    resolver = CapsuleResolver(registry=registry, mesh_client=mesh, ledger=ledger, sandbox=sandbox)
    result = resolver.resolve(uri.to_uri())
    assert result.status == 200
    assert result.utid == "mesh-utid"
