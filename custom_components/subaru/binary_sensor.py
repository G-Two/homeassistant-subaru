"""Support for Subaru binary sensors."""
from __future__ import annotations

from typing import Any

import subarulink.const as sc

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    API_GEN_2,
    DOMAIN,
    ENTRY_COORDINATOR,
    ENTRY_VEHICLES,
    VEHICLE_API_GEN,
    VEHICLE_HAS_EV,
    VEHICLE_STATUS,
    VEHICLE_VIN,
)
from .device import get_device_info

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

ON_VALUES = {
    BinarySensorDeviceClass.DOOR: [sc.DOOR_OPEN],
    BinarySensorDeviceClass.POWER: [sc.IGNITION_ON],
    BinarySensorDeviceClass.WINDOW: [sc.WINDOW_OPEN],
    BinarySensorDeviceClass.PLUG: [sc.LOCKED_CONNECTED, sc.UNLOCKED_CONNECTED],
    BinarySensorDeviceClass.BATTERY_CHARGING: [sc.CHARGING],
}

# Binary Sensors available to "Subaru Safety Plus" subscribers with Gen2 vehicles
API_GEN_2_BINARY_SENSORS = [
    BinarySensorEntityDescription(
        name="Ignition",
        key=sc.VEHICLE_STATE,
        device_class=BinarySensorDeviceClass.POWER,
    ),
    BinarySensorEntityDescription(
        name="Trunk",
        key=sc.DOOR_BOOT_POSITION,
        device_class=BinarySensorDeviceClass.DOOR,
    ),
    BinarySensorEntityDescription(
        name="Hood",
        key=sc.DOOR_ENGINE_HOOD_POSITION,
        device_class=BinarySensorDeviceClass.DOOR,
    ),
    BinarySensorEntityDescription(
        name="Front left door",
        key=sc.DOOR_FRONT_LEFT_POSITION,
        device_class=BinarySensorDeviceClass.DOOR,
    ),
    BinarySensorEntityDescription(
        name="Front right door",
        key=sc.DOOR_FRONT_RIGHT_POSITION,
        device_class=BinarySensorDeviceClass.DOOR,
    ),
    BinarySensorEntityDescription(
        name="Rear left door",
        key=sc.DOOR_REAR_LEFT_POSITION,
        device_class=BinarySensorDeviceClass.DOOR,
    ),
    BinarySensorEntityDescription(
        name="Rear right door",
        key=sc.DOOR_REAR_RIGHT_POSITION,
        device_class=BinarySensorDeviceClass.DOOR,
    ),
    BinarySensorEntityDescription(
        name="Front left window",
        key=sc.WINDOW_FRONT_LEFT_STATUS,
        device_class=BinarySensorDeviceClass.WINDOW,
    ),
    BinarySensorEntityDescription(
        name="Front right window",
        key=sc.WINDOW_FRONT_RIGHT_STATUS,
        device_class=BinarySensorDeviceClass.WINDOW,
    ),
    BinarySensorEntityDescription(
        name="Rear left window",
        key=sc.WINDOW_REAR_LEFT_STATUS,
        device_class=BinarySensorDeviceClass.WINDOW,
    ),
    BinarySensorEntityDescription(
        name="Rear right window",
        key=sc.WINDOW_REAR_RIGHT_STATUS,
        device_class=BinarySensorDeviceClass.WINDOW,
    ),
    BinarySensorEntityDescription(
        name="Sunroof",
        key=sc.WINDOW_SUNROOF_STATUS,
        device_class=BinarySensorDeviceClass.WINDOW,
    ),
]

# Binary Sensors available to "Subaru Safety Plus" subscribers with PHEV vehicles
EV_BINARY_SENSORS = [
    BinarySensorEntityDescription(
        name="EV charge port",
        key=sc.EV_IS_PLUGGED_IN,
        device_class=BinarySensorDeviceClass.PLUG,
    ),
    BinarySensorEntityDescription(
        name="EV battery charging",
        key=sc.EV_CHARGER_STATE_TYPE,
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Subaru binary sensors by config_entry."""
    entry = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = entry[ENTRY_COORDINATOR]
    vehicle_info = entry[ENTRY_VEHICLES]
    entities = []
    for info in vehicle_info.values():
        entities.extend(create_vehicle_binary_sensors(info, coordinator))
    async_add_entities(entities)


def create_vehicle_binary_sensors(
    vehicle_info: dict, coordinator: DataUpdateCoordinator
) -> list[SubaruBinarySensor]:
    """Instantiate all available binary sensors for the vehicle."""
    potential_sensors = []

    if vehicle_info[VEHICLE_API_GEN] == API_GEN_2:
        potential_sensors.extend(API_GEN_2_BINARY_SENSORS)

    if vehicle_info[VEHICLE_HAS_EV]:
        potential_sensors.extend(EV_BINARY_SENSORS)

    binary_sensors_to_add = []
    for sensor in potential_sensors:
        if (
            coordinator.data[vehicle_info[VEHICLE_VIN]][VEHICLE_STATUS].get(sensor.key)
            not in sc.BAD_BINARY_SENSOR_VALUES
        ):
            binary_sensors_to_add.append(sensor)

    return [
        SubaruBinarySensor(vehicle_info, coordinator, description)
        for description in binary_sensors_to_add
    ]


class SubaruBinarySensor(
    CoordinatorEntity[DataUpdateCoordinator[dict[str, Any]]], BinarySensorEntity
):
    """Class for Subaru binary sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        vehicle_info: dict,
        coordinator: DataUpdateCoordinator,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.vin = vehicle_info[VEHICLE_VIN]
        self.entity_description = description
        self._attr_device_info = get_device_info(vehicle_info)
        self._attr_unique_id = f"{self.vin}_{description.key}"

    @property
    def icon(self) -> str:
        """Return icon for sensor."""
        return BINARY_SENSOR_ICONS[self.device_class][self.is_on]

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        last_update_success = super().available
        if last_update_success and self.vin not in self.coordinator.data:
            return False
        if self.get_current_value() is None:
            return False
        return last_update_success

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.get_current_value() in ON_VALUES[self.device_class]

    def get_current_value(self) -> str | None:
        """Get raw value from the coordinator."""
        value = None
        if data := self.coordinator.data.get(self.vin):
            value = data[VEHICLE_STATUS].get(self.entity_description.key)
        return value
