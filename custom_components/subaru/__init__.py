"""The Subaru integration."""
import asyncio
from datetime import timedelta
import logging

from subarulink import Controller as SubaruAPI, InvalidCredentials, SubaruException
from subarulink.const import COUNTRY_USA
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_PASSWORD, CONF_PIN, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers import aiohttp_client, config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_COUNTRY,
    CONF_UPDATE_ENABLED,
    COORDINATOR_NAME,
    DOMAIN,
    ENTRY_CONTROLLER,
    ENTRY_COORDINATOR,
    ENTRY_VEHICLES,
    FETCH_INTERVAL,
    REMOTE_SERVICE_FETCH,
    SUPPORTED_PLATFORMS,
    UPDATE_INTERVAL,
    VEHICLE_API_GEN,
    VEHICLE_HAS_EV,
    VEHICLE_HAS_REMOTE_SERVICE,
    VEHICLE_HAS_REMOTE_START,
    VEHICLE_HAS_SAFETY_SERVICE,
    VEHICLE_LAST_UPDATE,
    VEHICLE_NAME,
    VEHICLE_VIN,
)
from .remote_service import (
    SERVICES_THAT_NEED_FETCH,
    async_call_remote_service,
    get_supported_services,
    update_subaru,
)

_LOGGER = logging.getLogger(__name__)

REMOTE_SERVICE_SCHEMA = vol.Schema({vol.Required(VEHICLE_VIN): cv.string})


async def async_setup(hass, base_config):
    """Do nothing since this integration does not support configuration.yml setup."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass, entry):
    """Set up Subaru from a config entry."""
    config = entry.data
    websession = aiohttp_client.async_get_clientsession(hass)

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
        vehicles[vin] = get_vehicle_info(controller, vin)

    async def async_update_data():
        """Fetch data from API endpoint."""
        try:
            return await refresh_subaru_data(entry, vehicles, controller)
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

    for component in SUPPORTED_PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    async def async_call_service(call):
        """Execute subaru service."""
        vin = call.data[VEHICLE_VIN].upper()

        if vin in vehicles:
            if call.service != REMOTE_SERVICE_FETCH:
                await async_call_remote_service(
                    hass, controller, call.service, vehicles[vin]
                )
            if call.service in SERVICES_THAT_NEED_FETCH:
                await coordinator.async_refresh()
            return

        hass.components.persistent_notification.create(
            f"ERROR - Invalid VIN provided while calling {call.service}", "Subaru"
        )
        raise HomeAssistantError(f"Invalid VIN provided while calling {call.service}")

    supported_services = get_supported_services(vehicles)

    for service in supported_services:
        hass.services.async_register(
            DOMAIN, service, async_call_service, schema=REMOTE_SERVICE_SCHEMA
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
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


async def refresh_subaru_data(config_entry, vehicle_info, controller):
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

        # Send an "update" remote command to vehicle, if supported (throttled with update_interval)
        if config_entry.options.get(CONF_UPDATE_ENABLED, False):
            await update_subaru(vehicle, controller)

        # Fetch data from Subaru servers
        await controller.fetch(vin, force=True)

        # Update our local data that will go to entity states
        received_data = await controller.get_data(vin)
        if received_data:
            data[vin] = received_data

    return data


def get_vehicle_info(controller, vin):
    """Obtain vehicle identifiers and capabilities."""
    info = {
        VEHICLE_VIN: vin,
        VEHICLE_NAME: controller.vin_to_name(vin),
        VEHICLE_HAS_EV: controller.get_ev_status(vin),
        VEHICLE_API_GEN: controller.get_api_gen(vin),
        VEHICLE_HAS_REMOTE_START: controller.get_res_status(vin),
        VEHICLE_HAS_REMOTE_SERVICE: controller.get_remote_status(vin),
        VEHICLE_HAS_SAFETY_SERVICE: controller.get_safety_status(vin),
        VEHICLE_LAST_UPDATE: 0,
    }
    return info
