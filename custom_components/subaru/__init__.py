"""The Subaru integration."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
import pprint

from subarulink import Controller as SubaruAPI, InvalidCredentials, SubaruException
from subarulink.const import COUNTRY_USA

from homeassistant.components.binary_sensor import (
    DOMAIN as BINARY_SENSOR_DOMAIN,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_PASSWORD,
    CONF_PIN,
    CONF_USERNAME,
    STATE_ON,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import aiohttp_client, entity_registry as er
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_COUNTRY,
    CONF_POLLING_OPTION,
    COORDINATOR_NAME,
    DOMAIN,
    ENTRY_CONTROLLER,
    ENTRY_COORDINATOR,
    ENTRY_VEHICLES,
    FETCH_INTERVAL,
    SUPPORTED_PLATFORMS,
    UPDATE_INTERVAL,
    UPDATE_INTERVAL_CHARGING,
    VEHICLE_API_GEN,
    VEHICLE_HAS_EV,
    VEHICLE_HAS_REMOTE_SERVICE,
    VEHICLE_HAS_REMOTE_START,
    VEHICLE_HAS_SAFETY_SERVICE,
    VEHICLE_LAST_FETCH,
    VEHICLE_LAST_UPDATE,
    VEHICLE_MODEL_NAME,
    VEHICLE_MODEL_YEAR,
    VEHICLE_NAME,
    VEHICLE_VIN,
)
from .migrate import async_migrate_entries
from .options import PollingOptions
from .remote_service import poll_subaru, refresh_subaru

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, base_config: ConfigType) -> bool:
    """Do nothing since this integration does not support configuration.yml setup."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Subaru from a config entry."""
    config = entry.data
    websession = aiohttp_client.async_create_clientsession(hass)

    # Backwards compatibility for configs made before v0.3.0
    country = config.get(CONF_COUNTRY)
    if not country:
        country = COUNTRY_USA

    try:
        controller = SubaruAPI(
            websession,
            config[CONF_USERNAME],
            config[CONF_PASSWORD],
            config[CONF_DEVICE_ID],
            config[CONF_PIN],
            None,
            country=country,
            update_interval=UPDATE_INTERVAL,
            fetch_interval=FETCH_INTERVAL,
        )
        _LOGGER.debug("Using subarulink %s", controller.version)
        await controller.connect()
    except InvalidCredentials:
        _LOGGER.error("Invalid account")
        return False
    except SubaruException as err:
        raise ConfigEntryNotReady(err) from err

    vehicles = {}
    for vin in controller.get_vehicles():
        vehicles[vin] = _get_vehicle_info(controller, vin)

    async def async_update_data() -> dict:
        """Fetch data from API endpoint."""
        try:
            return await _refresh_subaru_data(hass, entry, vehicles, controller)
        except SubaruException as err:
            raise UpdateFailed(err.message) from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=COORDINATOR_NAME,
        update_method=async_update_data,
        update_interval=timedelta(seconds=FETCH_INTERVAL),
    )

    await coordinator.async_refresh()

    hass.data.get(DOMAIN)[entry.entry_id] = {
        ENTRY_CONTROLLER: controller,
        ENTRY_COORDINATOR: coordinator,
        ENTRY_VEHICLES: vehicles,
    }

    await async_migrate_entries(hass, entry)

    for component in SUPPORTED_PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in SUPPORTED_PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def _refresh_subaru_data(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    vehicle_info: dict,
    controller: SubaruAPI,
) -> dict:
    """
    Refresh local data with data fetched via Subaru API.

    Subaru API calls assume a server side vehicle context
    Data fetch/update must be done for each vehicle
    """
    data = {}

    for vehicle in vehicle_info.values():
        vin = vehicle[VEHICLE_VIN]

        # Active subscription required
        if not vehicle[VEHICLE_HAS_SAFETY_SERVICE]:
            continue

        # Poll vehicle, if option is enabled
        polling_option = PollingOptions.get_by_value(
            config_entry.options.get(CONF_POLLING_OPTION, PollingOptions.DISABLE.value)
        )
        if polling_option == PollingOptions.CHARGING:
            # Is there a better way to check if the subaru is charging?
            e_registry = er.async_get(hass)
            battery_charging = e_registry.async_get_device_class_lookup(
                {(Platform.BINARY_SENSOR, BinarySensorDeviceClass.BATTERY_CHARGING)}
            )
            for item in battery_charging.values():
                entity_id = item[
                    (BINARY_SENSOR_DOMAIN, BinarySensorDeviceClass.BATTERY_CHARGING)
                ]
                entity = e_registry.async_get(entity_id)
                state = hass.states.get(entity_id)
                if entity and state:
                    if entity.platform == DOMAIN and state.state == STATE_ON:
                        await poll_subaru(
                            vehicle,
                            controller,
                            update_interval=UPDATE_INTERVAL_CHARGING,
                        )
        elif polling_option == PollingOptions.ENABLE:
            await poll_subaru(vehicle, controller)

        # Fetch data from Subaru servers
        await refresh_subaru(vehicle, controller)

        # Update our local data that will go to entity states
        received_data = await controller.get_data(vin)
        if received_data:
            data[vin] = received_data
            _LOGGER.debug("Subaru data %s", pprint.pformat(received_data))

    return data


def _get_vehicle_info(controller: SubaruAPI, vin: str) -> dict:
    """Obtain vehicle identifiers and capabilities."""
    info = {
        VEHICLE_VIN: vin,
        VEHICLE_MODEL_NAME: controller.get_model_name(vin),
        VEHICLE_MODEL_YEAR: controller.get_model_year(vin),
        VEHICLE_NAME: controller.vin_to_name(vin),
        VEHICLE_HAS_EV: controller.get_ev_status(vin),
        VEHICLE_API_GEN: controller.get_api_gen(vin),
        VEHICLE_HAS_REMOTE_START: controller.get_res_status(vin),
        VEHICLE_HAS_REMOTE_SERVICE: controller.get_remote_status(vin),
        VEHICLE_HAS_SAFETY_SERVICE: controller.get_safety_status(vin),
        VEHICLE_LAST_UPDATE: 0,
        VEHICLE_LAST_FETCH: 0,
    }
    return info
