from enum import Enum


class ActivationState(Enum):
    DISABLED = "disabled"
    ARMING = "arming"
    ACTIVE = "active"
    COOLDOWN = "cooldown"