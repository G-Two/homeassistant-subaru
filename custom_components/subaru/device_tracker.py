"""Support for Subaru device tracker."""
import subarulink.const as sc

from homeassistant.components.device_tracker import SOURCE_TYPE_GPS
from homeassistant.components.device_tracker.config_entry import TrackerEntity

from .const import DOMAIN, ENTRY_COORDINATOR, ENTRY_VEHICLES, VEHICLE_HAS_REMOTE_SERVICE
from .entity import SubaruEntity


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Subaru device tracker by config_entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][ENTRY_COORDINATOR]
    vehicle_info = hass.data[DOMAIN][config_entry.entry_id][ENTRY_VEHICLES]
    entities = []
    for vin in vehicle_info:
        if vehicle_info[vin][VEHICLE_HAS_REMOTE_SERVICE]:
            entities.append(SubaruDeviceTracker(vehicle_info[vin], coordinator))
    async_add_entities(entities, True)


class SubaruDeviceTracker(SubaruEntity, TrackerEntity):
    """Class for Subaru device tracker."""

    def __init__(self, vehicle_info, coordinator):
        """Initialize the device tracker."""
        super().__init__(vehicle_info, coordinator)
        self.hass_type = "device_tracker"
        self.entity_type = "Location"

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SOURCE_TYPE_GPS

    @property
    def latitude(self):
        """Return latitude value of the device."""
        value = None
        if self.coordinator.data.get(self.vin):
            value = self.coordinator.data[self.vin]["status"].get(sc.LATITUDE)
        return value

    @property
    def longitude(self):
        """Return longitude value of the device."""
        value = None
        if self.coordinator.data.get(self.vin):
            value = self.coordinator.data[self.vin]["status"].get(sc.LONGITUDE)
        return value
