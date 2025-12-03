class CodegenStateMachine:
    """
    Manages the lifecycle states of the code generation process.
    """
    STATES = [
        "GATHER_REQUIREMENTS",
        "GENERATE_CODE",
        "STATIC_ANALYSIS",
        "SIMULATE",
        "DYNAMIC_TEST",
        "DEPLOY",
        "CFR_LOG",
        "ZK_MINT"
    ]

    def __init__(self):
        self.state = self.STATES[0]

    def next_state(self) -> None:
        """
        Transitions to the next state in the lifecycle.
        """
        idx = self.STATES.index(self.state)
        if idx < len(self.STATES) - 1:
            self.state = self.STATES[idx + 1]
            
    def get_current_state(self) -> str:
        return self.state
