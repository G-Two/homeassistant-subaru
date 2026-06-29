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
    LOCK_UNKNOWN,
)
from subarulink.controller import Controller
from subarulink.exceptions import SubaruException
import voluptuous as vol

from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import SERVICE_LOCK, SERVICE_UNLOCK
from homeassistant.core import CALLBACK_TYPE, HassJob, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

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
from .remote_service import async_call_remote_service, poll_subaru, refresh_subaru

# Vehicle auto-relocks ~30s after a remote unlock if no door is opened.
# Poll past that window to capture the final post-relock state.
UNLOCK_VERIFY_DELAY_SEC = 45

LOCK_DOORS = (
    LOCK_BOOT_STATUS,
    LOCK_FRONT_LEFT_STATUS,
    LOCK_FRONT_RIGHT_STATUS,
    LOCK_REAR_LEFT_STATUS,
    LOCK_REAR_RIGHT_STATUS,
)

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


class SubaruLock(CoordinatorEntity[DataUpdateCoordinator[dict[str, Any]]], LockEntity):
    """
    Representation of a Subaru door lock.

    Vehicles that report lock status surface it via the is_locked property,
    which is kept in sync with the data update coordinator. Vehicles that do
    not report lock status always present an unknown lock state.
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
        super().__init__(coordinator)
        self.controller = controller
        self.config_entry = config_entry
        self.vehicle_info = vehicle_info
        self.vin = vehicle_info[VEHICLE_VIN]
        self.car_name = vehicle_info[VEHICLE_NAME]
        self.lock_status_available = self.vehicle_info[VEHICLE_HAS_LOCK_STATUS]
        self._attr_unique_id = f"{self.vin}_door_locks"
        self._attr_device_info = get_device_info(vehicle_info)
        self._verify_cancel: CALLBACK_TYPE | None = None
        self._verify_job = HassJob(
            self._verify_lock_state,
            name=f"subaru_lock_verify_{self.vin}",
            cancel_on_shutdown=True,
        )

    async def async_added_to_hass(self) -> None:
        """Register cleanup of any pending verify-poll timer."""
        await super().async_added_to_hass()
        self.async_on_remove(self._cancel_pending_verify)

    @callback
    def _cancel_pending_verify(self) -> None:
        """Cancel a pending delayed verify poll, if any."""
        if self._verify_cancel is not None:
            self._verify_cancel()
            self._verify_cancel = None

    async def _verify_lock_state(self, _: Any = None) -> None:
        """Force a vehicle poll to resolve the true lock state."""
        self._verify_cancel = None
        _LOGGER.debug("Verifying lock state for %s via vehicle poll", self.car_name)
        try:
            await poll_subaru(self.vehicle_info, self.controller, update_interval=0)
            await refresh_subaru(self.vehicle_info, self.controller, refresh_interval=0)
        except SubaruException as err:
            _LOGGER.warning(
                "Lock state verification poll failed for %s: %s",
                self.car_name,
                err.message,
            )
        if self.lock_status_available:
            self._attr_is_locking = False
            self._attr_is_unlocking = False
        self.coordinator.async_update_listeners()

    def _schedule_unlock_verify(self) -> None:
        """Schedule a delayed poll past the auto-relock window."""
        self._cancel_pending_verify()
        self._verify_cancel = async_call_later(
            self.hass, UNLOCK_VERIFY_DELAY_SEC, self._verify_job
        )

    async def async_lock(self, **kwargs: Any) -> None:
        """Send the lock command."""
        _LOGGER.debug("Locking doors for: %s", self.car_name)
        self._cancel_pending_verify()
        if self.lock_status_available:
            self._attr_is_locking = True
            self.async_write_ha_state()
        try:
            await async_call_remote_service(
                self.hass,
                self.controller,
                SERVICE_LOCK,
                self.vehicle_info,
                None,
                self.config_entry.options.get(CONF_NOTIFICATION_OPTION),
            )
        except HomeAssistantError as err:
            if self.lock_status_available:
                self._attr_is_locking = False
            self.coordinator.async_update_listeners()
            raise HomeAssistantError("Failed to lock doors") from err
        # is_locked reads coordinator.data[vin][VEHICLE_STATUS], which is the
        # same dict reference as subarulink's internal cache (returned by
        # controller.get_data and never copied). The fetch inside
        # async_call_remote_service mutates that cache in place, so this check
        # sees fresh post-command state without an explicit coordinator refresh.
        if self.lock_status_available and self.is_locked is None:
            await self._verify_lock_state()
        else:
            if self.lock_status_available:
                self._attr_is_locking = False
            self.coordinator.async_update_listeners()

    async def async_unlock(self, **kwargs: Any) -> None:
        """Send the unlock command."""
        _LOGGER.debug("Unlocking doors for: %s", self.car_name)
        if self.lock_status_available:
            self._attr_is_unlocking = True
            self.async_write_ha_state()
        try:
            await async_call_remote_service(
                self.hass,
                self.controller,
                SERVICE_UNLOCK,
                self.vehicle_info,
                UNLOCK_VALID_DOORS[UNLOCK_DOOR_ALL],
                self.config_entry.options.get(CONF_NOTIFICATION_OPTION),
            )
        except HomeAssistantError as err:
            if self.lock_status_available:
                self._attr_is_unlocking = False
            self.coordinator.async_update_listeners()
            raise HomeAssistantError("Failed to unlock doors") from err
        if self.lock_status_available:
            self._schedule_unlock_verify()
        else:
            self.coordinator.async_update_listeners()

    @property
    def is_locked(self) -> bool | None:
        """Return true if all doors are locked, None if any door is unknown."""
        if not self.lock_status_available:
            return None
        if self.vin not in self.coordinator.data:
            return None
        status = self.coordinator.data[self.vin][VEHICLE_STATUS]
        states = [status.get(door) for door in LOCK_DOORS]
        if any(s is None or s == LOCK_UNKNOWN for s in states):
            return None
        return all(s == LOCK_LOCKED for s in states)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return entity specific state attributes."""
        if self.lock_status_available:
            if self.vin not in self.coordinator.data:
                return None
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
        try:
            await async_call_remote_service(
                self.hass,
                self.controller,
                SERVICE_UNLOCK,
                self.vehicle_info,
                UNLOCK_VALID_DOORS[door],
                self.config_entry.options.get(CONF_NOTIFICATION_OPTION),
            )
        except HomeAssistantError as err:
            if self.lock_status_available:
                self._attr_is_unlocking = False
            self.coordinator.async_update_listeners()
            raise HomeAssistantError("Failed to unlock doors") from err
        if self.lock_status_available:
            self._schedule_unlock_verify()
        else:
            self.coordinator.async_update_listeners()
