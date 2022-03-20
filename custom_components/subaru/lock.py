"""Support for Subaru door locks."""
import logging

import voluptuous as vol

from homeassistant.components.lock import LockEntity
from homeassistant.const import SERVICE_LOCK, SERVICE_UNLOCK
from homeassistant.helpers import entity_platform

from . import DOMAIN as SUBARU_DOMAIN, get_device_info
from .const import (
    ATTR_DOOR,
    CONF_NOTIFICATION_OPTION,
    ENTRY_CONTROLLER,
    ENTRY_VEHICLES,
    SERVICE_UNLOCK_SPECIFIC_DOOR,
    UNLOCK_DOOR_ALL,
    UNLOCK_VALID_DOORS,
    VEHICLE_HAS_REMOTE_SERVICE,
    VEHICLE_NAME,
    VEHICLE_VIN,
)
from .remote_service import async_call_remote_service

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Subaru locks by config_entry."""
    entry = hass.data[SUBARU_DOMAIN][config_entry.entry_id]
    controller = entry[ENTRY_CONTROLLER]
    vehicle_info = entry[ENTRY_VEHICLES]

    async_add_entities(
        SubaruLock(vehicle, controller, config_entry)
        for vehicle in vehicle_info.values()
        if vehicle[VEHICLE_HAS_REMOTE_SERVICE]
    )

    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        SERVICE_UNLOCK_SPECIFIC_DOOR,
        {vol.Required(ATTR_DOOR): vol.In(UNLOCK_VALID_DOORS)},
        "async_unlock_specific_door",
    )


class SubaruLock(LockEntity):
    """
    Representation of a Subaru door lock.

    Note that the Subaru API currently does not support returning the status of the locks.
    Lock status is always unknown.
    """

    def __init__(self, vehicle_info, controller, config_entry):
        """Initialize the locks for the vehicle."""
        self.controller = controller
        self.vehicle_info = vehicle_info
        self.car_name = vehicle_info[VEHICLE_NAME]
        self.config_entry = config_entry
        self._attr_name = f"{self.car_name} Door Locks"
        self._attr_unique_id = f"{vehicle_info[VEHICLE_VIN]}_door_locks"
        self._attr_device_info = get_device_info(vehicle_info)

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
        await async_call_remote_service(
            self.hass,
            self.controller,
            SERVICE_UNLOCK,
            self.vehicle_info,
            UNLOCK_VALID_DOORS[door],
            self.config_entry.options.get(CONF_NOTIFICATION_OPTION),
        )
