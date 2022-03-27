"""Support for Subaru device tracker."""
import subarulink.const as sc

from homeassistant.components.device_tracker import SOURCE_TYPE_GPS
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import get_device_info
from .const import (
    DOMAIN,
    ENTRY_COORDINATOR,
    ENTRY_VEHICLES,
    VEHICLE_HAS_REMOTE_SERVICE,
    VEHICLE_NAME,
    VEHICLE_STATUS,
    VEHICLE_VIN,
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Subaru device tracker by config_entry."""
    entry = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = entry[ENTRY_COORDINATOR]
    vehicle_info = entry[ENTRY_VEHICLES]
    entities = []
    for vin in vehicle_info:
        if vehicle_info[vin][VEHICLE_HAS_REMOTE_SERVICE]:
            entities.append(SubaruDeviceTracker(vehicle_info[vin], coordinator))
    async_add_entities(entities)


class SubaruDeviceTracker(CoordinatorEntity, TrackerEntity):
    """Class for Subaru device tracker."""

    def __init__(self, vehicle_info, coordinator):
        """Initialize the device tracker."""
        super().__init__(coordinator)
        self.vin = vehicle_info[VEHICLE_VIN]
        self._attr_name = f"{vehicle_info[VEHICLE_NAME]} Location"
        self._attr_unique_id = f"{self.vin}_location"
        self._attr_should_poll = False
        self._attr_device_info = get_device_info(vehicle_info)

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SOURCE_TYPE_GPS

    @property
    def latitude(self):
        """Return latitude value of the device."""
        value = None
        if isinstance(data := self.coordinator.data.get(self.vin), dict):
            value = data[VEHICLE_STATUS].get(sc.LATITUDE)
        return value

    @property
    def longitude(self):
        """Return longitude value of the device."""
        value = None
        if isinstance(data := self.coordinator.data.get(self.vin), dict):
            value = data[VEHICLE_STATUS].get(sc.LONGITUDE)
        return value
