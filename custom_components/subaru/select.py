"""Support for Subaru selectors."""
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.restore_state import RestoreEntity

from . import DOMAIN as SUBARU_DOMAIN, get_device_info
from .const import (
    ENTRY_COORDINATOR,
    ENTRY_VEHICLES,
    VEHICLE_CLIMATE,
    VEHICLE_CLIMATE_PRESET_NAME,
    VEHICLE_CLIMATE_SELECTED_PRESET,
    VEHICLE_HAS_EV,
    VEHICLE_HAS_REMOTE_START,
    VEHICLE_NAME,
    VEHICLE_VIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Subaru selectors by config_entry."""
    entry = hass.data[SUBARU_DOMAIN][config_entry.entry_id]
    coordinator = entry[ENTRY_COORDINATOR]
    vehicle_info = entry[ENTRY_VEHICLES]
    climate_select = []
    for vin in vehicle_info:
        if (
            vehicle_info[vin][VEHICLE_HAS_REMOTE_START]
            or vehicle_info[vin][VEHICLE_HAS_EV]
        ):
            climate_select.append(
                SubaruClimateSelect(vehicle_info[vin], coordinator, config_entry)
            )
    async_add_entities(climate_select)


class SubaruClimateSelect(SelectEntity, RestoreEntity):
    """Representation of a Subaru climate preset selector entity."""

    def __init__(self, vehicle_info, coordinator, config_entry):
        """Initialize the selector for the vehicle."""
        self.coordinator = coordinator
        self.vin = vehicle_info[VEHICLE_VIN]
        self.car_name = vehicle_info[VEHICLE_NAME]
        self.config_entry = config_entry
        self._attr_current_option = None
        self._attr_name = f"{vehicle_info[VEHICLE_NAME]} Climate Preset"
        self._attr_unique_id = f"{self.vin}_climate_preset"
        self._attr_device_info = get_device_info(vehicle_info)

    @property
    def options(self):
        """Return a set of selectable options."""
        vehicle_data = None
        if self.coordinator.data:
            vehicle_data = self.coordinator.data.get(self.vin)
        if vehicle_data:
            if isinstance(preset_data := vehicle_data.get(VEHICLE_CLIMATE), list):
                return [preset[VEHICLE_CLIMATE_PRESET_NAME] for preset in preset_data]

    async def async_added_to_hass(self):
        """Restore previous state of this selector."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        if state and state.state in self.options:
            self._attr_current_option = state.state
            self.coordinator.data.get(self.vin)[
                VEHICLE_CLIMATE_SELECTED_PRESET
            ] = state.state
            self.async_write_ha_state()

    async def async_select_option(self, option):
        """Change the selected option."""
        _LOGGER.debug("Selecting %s climate preset for %s", option, self.car_name)
        if option in self.options:
            self._attr_current_option = option
            self.coordinator.data.get(self.vin)[
                VEHICLE_CLIMATE_SELECTED_PRESET
            ] = option
            self.async_write_ha_state()
