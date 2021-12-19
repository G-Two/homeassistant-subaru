"""Support for Subaru door locks."""
import logging

from homeassistant.components.lock import DOMAIN as LOCK_DOMAIN, LockEntity
from homeassistant.const import SERVICE_LOCK, SERVICE_UNLOCK

from . import DOMAIN as SUBARU_DOMAIN
from .const import (
    CONF_NOTIFICATION_OPTION,
    ENTRY_CONTROLLER,
    ENTRY_COORDINATOR,
    ENTRY_VEHICLES,
    VEHICLE_HAS_REMOTE_SERVICE,
)
from .entity import SubaruEntity
from .remote_service import async_call_remote_service

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Subaru locks by config_entry."""
    controller = hass.data[SUBARU_DOMAIN][config_entry.entry_id][ENTRY_CONTROLLER]
    coordinator = hass.data[SUBARU_DOMAIN][config_entry.entry_id][ENTRY_COORDINATOR]
    vehicle_info = hass.data[SUBARU_DOMAIN][config_entry.entry_id][ENTRY_VEHICLES]
    entities = []
    for vehicle in vehicle_info.values():
        if vehicle[VEHICLE_HAS_REMOTE_SERVICE]:
            entities.append(SubaruLock(vehicle, coordinator, controller, config_entry))
    async_add_entities(entities, True)


class SubaruLock(SubaruEntity, LockEntity):
    """
    Representation of a Subaru door lock.

    Note that the Subaru API currently does not support returning the status of the locks.
    Lock status is always unknown.
    """

    def __init__(self, vehicle_info, coordinator, controller, config_entry):
        """Initialize the locks for the vehicle."""
        super().__init__(vehicle_info, coordinator)
        self.entity_type = "Door Lock"
        self.hass_type = LOCK_DOMAIN
        self.controller = controller
        self.config_entry = config_entry

    async def async_lock(self, **kwargs):
        """Send the lock command."""
        _LOGGER.debug("Locking doors for: %s", self.vin)
        await async_call_remote_service(
            self.hass,
            self.controller,
            SERVICE_LOCK,
            self.vehicle_info,
            self.config_entry.options.get(CONF_NOTIFICATION_OPTION),
        )

    async def async_unlock(self, **kwargs):
        """Send the unlock command."""
        _LOGGER.debug("Unlocking doors for: %s", self.vin)
        await async_call_remote_service(
            self.hass,
            self.controller,
            SERVICE_UNLOCK,
            self.vehicle_info,
            self.config_entry.options.get(CONF_NOTIFICATION_OPTION),
        )
