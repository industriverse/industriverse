from enum import Enum


class UTIDEventType(str, Enum):
    GENERATED = "utid_generated"
    VERIFIED = "utid_verified"
    ATTACHED = "utid_attached"
    INVALID = "utid_invalid"
