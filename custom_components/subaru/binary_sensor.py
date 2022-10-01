"""Support for Subaru binary sensors."""
from dataclasses import dataclass
from typing import List

import subarulink.const as sc

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
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


@dataclass
class SubaruBinarySensorFieldsMixin:
    """Additional fields needed for Subaru binary sensors."""

    suffix: str
    on_values: List


@dataclass
class SubaruBinarySensorEntityDescription(
    BinarySensorEntityDescription, SubaruBinarySensorFieldsMixin
):
    """Describes Subaru binary sensor entity."""


# Binary Sensors available to "Subaru Safety Plus" subscribers with Gen2 vehicles
API_GEN_2_SENSORS = [
    SubaruBinarySensorEntityDescription(
        suffix="Ignition",
        key=sc.VEHICLE_STATE,
        device_class=BinarySensorDeviceClass.POWER,
        on_values=[sc.IGNITION_ON],
    ),
    SubaruBinarySensorEntityDescription(
        suffix="Trunk",
        key=sc.DOOR_BOOT_POSITION,
        device_class=BinarySensorDeviceClass.DOOR,
        on_values=[sc.DOOR_OPEN],
    ),
    SubaruBinarySensorEntityDescription(
        suffix="Hood",
        key=sc.DOOR_ENGINE_HOOD_POSITION,
        device_class=BinarySensorDeviceClass.DOOR,
        on_values=[sc.DOOR_OPEN],
    ),
    SubaruBinarySensorEntityDescription(
        suffix="Front Left Door",
        key=sc.DOOR_FRONT_LEFT_POSITION,
        device_class=BinarySensorDeviceClass.DOOR,
        on_values=[sc.DOOR_OPEN],
    ),
    SubaruBinarySensorEntityDescription(
        suffix="Front Right Door",
        key=sc.DOOR_FRONT_RIGHT_POSITION,
        device_class=BinarySensorDeviceClass.DOOR,
        on_values=[sc.DOOR_OPEN],
    ),
    SubaruBinarySensorEntityDescription(
        suffix="Rear Left Door",
        key=sc.DOOR_REAR_LEFT_POSITION,
        device_class=BinarySensorDeviceClass.DOOR,
        on_values=[sc.DOOR_OPEN],
    ),
    SubaruBinarySensorEntityDescription(
        suffix="Rear Right Door",
        key=sc.DOOR_REAR_RIGHT_POSITION,
        device_class=BinarySensorDeviceClass.DOOR,
        on_values=[sc.DOOR_OPEN],
    ),
    SubaruBinarySensorEntityDescription(
        suffix="Front Left Window",
        key=sc.WINDOW_FRONT_LEFT_STATUS,
        device_class=BinarySensorDeviceClass.WINDOW,
        on_values=[sc.WINDOW_OPEN],
    ),
    SubaruBinarySensorEntityDescription(
        suffix="Front Right Window",
        key=sc.WINDOW_FRONT_RIGHT_STATUS,
        device_class=BinarySensorDeviceClass.WINDOW,
        on_values=[sc.WINDOW_OPEN],
    ),
    SubaruBinarySensorEntityDescription(
        suffix="Rear Left Window",
        key=sc.WINDOW_REAR_LEFT_STATUS,
        device_class=BinarySensorDeviceClass.WINDOW,
        on_values=[sc.WINDOW_OPEN],
    ),
    SubaruBinarySensorEntityDescription(
        suffix="Rear Right Window",
        key=sc.WINDOW_REAR_RIGHT_STATUS,
        device_class=BinarySensorDeviceClass.WINDOW,
        on_values=[sc.WINDOW_OPEN],
    ),
    SubaruBinarySensorEntityDescription(
        suffix="Sunroof",
        key=sc.WINDOW_SUNROOF_STATUS,
        device_class=BinarySensorDeviceClass.WINDOW,
        on_values=[sc.WINDOW_OPEN],
    ),
]

# Binary Sensors available to "Subaru Safety Plus" subscribers with PHEV vehicles
EV_SENSORS = [
    SubaruBinarySensorEntityDescription(
        suffix="EV Charge Port",
        key=sc.EV_IS_PLUGGED_IN,
        device_class=BinarySensorDeviceClass.PLUG,
        on_values=[sc.LOCKED_CONNECTED, sc.UNLOCKED_CONNECTED],
    ),
    SubaruBinarySensorEntityDescription(
        suffix="EV Battery Charging",
        key=sc.EV_CHARGER_STATE_TYPE,
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        on_values=[sc.CHARGING],
    ),
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

    for sensor_description in sensors_to_add:
        if (
            coordinator.data[vehicle_info[VEHICLE_VIN]][VEHICLE_STATUS].get(
                sensor_description.key
            )
            not in sc.BAD_BINARY_SENSOR_VALUES
        ):
            entities.append(
                SubaruBinarySensor(
                    vehicle_info,
                    coordinator,
                    sensor_description,
                )
            )


class SubaruBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Class for Subaru binary sensors."""

    entity_description: SubaruBinarySensorEntityDescription

    def __init__(self, vehicle_info, coordinator, description):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.vin = vehicle_info[VEHICLE_VIN]
        self.entity_description = description
        self._attr_device_info = get_device_info(vehicle_info)
        self._attr_name = f"{vehicle_info[VEHICLE_NAME]} {description.suffix}"
        self._attr_unique_id = f"{self.vin}_{description.suffix}"

    @property
    def icon(self):
        """Return icon for sensor."""
        return BINARY_SENSOR_ICONS[self.device_class][self.is_on]

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
        return self.get_current_value() in self.entity_description.on_values

    def get_current_value(self):
        """Get raw value from the coordinator."""
        if isinstance(data := self.coordinator.data, dict):
            if data.get(self.vin):
                return data[self.vin][VEHICLE_STATUS].get(self.entity_description.key)
            return None
