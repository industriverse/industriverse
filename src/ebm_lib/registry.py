import importlib
from typing import Dict

_registry: Dict[str, str] = {}

def register(name: str, module_path: str):
    _registry[name] = module_path

def get(name: str):
    if name not in _registry:
        raise ValueError(f"Energy Prior '{name}' not found in registry.")
    module = importlib.import_module(_registry[name])
    return module.PRIOR
