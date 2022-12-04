"""Support for Subaru buttons."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_NOTIFICATION_OPTION,
    DOMAIN as SUBARU_DOMAIN,
    ENTRY_CONTROLLER,
    ENTRY_COORDINATOR,
    ENTRY_VEHICLES,
    REMOTE_SERVICE_CHARGE_START,
    REMOTE_SERVICE_HORN,
    REMOTE_SERVICE_HORN_STOP,
    REMOTE_SERVICE_LIGHTS,
    REMOTE_SERVICE_LIGHTS_STOP,
    REMOTE_SERVICE_POLL_VEHICLE,
    REMOTE_SERVICE_REFRESH,
    REMOTE_SERVICE_REMOTE_START,
    REMOTE_SERVICE_REMOTE_STOP,
    VEHICLE_CLIMATE_SELECTED_PRESET,
    VEHICLE_HAS_EV,
    VEHICLE_HAS_REMOTE_SERVICE,
    VEHICLE_HAS_REMOTE_START,
    VEHICLE_VIN,
)
from .device import get_device_info
from .remote_service import async_call_remote_service

_LOGGER = logging.getLogger(__name__)

G1_REMOTE_BUTTONS = [
    ButtonEntityDescription(
        key=REMOTE_SERVICE_HORN, icon="mdi:volume-high", name="Horn start"
    ),
    ButtonEntityDescription(
        key=REMOTE_SERVICE_HORN_STOP, icon="mdi:volume-off", name="Horn stop"
    ),
    ButtonEntityDescription(
        key=REMOTE_SERVICE_LIGHTS, icon="mdi:lightbulb-on", name="Lights start"
    ),
    ButtonEntityDescription(
        key=REMOTE_SERVICE_LIGHTS_STOP, icon="mdi:lightbulb-off", name="Lights stop"
    ),
    ButtonEntityDescription(
        key=REMOTE_SERVICE_POLL_VEHICLE, icon="mdi:car-connected", name="Poll Vehicle"
    ),
    ButtonEntityDescription(
        key=REMOTE_SERVICE_REFRESH, icon="mdi:refresh", name="Refresh"
    ),
]

RES_REMOTE_BUTTONS = [
    ButtonEntityDescription(
        key=REMOTE_SERVICE_REMOTE_START, icon="mdi:power", name="Remote start"
    ),
    ButtonEntityDescription(
        key=REMOTE_SERVICE_REMOTE_STOP,
        icon="mdi:stop-circle-outline",
        name="Remote Stop",
    ),
]

EV_REMOTE_BUTTONS = [
    ButtonEntityDescription(
        key=REMOTE_SERVICE_CHARGE_START, icon="mdi:ev-station", name="Charge EV"
    )
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Subaru buttons by config_entry."""
    entry = hass.data[SUBARU_DOMAIN][config_entry.entry_id]
    coordinator = entry[ENTRY_COORDINATOR]
    vehicle_info = entry[ENTRY_VEHICLES]
    entities = []
    for info in vehicle_info.values():
        entities.extend(create_vehicle_buttons(info, coordinator, config_entry))
    async_add_entities(entities)


def create_vehicle_buttons(
    vehicle_info: dict, coordinator: DataUpdateCoordinator, config_entry: ConfigEntry
) -> list[SubaruButton]:
    """Instantiate all available buttons for the vehicle."""
    buttons_to_add = []
    if vehicle_info[VEHICLE_HAS_REMOTE_SERVICE]:
        buttons_to_add.extend(G1_REMOTE_BUTTONS)

        if vehicle_info[VEHICLE_HAS_REMOTE_START] or vehicle_info[VEHICLE_HAS_EV]:
            buttons_to_add.extend(RES_REMOTE_BUTTONS)

        if vehicle_info[VEHICLE_HAS_EV]:
            buttons_to_add.extend(EV_REMOTE_BUTTONS)

    return [
        SubaruButton(vehicle_info, config_entry, coordinator, description)
        for description in buttons_to_add
    ]


class SubaruButton(ButtonEntity):
    """Class for a Subaru buttons."""

    _attr_has_entity_name = True

    def __init__(
        self,
        vehicle_info: dict,
        config_entry: ConfigEntry,
        coordinator: DataUpdateCoordinator,
        description: ButtonEntityDescription,
    ) -> None:
        """Initialize the button for the vehicle."""
        self.vin = vehicle_info[VEHICLE_VIN]
        self.vehicle_info = vehicle_info
        self.entity_description = description
        self.config_entry = config_entry
        self.arg = None
        self.coordinator = coordinator
        self._attr_device_info = get_device_info(vehicle_info)
        self._attr_unique_id = f"{self.vin}_{description.key}"

    async def async_press(self) -> None:
        """Press the button."""
        _LOGGER.info("%s button pressed", self.name)
        arg = None
        if self.entity_description.key == REMOTE_SERVICE_REMOTE_START:
            arg = self.coordinator.data.get(self.vin).get(
                VEHICLE_CLIMATE_SELECTED_PRESET
            )
        controller = self.hass.data[SUBARU_DOMAIN][self.config_entry.entry_id][
            ENTRY_CONTROLLER
        ]
        await async_call_remote_service(
            self.hass,
            controller,
            self.entity_description.key,
            self.vehicle_info,
            arg,
            self.config_entry.options.get(CONF_NOTIFICATION_OPTION),
        )
        await self.coordinator.async_refresh()
