"""Support for Subaru selectors."""
import logging

from homeassistant.components.select import DOMAIN as SELECT_DOMAIN, SelectEntity
from homeassistant.helpers.restore_state import RestoreEntity

from . import DOMAIN as SUBARU_DOMAIN
from .const import (
    ENTRY_COORDINATOR,
    ENTRY_VEHICLES,
    VEHICLE_CLIMATE,
    VEHICLE_CLIMATE_SELECTED_PRESET,
    VEHICLE_HAS_EV,
    VEHICLE_HAS_REMOTE_START,
)
from .entity import SubaruEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Subaru selectors by config_entry."""
    coordinator = hass.data[SUBARU_DOMAIN][config_entry.entry_id][ENTRY_COORDINATOR]
    vehicle_info = hass.data[SUBARU_DOMAIN][config_entry.entry_id][ENTRY_VEHICLES]
    climate_select = []
    for vin in vehicle_info:
        if (
            vehicle_info[vin][VEHICLE_HAS_REMOTE_START]
            or vehicle_info[vin][VEHICLE_HAS_EV]
        ):
            climate_select.append(
                SubaruClimateSelect(
                    "Climate Preset", vehicle_info[vin], coordinator, config_entry
                )
            )
    async_add_entities(climate_select, True)


class SubaruClimateSelect(SubaruEntity, SelectEntity, RestoreEntity):
    """Representation of a Subaru climate preset selector entity."""

    def __init__(self, type, vehicle_info, coordinator, config_entry):
        """Initialize the selector for the vehicle."""
        super().__init__(vehicle_info, coordinator)
        self.entity_type = type
        self.hass_type = SELECT_DOMAIN
        self.config_entry = config_entry
        self._attr_current_option = None

    @property
    def options(self):
        """Return a set of selectable options."""
        vehicle_data = self.coordinator.data.get(self.vin)
        if vehicle_data:
            preset_data = vehicle_data.get(VEHICLE_CLIMATE)
            if isinstance(preset_data, list):
                return [preset["name"] for preset in preset_data]

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
