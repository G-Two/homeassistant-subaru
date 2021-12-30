"""Support for Subaru door locks."""
import logging

import voluptuous as vol

from homeassistant.components.lock import DOMAIN as LOCK_DOMAIN, LockEntity
from homeassistant.const import SERVICE_LOCK, SERVICE_UNLOCK
from homeassistant.helpers import config_validation as cv, entity_platform

from . import DOMAIN as SUBARU_DOMAIN
from .const import (
    ATTR_DOOR,
    CONF_NOTIFICATION_OPTION,
    ENTRY_CONTROLLER,
    ENTRY_COORDINATOR,
    ENTRY_VEHICLES,
    SERVICE_UNLOCK_SPECIFIC_DOOR,
    UNLOCK_DOOR_ALL,
    UNLOCK_VALID_DOORS,
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

    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        SERVICE_UNLOCK_SPECIFIC_DOOR,
        {vol.Required(ATTR_DOOR): cv.string},
        "async_unlock_specific_door",
    )


class SubaruLock(SubaruEntity, LockEntity):
    """
    Representation of a Subaru door lock.

    Note that the Subaru API currently does not support returning the status of the locks.
    Lock status is always unknown.
    """

    def __init__(self, vehicle_info, coordinator, controller, config_entry):
        """Initialize the locks for the vehicle."""
        super().__init__(vehicle_info, coordinator)
        self.entity_type = "Door Locks"
        self.hass_type = LOCK_DOMAIN
        self.controller = controller
        self.config_entry = config_entry

    async def async_lock(self, **kwargs):
        """Send the lock command."""
        _LOGGER.debug("Locking doors for: %s", self.car_name)
        await async_call_remote_service(
            self.hass,
            self.controller,
            SERVICE_LOCK,
            self.vehicle_info,
            None,
            self.config_entry.options.get(CONF_NOTIFICATION_OPTION),
        )

    async def async_unlock(self, **kwargs):
        """Send the unlock command."""
        _LOGGER.debug("Unlocking doors for: %s", self.car_name)
        await async_call_remote_service(
            self.hass,
            self.controller,
            SERVICE_UNLOCK,
            self.vehicle_info,
            UNLOCK_VALID_DOORS[UNLOCK_DOOR_ALL],
            self.config_entry.options.get(CONF_NOTIFICATION_OPTION),
        )

    async def async_unlock_specific_door(self, door):
        """Send the unlock command for a specified door."""
        _LOGGER.debug("Unlocking %s door for: %s", self, self.car_name)
        if door in UNLOCK_VALID_DOORS:
            await async_call_remote_service(
                self.hass,
                self.controller,
                SERVICE_UNLOCK,
                self.vehicle_info,
                UNLOCK_VALID_DOORS[door],
                self.config_entry.options.get(CONF_NOTIFICATION_OPTION),
            )
