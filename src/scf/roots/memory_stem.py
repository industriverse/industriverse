from typing import Any, List, Dict

class MemoryStem:
    """
    Long-term memory reservoir for the Sovereign Code Foundry.
    Stores success/failure patterns and structural templates.
    """
    def __init__(self):
        self.success_cache = []
        self.failure_cache = []
        self.archives = {}

    def record_success(self, code_artifact: Any) -> None:
        """
        Records a successful code generation attempt.
        """
        self.success_cache.append(code_artifact)

    def record_failure(self, code_artifact: Any, reason: str) -> None:
        """
        Records a failed attempt with the reason for failure.
        """
        self.failure_cache.append({"artifact": code_artifact, "reason": reason})

    def retrieve_patterns(self) -> List[Any]:
        """
        Retrieves successful coding patterns relevant to the current context.
        """
        return self.success_cache
