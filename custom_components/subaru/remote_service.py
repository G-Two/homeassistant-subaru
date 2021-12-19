"""Remote vehicle services for Subaru integration."""
import logging
import time

from subarulink.exceptions import SubaruException

from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    REMOTE_SERVICE_CHARGE_START,
    REMOTE_SERVICE_FETCH,
    REMOTE_SERVICE_HORN,
    REMOTE_SERVICE_HORN_STOP,
    REMOTE_SERVICE_LIGHTS,
    REMOTE_SERVICE_LIGHTS_STOP,
    REMOTE_SERVICE_REMOTE_START,
    REMOTE_SERVICE_REMOTE_STOP,
    REMOTE_SERVICE_UPDATE,
    UPDATE_INTERVAL,
    VEHICLE_HAS_EV,
    VEHICLE_HAS_REMOTE_SERVICE,
    VEHICLE_HAS_REMOTE_START,
    VEHICLE_HAS_SAFETY_SERVICE,
    VEHICLE_LAST_UPDATE,
    VEHICLE_NAME,
    VEHICLE_VIN,
    NotificationOptions,
)

_LOGGER = logging.getLogger(__name__)

SERVICES_THAT_NEED_FETCH = [
    REMOTE_SERVICE_FETCH,
    REMOTE_SERVICE_REMOTE_START,
    REMOTE_SERVICE_REMOTE_STOP,
    REMOTE_SERVICE_UPDATE,
    REMOTE_SERVICE_CHARGE_START,
]


async def async_call_remote_service(hass, controller, cmd, vehicle_info, notify_option):
    """Execute subarulink remote command with start/end notification."""
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
            success = await update_subaru(
                vehicle_info, controller, override_interval=True
            )
        else:
            success = await getattr(controller, cmd)(vin)
    except SubaruException as err:
        err_msg = err.message

    if notify in [NotificationOptions.PENDING, NotificationOptions.SUCCESS]:
        hass.components.persistent_notification.dismiss(DOMAIN)

    if success:
        if notify == NotificationOptions.SUCCESS:
            hass.components.persistent_notification.create(
                f"{cmd} command successfully completed for {car_name}", "Subaru",
            )
        _LOGGER.debug("%s command successfully completed for %s", cmd, car_name)
        return True

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


async def update_subaru(vehicle, controller, override_interval=False):
    """Commands remote vehicle update (polls the vehicle to update subaru API cache)."""
    cur_time = time.time()
    last_update = vehicle[VEHICLE_LAST_UPDATE]
    success = None

    if (cur_time - last_update) > UPDATE_INTERVAL or override_interval:
        success = await controller.update(vehicle[VEHICLE_VIN], force=True)
        vehicle[VEHICLE_LAST_UPDATE] = cur_time

    return success
