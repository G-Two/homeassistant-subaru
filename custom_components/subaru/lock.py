"""Support for Subaru door locks."""

from __future__ import annotations

import logging
from typing import Any

from subarulink.const import (
    LOCK_BOOT_STATUS,
    LOCK_FRONT_LEFT_STATUS,
    LOCK_FRONT_RIGHT_STATUS,
    LOCK_LOCKED,
    LOCK_REAR_LEFT_STATUS,
    LOCK_REAR_RIGHT_STATUS,
)
from subarulink.controller import Controller
import voluptuous as vol

from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import SERVICE_LOCK, SERVICE_UNLOCK
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import DOMAIN
from .const import (
    ATTR_DOOR,
    CONF_NOTIFICATION_OPTION,
    ENTRY_CONTROLLER,
    ENTRY_COORDINATOR,
    ENTRY_VEHICLES,
    SERVICE_UNLOCK_SPECIFIC_DOOR,
    UNLOCK_DOOR_ALL,
    UNLOCK_VALID_DOORS,
    VEHICLE_HAS_LOCK_STATUS,
    VEHICLE_HAS_REMOTE_SERVICE,
    VEHICLE_NAME,
    VEHICLE_STATUS,
    VEHICLE_VIN,
)
from .device import get_device_info
from .remote_service import async_call_remote_service

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Subaru locks by config_entry."""
    entry = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = entry[ENTRY_COORDINATOR]
    controller = entry[ENTRY_CONTROLLER]
    vehicle_info = entry[ENTRY_VEHICLES]
    async_add_entities(
        SubaruLock(vehicle, coordinator, controller, config_entry)
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

    Note that the Subaru API currently does not support returning the status of the locks. Lock status is always unknown.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "door_locks"

    def __init__(
        self,
        vehicle_info: dict,
        coordinator: DataUpdateCoordinator,
        controller: Controller,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the locks for the vehicle."""
        self.controller = controller
        self.coordinator = coordinator
        self.config_entry = config_entry
        self.vehicle_info = vehicle_info
        self.vin = vehicle_info[VEHICLE_VIN]
        self.car_name = vehicle_info[VEHICLE_NAME]
        self.lock_status_available = self.vehicle_info[VEHICLE_HAS_LOCK_STATUS]
        self._attr_unique_id = f"{self.vin}_door_locks"
        self._attr_device_info = get_device_info(vehicle_info)

    async def async_lock(self, **kwargs: Any) -> None:
        """Send the lock command."""
        _LOGGER.debug("Locking doors for: %s", self.car_name)
        if self.lock_status_available:
            self._attr_is_locking = True
            self.async_write_ha_state()
        await async_call_remote_service(
            self.hass,
            self.controller,
            SERVICE_LOCK,
            self.vehicle_info,
            None,
            self.config_entry.options.get(CONF_NOTIFICATION_OPTION),
        )
        if self.lock_status_available:
            await self.coordinator.async_request_refresh()

    async def async_unlock(self, **kwargs: Any) -> None:
        """Send the unlock command."""
        _LOGGER.debug("Unlocking doors for: %s", self.car_name)
        if self.lock_status_available:
            self._attr_is_unlocking = True
            self.async_write_ha_state()
        await async_call_remote_service(
            self.hass,
            self.controller,
            SERVICE_UNLOCK,
            self.vehicle_info,
            UNLOCK_VALID_DOORS[UNLOCK_DOOR_ALL],
            self.config_entry.options.get(CONF_NOTIFICATION_OPTION),
        )
        if self.lock_status_available:
            await self.coordinator.async_request_refresh()

    @property
    def is_locked(self) -> bool | None:
        """Return true if all doors are locked."""
        if self.lock_status_available:
            for door in [
                LOCK_BOOT_STATUS,
                LOCK_FRONT_LEFT_STATUS,
                LOCK_FRONT_RIGHT_STATUS,
                LOCK_REAR_LEFT_STATUS,
                LOCK_REAR_RIGHT_STATUS,
            ]:
                if (
                    self.coordinator.data[self.vin][VEHICLE_STATUS].get(door)
                    == LOCK_LOCKED
                ):
                    continue
                return False
            return True
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return entity specific state attributes."""
        if self.lock_status_available:
            return {
                LOCK_BOOT_STATUS: self.coordinator.data[self.vin][VEHICLE_STATUS].get(
                    LOCK_BOOT_STATUS
                ),
                LOCK_FRONT_LEFT_STATUS: self.coordinator.data[self.vin][
                    VEHICLE_STATUS
                ].get(LOCK_FRONT_LEFT_STATUS),
                LOCK_FRONT_RIGHT_STATUS: self.coordinator.data[self.vin][
                    VEHICLE_STATUS
                ].get(LOCK_FRONT_RIGHT_STATUS),
                LOCK_REAR_LEFT_STATUS: self.coordinator.data[self.vin][
                    VEHICLE_STATUS
                ].get(LOCK_REAR_LEFT_STATUS),
                LOCK_REAR_RIGHT_STATUS: self.coordinator.data[self.vin][
                    VEHICLE_STATUS
                ].get(LOCK_REAR_RIGHT_STATUS),
            }

    async def async_unlock_specific_door(self, door: str) -> None:
        """Send the unlock command for a specified door."""
        _LOGGER.debug("Unlocking %s door for: %s", self, self.car_name)
        if self.lock_status_available:
            self._attr_is_unlocking = True
            self.async_write_ha_state()
        await async_call_remote_service(
            self.hass,
            self.controller,
            SERVICE_UNLOCK,
            self.vehicle_info,
            UNLOCK_VALID_DOORS[door],
            self.config_entry.options.get(CONF_NOTIFICATION_OPTION),
        )
        if self.lock_status_available:
            await self.coordinator.async_request_refresh()
