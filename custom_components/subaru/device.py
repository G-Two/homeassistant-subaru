"""Common device information for a vehicle."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo

from .const import (
    DOMAIN,
    MANUFACTURER,
    VEHICLE_MODEL_NAME,
    VEHICLE_MODEL_YEAR,
    VEHICLE_NAME,
    VEHICLE_VIN,
)


def get_device_info(vehicle_info: dict) -> DeviceInfo:
    """Return DeviceInfo object based on vehicle info."""
    return DeviceInfo(
        identifiers={(DOMAIN, vehicle_info[VEHICLE_VIN])},
        manufacturer=MANUFACTURER,
        model=f"{vehicle_info[VEHICLE_MODEL_YEAR]} {vehicle_info[VEHICLE_MODEL_NAME]}",
        name=vehicle_info[VEHICLE_NAME],
    )
