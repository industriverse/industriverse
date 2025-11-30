import re

class TelosClassifier:
    """
    Challenge #2: Self-Healing Industrial Systems.
    Classifies failure logs to determine the appropriate recovery strategy.
    """
    def __init__(self):
        self.patterns = {
            "TRANSIENT_NETWORK": [
                r"Connection timed out",
                r"Network unreachable",
                r"503 Service Unavailable"
            ],
            "HARDWARE_FAULT": [
                r"Servo overload",
                r"Thermal shutdown",
                r"Emergency Stop Triggered"
            ],
            "CONFIG_ERROR": [
                r"FileNotFoundError",
                r"KeyError",
                r"Invalid configuration"
            ],
            "MODEL_DRIFT": [
                r"Physics Violation",
                r"Drift detected"
            ]
        }

    def classify_failure(self, log_entry):
        """
        Classifies a log entry into a failure category.
        Returns: (Category, Confidence, RecommendedAction)
        """
        for category, regex_list in self.patterns.items():
            for pattern in regex_list:
                if re.search(pattern, log_entry, re.IGNORECASE):
                    return category, 1.0, self._get_recommendation(category)
        
        return "UNKNOWN", 0.0, "ESCALATE_TO_HUMAN"

    def _get_recommendation(self, category):
        if category == "TRANSIENT_NETWORK":
            return "RETRY_EXPONENTIAL_BACKOFF"
        elif category == "HARDWARE_FAULT":
            return "HALT_AND_ALERT"
        elif category == "CONFIG_ERROR":
            return "ATTEMPT_AUTO_PATCH" # Telos Agent would generate patch
        elif category == "MODEL_DRIFT":
            return "TRIGGER_ALETHEIA_RECALIBRATION"
        return "ESCALATE"
