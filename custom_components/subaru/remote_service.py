"""Remote vehicle services for Subaru integration."""
import logging
import time

from subarulink.exceptions import SubaruException

from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    FETCH_INTERVAL,
    REMOTE_SERVICE_CHARGE_START,
    REMOTE_SERVICE_FETCH,
    REMOTE_SERVICE_HORN,
    REMOTE_SERVICE_HORN_STOP,
    REMOTE_SERVICE_LIGHTS,
    REMOTE_SERVICE_LIGHTS_STOP,
    REMOTE_SERVICE_REMOTE_START,
    REMOTE_SERVICE_REMOTE_STOP,
    REMOTE_SERVICE_UNLOCK,
    REMOTE_SERVICE_UPDATE,
    UPDATE_INTERVAL,
    VEHICLE_HAS_EV,
    VEHICLE_HAS_REMOTE_SERVICE,
    VEHICLE_HAS_REMOTE_START,
    VEHICLE_HAS_SAFETY_SERVICE,
    VEHICLE_LAST_FETCH,
    VEHICLE_LAST_UPDATE,
    VEHICLE_NAME,
    VEHICLE_VIN,
)
from .options import NotificationOptions

_LOGGER = logging.getLogger(__name__)

SERVICES_THAT_NEED_FETCH = [
    REMOTE_SERVICE_FETCH,
    REMOTE_SERVICE_REMOTE_START,
    REMOTE_SERVICE_REMOTE_STOP,
    REMOTE_SERVICE_UPDATE,
    REMOTE_SERVICE_CHARGE_START,
]


async def async_call_remote_service(
    hass, controller, cmd, vehicle_info, arg, notify_option
):
    """Execute subarulink remote command with optional start/end notification."""
    car_name = vehicle_info[VEHICLE_NAME]
    vin = vehicle_info[VEHICLE_VIN]
    notify = NotificationOptions.get_by_value(notify_option)
    if notify in [NotificationOptions.PENDING, NotificationOptions.SUCCESS]:
        hass.components.persistent_notification.create(
            f"Sending {cmd} command to {car_name}\nThis may take 10-15 seconds",
            "Subaru",
            DOMAIN,
        )
    _LOGGER.debug("Sending %s command command to %s", cmd, car_name)
    success = False
    err_msg = ""
    try:
        if cmd == REMOTE_SERVICE_UPDATE:
            success = await poll_subaru(vehicle_info, controller, update_interval=0)
        elif cmd in [REMOTE_SERVICE_REMOTE_START, REMOTE_SERVICE_UNLOCK]:
            success = await getattr(controller, cmd)(vin, arg)
        elif cmd == REMOTE_SERVICE_FETCH:
            pass
        else:
            success = await getattr(controller, cmd)(vin)

        if cmd in SERVICES_THAT_NEED_FETCH:
            success = await refresh_subaru(vehicle_info, controller, refresh_interval=0)

    except SubaruException as err:
        err_msg = err.message

    if notify in [NotificationOptions.PENDING, NotificationOptions.SUCCESS]:
        hass.components.persistent_notification.dismiss(DOMAIN)

    if success:
        if notify == NotificationOptions.SUCCESS:
            hass.components.persistent_notification.create(
                f"{cmd} command successfully completed for {car_name}",
                "Subaru",
            )
        _LOGGER.debug("%s command successfully completed for %s", cmd, car_name)
        return

    if notify != NotificationOptions.DISABLE:
        hass.components.persistent_notification.create(
            f"{cmd} command failed for {car_name}: {err_msg}", "Subaru"
        )
    raise HomeAssistantError(f"Service {cmd} failed for {car_name}: {err_msg}")


def get_supported_services(vehicle_info):
    """Return a list of supported services."""
    remote_services = set()
    for vin in vehicle_info:
        if vehicle_info[vin][VEHICLE_HAS_SAFETY_SERVICE]:
            remote_services.add(REMOTE_SERVICE_FETCH)
        if vehicle_info[vin][VEHICLE_HAS_REMOTE_SERVICE]:
            remote_services.add(REMOTE_SERVICE_HORN)
            remote_services.add(REMOTE_SERVICE_HORN_STOP)
            remote_services.add(REMOTE_SERVICE_LIGHTS)
            remote_services.add(REMOTE_SERVICE_LIGHTS_STOP)
            remote_services.add(REMOTE_SERVICE_UPDATE)
        if (
            vehicle_info[vin][VEHICLE_HAS_REMOTE_START]
            or vehicle_info[vin][VEHICLE_HAS_EV]
        ):
            remote_services.add(REMOTE_SERVICE_REMOTE_START)
            remote_services.add(REMOTE_SERVICE_REMOTE_STOP)
        if vehicle_info[vin][VEHICLE_HAS_EV]:
            remote_services.add(REMOTE_SERVICE_CHARGE_START)
    return remote_services


async def poll_subaru(vehicle, controller, update_interval=UPDATE_INTERVAL):
    """Commands remote vehicle update (polls the vehicle to update subaru API cache)."""
    cur_time = time.time()
    last_update = vehicle[VEHICLE_LAST_UPDATE]
    success = None

    if (cur_time - last_update) > update_interval:
        success = await controller.update(vehicle[VEHICLE_VIN], force=True)
        vehicle[VEHICLE_LAST_UPDATE] = cur_time

    return success


async def refresh_subaru(vehicle, controller, refresh_interval=FETCH_INTERVAL):
    """Refresh data from Subaru servers."""
    cur_time = time.time()
    last_fetch = vehicle[VEHICLE_LAST_FETCH]
    vin = vehicle[VEHICLE_VIN]
    success = None

    if (cur_time - last_fetch) > refresh_interval:
        success = await controller.fetch(vin, force=True)
        vehicle[VEHICLE_LAST_FETCH] = cur_time

    return success
