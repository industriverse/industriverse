import functools
from typing import Any, Callable, Dict

from src.proof_core.integrity_layer.integrity_manager import IntegrityManager


def proof_hook(domain: str):
    """
    Decorator to attach proof recording to a function.
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            manager = IntegrityManager()
            utid = kwargs.get("utid") or "UTID:REAL:unknown"
            result = await func(*args, **kwargs)
            try:
                await manager.record_action(
                    utid=utid,
                    domain=domain,
                    inputs={"args": str(args), "kwargs": str(kwargs)},
                    outputs={"result": str(result)},
                )
            except Exception:
                # Best-effort; avoid breaking primary flow
                pass
            return result

        return wrapper

    return decorator
