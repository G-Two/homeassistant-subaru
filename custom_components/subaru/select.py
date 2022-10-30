"""Support for Subaru selectors."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN as SUBARU_DOMAIN,
    ENTRY_COORDINATOR,
    ENTRY_VEHICLES,
    VEHICLE_CLIMATE,
    VEHICLE_CLIMATE_PRESET_NAME,
    VEHICLE_CLIMATE_SELECTED_PRESET,
    VEHICLE_HAS_EV,
    VEHICLE_HAS_REMOTE_START,
    VEHICLE_VIN,
)
from .device import get_device_info

_LOGGER = logging.getLogger(__name__)

CLIMATE_SELECT = SelectEntityDescription(
    name="Climate preset", key=VEHICLE_CLIMATE, icon="mdi:thermometer-lines"
)
# Select naming scheme was inconsistent. Description below reflects previous naming for migration purposes.
OLD_CLIMATE_SELECT = SelectEntityDescription(name="climate_preset", key=VEHICLE_CLIMATE)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Subaru selectors by config_entry."""
    entry = hass.data[SUBARU_DOMAIN][config_entry.entry_id]
    coordinator = entry[ENTRY_COORDINATOR]
    vehicle_info = entry[ENTRY_VEHICLES]
    climate_select = []
    for info in vehicle_info.values():
        if info[VEHICLE_HAS_REMOTE_START] or info[VEHICLE_HAS_EV]:
            climate_select.append(SubaruClimateSelect(info, config_entry, coordinator))
    async_add_entities(climate_select)


class SubaruClimateSelect(SelectEntity, RestoreEntity):
    """Representation of a Subaru climate preset selector entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        vehicle_info: dict,
        config_entry: ConfigEntry,
        coordinator: DataUpdateCoordinator,
    ) -> None:
        """Initialize the selector for the vehicle."""
        self.coordinator = coordinator
        self.vin = vehicle_info[VEHICLE_VIN]
        self.config_entry = config_entry
        self.entity_description = CLIMATE_SELECT
        self._attr_current_option = ""
        self._attr_device_info = get_device_info(vehicle_info)
        self._attr_unique_id = f"{self.vin}_{self.entity_description.key}"

    @property
    def options(self) -> list:
        """Return a set of selectable options."""
        vehicle_data = None
        if self.coordinator.data:
            vehicle_data = self.coordinator.data.get(self.vin)
        if vehicle_data:
            if isinstance(
                preset_data := vehicle_data.get(self.entity_description.key), list
            ):
                return [preset[VEHICLE_CLIMATE_PRESET_NAME] for preset in preset_data]
        return []

    async def async_added_to_hass(self) -> None:
        """Restore previous state of this selector."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        if state and (state.state in self.options):
            self._attr_current_option = state.state
            self.coordinator.data.get(self.vin)[
                VEHICLE_CLIMATE_SELECTED_PRESET
            ] = state.state
            self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        _LOGGER.debug(
            "Selecting %s climate preset for %s", option, self.device_info["name"]
        )
        if option in self.options:
            self._attr_current_option = option
            self.coordinator.data.get(self.vin)[
                VEHICLE_CLIMATE_SELECTED_PRESET
            ] = option
            self.async_write_ha_state()
