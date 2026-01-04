"""The Subaru integration."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
import pprint

from subarulink import Controller as SubaruAPI, InvalidCredentials, SubaruException
from subarulink.const import COUNTRY_USA

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
    PLATFORMS,
    UPDATE_INTERVAL,
    UPDATE_INTERVAL_CHARGING,
    VEHICLE_API_GEN,
    VEHICLE_HAS_EV,
    VEHICLE_HAS_LOCK_STATUS,
    VEHICLE_HAS_POWER_WINDOWS,
    VEHICLE_HAS_REMOTE_SERVICE,
    VEHICLE_HAS_REMOTE_START,
    VEHICLE_HAS_SAFETY_SERVICE,
    VEHICLE_HAS_SUNROOF,
    VEHICLE_HAS_TPMS,
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

    vehicles = {}

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

        for vin in controller.get_vehicles():
            if controller.get_subscription_status(vin):
                vehicles[vin] = await _get_vehicle_info(controller, vin)

    except InvalidCredentials:
        _LOGGER.error("Invalid account")
        return False
    except SubaruException as err:
        raise ConfigEntryNotReady(err.message) from err

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

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def _refresh_subaru_data(
    hass: HomeAssistant,
    entry: ConfigEntry,
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

        # Poll vehicle, if option is enabled
        polling_option = PollingOptions.get_by_value(
            entry.options.get(CONF_POLLING_OPTION, PollingOptions.DISABLE.value)
        )
        if polling_option == PollingOptions.CHARGING:
            entity_registry = er.async_get(hass)
            if entity_id := entity_registry.async_get_entity_id(
                Platform.BINARY_SENSOR, DOMAIN, f"{vin.upper()}_EV_CHARGER_STATE_TYPE"
            ):
                if state := hass.states.get(entity_id):
                    if state.state == STATE_ON:
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


async def _get_vehicle_info(controller: SubaruAPI, vin: str) -> dict:
    """Obtain vehicle identifiers and capabilities."""
    info = {
        VEHICLE_VIN: vin,
        VEHICLE_MODEL_NAME: controller.get_model_name(vin),
        VEHICLE_MODEL_YEAR: controller.get_model_year(vin),
        VEHICLE_NAME: controller.vin_to_name(vin),
        VEHICLE_HAS_EV: controller.get_ev_status(vin),
        VEHICLE_API_GEN: controller.get_api_gen(vin),
        VEHICLE_HAS_LOCK_STATUS: await controller.has_lock_status(vin),
        VEHICLE_HAS_POWER_WINDOWS: await controller.has_power_windows(vin),
        VEHICLE_HAS_SUNROOF: controller.has_sunroof(vin),
        VEHICLE_HAS_REMOTE_START: controller.get_res_status(vin),
        VEHICLE_HAS_REMOTE_SERVICE: controller.get_remote_status(vin),
        VEHICLE_HAS_SAFETY_SERVICE: controller.get_safety_status(vin),
        VEHICLE_HAS_TPMS: controller.has_tpms(vin),
        VEHICLE_LAST_UPDATE: 0,
        VEHICLE_LAST_FETCH: 0,
    }
    return info
