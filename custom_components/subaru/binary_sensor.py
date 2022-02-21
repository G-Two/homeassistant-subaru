"""Support for Subaru binary sensors."""
import subarulink.const as sc

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import get_device_info
from .const import (
    API_GEN_2,
    DOMAIN,
    ENTRY_COORDINATOR,
    ENTRY_VEHICLES,
    VEHICLE_API_GEN,
    VEHICLE_HAS_EV,
    VEHICLE_NAME,
    VEHICLE_STATUS,
    VEHICLE_VIN,
)

SENSOR_TYPE = "name"
SENSOR_FIELD = "field"
SENSOR_CLASS = "class"
SENSOR_ON_VALUE = "on_value"

BINARY_SENSOR_ICONS = {
    BinarySensorDeviceClass.POWER: {True: "mdi:engine", False: "mdi:engine-off"},
    BinarySensorDeviceClass.BATTERY_CHARGING: {
        True: "mdi:car-electric",
        False: "mdi:car",
    },
    BinarySensorDeviceClass.DOOR: {True: "mdi:door-open", False: "mdi:door-closed"},
    BinarySensorDeviceClass.PLUG: {True: "mdi:power-plug", False: "mdi:power-plug-off"},
    BinarySensorDeviceClass.WINDOW: {
        True: "mdi:window-open",
        False: "mdi:window-closed",
    },
}


# Binary Sensor data available to "Subaru Safety Plus" subscribers with Gen2 vehicles
API_GEN_2_SENSORS = [
    {
        SENSOR_TYPE: "Ignition",
        SENSOR_FIELD: sc.VEHICLE_STATE,
        SENSOR_CLASS: BinarySensorDeviceClass.POWER,
        SENSOR_ON_VALUE: sc.IGNITION_ON,
    },
    {
        SENSOR_TYPE: "Trunk",
        SENSOR_FIELD: sc.DOOR_BOOT_POSITION,
        SENSOR_CLASS: BinarySensorDeviceClass.DOOR,
        SENSOR_ON_VALUE: sc.DOOR_OPEN,
    },
    {
        SENSOR_TYPE: "Hood",
        SENSOR_FIELD: sc.DOOR_ENGINE_HOOD_POSITION,
        SENSOR_CLASS: BinarySensorDeviceClass.DOOR,
        SENSOR_ON_VALUE: sc.DOOR_OPEN,
    },
    {
        SENSOR_TYPE: "Front Left Door",
        SENSOR_FIELD: sc.DOOR_FRONT_LEFT_POSITION,
        SENSOR_CLASS: BinarySensorDeviceClass.DOOR,
        SENSOR_ON_VALUE: sc.DOOR_OPEN,
    },
    {
        SENSOR_TYPE: "Front Right Door",
        SENSOR_FIELD: sc.DOOR_FRONT_RIGHT_POSITION,
        SENSOR_CLASS: BinarySensorDeviceClass.DOOR,
        SENSOR_ON_VALUE: sc.DOOR_OPEN,
    },
    {
        SENSOR_TYPE: "Rear Left Door",
        SENSOR_FIELD: sc.DOOR_REAR_LEFT_POSITION,
        SENSOR_CLASS: BinarySensorDeviceClass.DOOR,
        SENSOR_ON_VALUE: sc.DOOR_OPEN,
    },
    {
        SENSOR_TYPE: "Rear Right Door",
        SENSOR_FIELD: sc.DOOR_REAR_RIGHT_POSITION,
        SENSOR_CLASS: BinarySensorDeviceClass.DOOR,
        SENSOR_ON_VALUE: sc.DOOR_OPEN,
    },
    {
        SENSOR_TYPE: "Front Left Window",
        SENSOR_FIELD: sc.WINDOW_FRONT_LEFT_STATUS,
        SENSOR_CLASS: BinarySensorDeviceClass.WINDOW,
        SENSOR_ON_VALUE: sc.WINDOW_OPEN,
    },
    {
        SENSOR_TYPE: "Front Right Window",
        SENSOR_FIELD: sc.WINDOW_FRONT_RIGHT_STATUS,
        SENSOR_CLASS: BinarySensorDeviceClass.WINDOW,
        SENSOR_ON_VALUE: sc.WINDOW_OPEN,
    },
    {
        SENSOR_TYPE: "Rear Left Window",
        SENSOR_FIELD: sc.WINDOW_REAR_LEFT_STATUS,
        SENSOR_CLASS: BinarySensorDeviceClass.WINDOW,
        SENSOR_ON_VALUE: sc.WINDOW_OPEN,
    },
    {
        SENSOR_TYPE: "Rear Right Window",
        SENSOR_FIELD: sc.WINDOW_REAR_RIGHT_STATUS,
        SENSOR_CLASS: BinarySensorDeviceClass.WINDOW,
        SENSOR_ON_VALUE: sc.WINDOW_OPEN,
    },
    {
        SENSOR_TYPE: "Sunroof",
        SENSOR_FIELD: sc.WINDOW_SUNROOF_STATUS,
        SENSOR_CLASS: BinarySensorDeviceClass.WINDOW,
        SENSOR_ON_VALUE: sc.WINDOW_OPEN,
    },
]

# Binary Sensor data available to "Subaru Safety Plus" subscribers with PHEV vehicles
EV_SENSORS = [
    {
        SENSOR_TYPE: "EV Charge Port",
        SENSOR_FIELD: sc.EV_IS_PLUGGED_IN,
        SENSOR_CLASS: BinarySensorDeviceClass.PLUG,
        SENSOR_ON_VALUE: [sc.LOCKED_CONNECTED, sc.UNLOCKED_CONNECTED],
    },
    {
        SENSOR_TYPE: "EV Battery Charging",
        SENSOR_FIELD: sc.EV_CHARGER_STATE_TYPE,
        SENSOR_CLASS: BinarySensorDeviceClass.BATTERY_CHARGING,
        SENSOR_ON_VALUE: sc.CHARGING,
    },
]


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Subaru binary sensors by config_entry."""
    entry = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = entry[ENTRY_COORDINATOR]
    vehicle_info = entry[ENTRY_VEHICLES]
    entities = []
    for vin in vehicle_info:
        _create_sensor_entities(entities, vehicle_info[vin], coordinator)
    async_add_entities(entities)


def _create_sensor_entities(entities, vehicle_info, coordinator):
    sensors_to_add = []

    if vehicle_info[VEHICLE_API_GEN] == API_GEN_2:
        sensors_to_add.extend(API_GEN_2_SENSORS)

    if vehicle_info[VEHICLE_HAS_EV]:
        sensors_to_add.extend(EV_SENSORS)

    for subaru_sensor in sensors_to_add:
        if (
            coordinator.data[vehicle_info[VEHICLE_VIN]]["status"].get(
                subaru_sensor[SENSOR_FIELD]
            )
            not in sc.BAD_BINARY_SENSOR_VALUES
        ):
            entities.append(
                SubaruBinarySensor(
                    vehicle_info,
                    coordinator,
                    subaru_sensor[SENSOR_TYPE],
                    subaru_sensor[SENSOR_FIELD],
                    subaru_sensor[SENSOR_CLASS],
                    subaru_sensor[SENSOR_ON_VALUE],
                )
            )


class SubaruBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Class for Subaru binary sensors."""

    def __init__(
        self, vehicle_info, coordinator, entity_type, data_field, device_class, on_value
    ):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.vin = vehicle_info[VEHICLE_VIN]
        self._attr_device_class = device_class
        self._attr_device_info = get_device_info(vehicle_info)
        self._attr_name = f"{vehicle_info[VEHICLE_NAME]} {entity_type}"
        self._attr_unique_id = f"{self.vin}_{entity_type}"
        self._attr_should_poll = False
        self.data_field = data_field
        self.on_value = on_value

    @property
    def icon(self):
        """Return icon for sensor."""
        return BINARY_SENSOR_ICONS[self._attr_device_class][self.is_on]

    @property
    def available(self):
        """Return if entity is available."""
        last_update_success = super().available
        if last_update_success and self.vin not in self.coordinator.data:
            return False
        if self.get_current_value() is None:
            return False
        return last_update_success

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        if isinstance(self.on_value, list):
            return self.get_current_value() in self.on_value
        return self.get_current_value() == self.on_value

    def get_current_value(self):
        """Get raw value from the coordinator."""
        if isinstance(data := self.coordinator.data, dict):
            if data.get(self.vin):
                return data[self.vin][VEHICLE_STATUS].get(self.data_field)
            return None
