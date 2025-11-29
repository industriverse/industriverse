class BytecodeSanitizer:
    """
    AI Shield v3 - Gate 2: Bytecode Sanitization.
    Cleans and clamps Industrial Bytecode (IB) instructions to safe limits.
    """
    def __init__(self):
        self.limits = {
            "SPINDLE_RPM": 12000,
            "FEED_RATE": 5000,
            "TEMP_NOZZLE": 280,
            "TEMP_BED": 110
        }
        self.forbidden_ops = ["OP_OVERRIDE_SAFETY", "OP_DEBUG_CRASH"]

    def sanitize(self, bytecode_program):
        """
        Input: List of instruction dicts
        Output: { sanitized_program: [], modifications: [] }
        """
        sanitized = []
        modifications = []

        for op in bytecode_program:
            op_code = op.get("op")
            params = op.get("params", {})
            
            # 1. Opcode Whitelist
            if op_code in self.forbidden_ops:
                modifications.append(f"Removed forbidden op: {op_code}")
                continue # Skip this instruction

            # 2. Parameter Clamping
            new_params = params.copy()
            if op_code == "OP_SPINDLE":
                rpm = params.get("rpm", 0)
                if rpm > self.limits["SPINDLE_RPM"]:
                    new_params["rpm"] = self.limits["SPINDLE_RPM"]
                    modifications.append(f"Clamped SPINDLE_RPM from {rpm} to {self.limits['SPINDLE_RPM']}")
            
            if op_code == "OP_HEAT":
                temp = params.get("temp", 0)
                target = params.get("target", "nozzle")
                limit = self.limits.get(f"TEMP_{target.upper()}", 250)
                if temp > limit:
                    new_params["temp"] = limit
                    modifications.append(f"Clamped TEMP_{target.upper()} from {temp} to {limit}")

            sanitized.append({"op": op_code, "params": new_params})

        return {
            "sanitized_program": sanitized,
            "modifications": modifications
        }

if __name__ == "__main__":
    sanitizer = BytecodeSanitizer()
    program = [
        {"op": "OP_SPINDLE", "params": {"rpm": 15000}},
        {"op": "OP_OVERRIDE_SAFETY", "params": {}},
        {"op": "OP_MOVE", "params": {"x": 10, "y": 10}}
    ]
    print(sanitizer.sanitize(program))
