"""Enums for Subaru integration config options."""

from enum import Enum


class ConfigOptionsEnum(Enum):
    """Base class for Config UI options enums."""

    @classmethod
    def list(cls):
        """List values."""
        return [item.value for item in cls]

    @classmethod
    def get_by_value(cls, value):
        """Get enum instance by value."""
        result = None
        for item in cls:
            if item.value == value:
                result = item
        return result


class NotificationOptions(ConfigOptionsEnum):
    """Lovelace levels of notification."""

    DISABLE = "Disable — No notifications will appear"
    FAILURE = "Failure — Only notify on failure"
    PENDING = "Pending — Temporary notification of remote command in progress"
    SUCCESS = "Success — Persistent notification of completed remote command"


class PollingOptions(ConfigOptionsEnum):
    """Options for vehicle polling."""

    DISABLE = "Disable — Do not poll vehicle (vehicle will still push update when engine is turned off)"
    CHARGING = "Charge Only — Poll vehicle every 30 minutes during charging only"
    ENABLE = "Enable — Poll vehicle every 2 hours"
