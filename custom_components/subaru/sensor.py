"""Support for Subaru sensors."""
from datetime import datetime

import subarulink.const as sc

from custom_components.subaru import get_device_info
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import (
    ELECTRIC_POTENTIAL_VOLT,
    LENGTH_KILOMETERS,
    LENGTH_MILES,
    PERCENTAGE,
    PRESSURE_HPA,
    PRESSURE_PSI,
    TEMP_CELSIUS,
    VOLUME_GALLONS,
    VOLUME_LITERS,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.distance import convert as dist_convert
from homeassistant.util.unit_system import IMPERIAL_SYSTEM, LENGTH_UNITS, PRESSURE_UNITS
from homeassistant.util.volume import convert as vol_convert

from .const import (
    API_GEN_2,
    DOMAIN,
    ENTRY_COORDINATOR,
    ENTRY_VEHICLES,
    ICONS,
    VEHICLE_API_GEN,
    VEHICLE_HAS_EV,
    VEHICLE_HAS_SAFETY_SERVICE,
    VEHICLE_NAME,
    VEHICLE_STATUS,
    VEHICLE_VIN,
)

L_PER_GAL = vol_convert(1, VOLUME_GALLONS, VOLUME_LITERS)
KM_PER_MI = dist_convert(1, LENGTH_MILES, LENGTH_KILOMETERS)

# Fuel Economy Constants
FUEL_CONSUMPTION_L_PER_100KM = "L/100km"
FUEL_CONSUMPTION_MPG = "mi/gal"
FUEL_CONSUMPTION_UNITS = [FUEL_CONSUMPTION_L_PER_100KM, FUEL_CONSUMPTION_MPG]

SENSOR_TYPE = "type"
SENSOR_CLASS = "class"
SENSOR_FIELD = "field"
SENSOR_UNITS = "units"

# Sensor data available to "Subaru Safety Plus" subscribers with Gen1/Gen2 vehicles
SAFETY_SENSORS = [
    {
        # Note: For Gen1, this value is only updated every 500 miles.
        # There is no known manual update method.
        SENSOR_TYPE: "Odometer",
        SENSOR_CLASS: None,
        SENSOR_FIELD: sc.ODOMETER,
        SENSOR_UNITS: LENGTH_KILOMETERS,
    },
]

# Sensor data available to "Subaru Safety Plus" subscribers with Gen2 vehicles
API_GEN_2_SENSORS = [
    {
        SENSOR_TYPE: "Avg Fuel Consumption",
        SENSOR_CLASS: None,
        SENSOR_FIELD: sc.AVG_FUEL_CONSUMPTION,
        SENSOR_UNITS: FUEL_CONSUMPTION_L_PER_100KM,
    },
    {
        SENSOR_TYPE: "Range",
        SENSOR_CLASS: None,
        SENSOR_FIELD: sc.DIST_TO_EMPTY,
        SENSOR_UNITS: LENGTH_KILOMETERS,
    },
    {
        SENSOR_TYPE: "External Temp",
        SENSOR_CLASS: SensorDeviceClass.TEMPERATURE,
        SENSOR_FIELD: sc.EXTERNAL_TEMP,
        SENSOR_UNITS: TEMP_CELSIUS,
    },
    {
        SENSOR_TYPE: "12V Battery Voltage",
        SENSOR_CLASS: SensorDeviceClass.VOLTAGE,
        SENSOR_FIELD: sc.BATTERY_VOLTAGE,
        SENSOR_UNITS: ELECTRIC_POTENTIAL_VOLT,
    },
    {
        SENSOR_TYPE: "Tire Pressure FL",
        SENSOR_CLASS: SensorDeviceClass.PRESSURE,
        SENSOR_FIELD: sc.TIRE_PRESSURE_FL,
        SENSOR_UNITS: PRESSURE_HPA,
    },
    {
        SENSOR_TYPE: "Tire Pressure FR",
        SENSOR_CLASS: SensorDeviceClass.PRESSURE,
        SENSOR_FIELD: sc.TIRE_PRESSURE_FR,
        SENSOR_UNITS: PRESSURE_HPA,
    },
    {
        SENSOR_TYPE: "Tire Pressure RL",
        SENSOR_CLASS: SensorDeviceClass.PRESSURE,
        SENSOR_FIELD: sc.TIRE_PRESSURE_RL,
        SENSOR_UNITS: PRESSURE_HPA,
    },
    {
        SENSOR_TYPE: "Tire Pressure RR",
        SENSOR_CLASS: SensorDeviceClass.PRESSURE,
        SENSOR_FIELD: sc.TIRE_PRESSURE_RR,
        SENSOR_UNITS: PRESSURE_HPA,
    },
]

# Sensor data available to "Subaru Safety Plus" subscribers with PHEV vehicles
EV_SENSORS = [
    {
        SENSOR_TYPE: "EV Range",
        SENSOR_CLASS: None,
        SENSOR_FIELD: sc.EV_DISTANCE_TO_EMPTY,
        SENSOR_UNITS: LENGTH_MILES,
    },
    {
        SENSOR_TYPE: "EV Battery Level",
        SENSOR_CLASS: SensorDeviceClass.BATTERY,
        SENSOR_FIELD: sc.EV_STATE_OF_CHARGE_PERCENT,
        SENSOR_UNITS: PERCENTAGE,
    },
    {
        SENSOR_TYPE: "EV Time to Full Charge",
        SENSOR_CLASS: SensorDeviceClass.TIMESTAMP,
        SENSOR_FIELD: sc.EV_TIME_TO_FULLY_CHARGED_UTC,
        SENSOR_UNITS: None,
    },
]


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Subaru sensors by config_entry."""
    entry_id = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = entry_id[ENTRY_COORDINATOR]
    vehicle_info = entry_id[ENTRY_VEHICLES]
    entities = []
    for vin in vehicle_info:
        entities.extend(create_vehicle_sensors(vehicle_info[vin], coordinator))
    async_add_entities(entities, True)


def create_vehicle_sensors(vehicle_info, coordinator):
    """Instantiate all available sensors for the vehicle."""
    sensors_to_add = []
    if vehicle_info[VEHICLE_HAS_SAFETY_SERVICE]:
        sensors_to_add.extend(SAFETY_SENSORS)

        if vehicle_info[VEHICLE_API_GEN] == API_GEN_2:
            sensors_to_add.extend(API_GEN_2_SENSORS)

        if vehicle_info[VEHICLE_HAS_EV]:
            sensors_to_add.extend(EV_SENSORS)

    return [
        SubaruSensor(
            vehicle_info,
            coordinator,
            s[SENSOR_TYPE],
            s[SENSOR_CLASS],
            s[SENSOR_FIELD],
            s[SENSOR_UNITS],
        )
        for s in sensors_to_add
    ]


class SubaruSensor(CoordinatorEntity, SensorEntity):
    """Class for Subaru sensors."""

    def __init__(
        self,
        vehicle_info,
        coordinator,
        entity_type,
        device_class,
        data_field,
        native_unit,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.vin = vehicle_info[VEHICLE_VIN]
        self.entity_type = entity_type
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = native_unit
        self._attr_name = f"{vehicle_info[VEHICLE_NAME]} {self.entity_type}"
        self._attr_unique_id = f"{self.vin}_{self.entity_type}"
        self._attr_should_poll = False
        self._attr_device_info = get_device_info(vehicle_info)
        self.data_field = data_field

    @property
    def icon(self):
        """Return the icon of the sensor."""
        if not self._attr_device_class:
            return ICONS.get(self.entity_type)
        return None

    @property
    def state(self):
        """Return the state of the sensor."""
        value = self.native_value
        units = self.hass.config.units

        if value is None:
            return None

        if self.unit_of_measurement in PRESSURE_UNITS and units == IMPERIAL_SYSTEM:
            return round(units.pressure(value, self.native_unit_of_measurement), 1,)

        if self.unit_of_measurement in LENGTH_UNITS:
            return round(units.length(value, self.native_unit_of_measurement), 1,)

        if (
            self.unit_of_measurement in FUEL_CONSUMPTION_UNITS
            and units == IMPERIAL_SYSTEM
        ):
            return round((100.0 * L_PER_GAL) / (KM_PER_MI * value), 1)

        if self._attr_device_class == SensorDeviceClass.TIMESTAMP and isinstance(
            value, datetime
        ):
            return value.isoformat(timespec="seconds")

        return value

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of the entity, after unit conversion."""
        if (
            self._attr_device_class == SensorDeviceClass.PRESSURE
            and self.hass.config.units == IMPERIAL_SYSTEM
        ):
            return PRESSURE_PSI

        if self.native_unit_of_measurement in FUEL_CONSUMPTION_UNITS:
            if self.hass.config.units == IMPERIAL_SYSTEM:
                return FUEL_CONSUMPTION_MPG
            return FUEL_CONSUMPTION_L_PER_100KM

        if (
            self.native_unit_of_measurement in LENGTH_UNITS
            and self.hass.config.units == IMPERIAL_SYSTEM
        ):
            return LENGTH_MILES

        return self.native_unit_of_measurement

    @property
    def available(self):
        """Return if entity is available."""
        last_update_success = super().available
        if last_update_success and self.vin not in self.coordinator.data:
            return False
        if self.state is None:
            return False
        return last_update_success

    @property
    def native_value(self):
        """Get raw value from the coordinator."""
        if isinstance(data := self.coordinator.data, dict):
            value = data.get(self.vin)[VEHICLE_STATUS].get(self.data_field)
            if value in sc.BAD_SENSOR_VALUES:
                value = None
            if isinstance(value, str):
                if "." in value:
                    value = float(value)
                elif value.isdigit():
                    value = int(value)
            return value
