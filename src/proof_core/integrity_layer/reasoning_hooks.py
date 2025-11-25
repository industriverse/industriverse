import functools
from typing import Any, Callable, Dict, Optional

from src.proof_core.integrity_layer.integrity_manager import IntegrityManager


def reasoning_step(domain: str):
    """
    Decorator to emit a proof record for a reasoning step (ACE/DGM/TUMIX/Nanochat).
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            manager = IntegrityManager()
            utid = kwargs.get("utid") or "UTID:REAL:unknown"
            inputs = {"args": str(args), "kwargs": str(kwargs)}
            result = await func(*args, **kwargs)
            outputs = {"result": str(result)}
            metadata = kwargs.get("proof_metadata") or {}
            try:
                await manager.record_action(
                    utid=utid,
                    domain=domain,
                    inputs=inputs,
                    outputs=outputs,
                    metadata=metadata,
                )
            except Exception:
                pass
            return result

        return wrapper

    return decorator


async def record_reasoning_edge(
    utid: str,
    domain: str,
    node_id: str,
    inputs: Dict[str, Any],
    outputs: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Helper to record a reasoning DAG edge without decoration.
    """
    manager = IntegrityManager()
    meta = metadata or {}
    meta["node_id"] = node_id
    await manager.record_action(
        utid=utid,
        domain=domain,
        inputs=inputs,
        outputs=outputs,
        metadata=meta,
    )
