"""Remote vehicle services for Subaru integration."""

from __future__ import annotations

import logging
import time
from typing import Any

from subarulink.controller import Controller
from subarulink.exceptions import SubaruException

from homeassistant.components import persistent_notification
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    EVENT_SUBARU_COMMAND_FAIL,
    EVENT_SUBARU_COMMAND_SENT,
    EVENT_SUBARU_COMMAND_SUCCESS,
    FETCH_INTERVAL,
    REMOTE_SERVICE_POLL_VEHICLE,
    REMOTE_SERVICE_REFRESH,
    REMOTE_SERVICE_REMOTE_START,
    REMOTE_SERVICE_UNLOCK,
    UPDATE_INTERVAL,
    VEHICLE_LAST_FETCH,
    VEHICLE_LAST_UPDATE,
    VEHICLE_NAME,
    VEHICLE_VIN,
)
from .options import NotificationOptions

_LOGGER = logging.getLogger(__name__)


# pylint: disable=too-many-positional-arguments
async def async_call_remote_service(
    hass: HomeAssistant,
    controller: Controller,
    cmd: str,
    vehicle_info: dict,
    arg: Any | None,
    notify_option: str,
) -> None:
    """Execute subarulink remote command with optional start/end notification."""
    car_name = vehicle_info[VEHICLE_NAME]
    vin = vehicle_info[VEHICLE_VIN]
    notify = NotificationOptions.get_by_value(notify_option)
    if notify in [NotificationOptions.PENDING, NotificationOptions.SUCCESS]:
        persistent_notification.create(
            hass,
            f"Sending {cmd} command to {car_name}\nThis may take 10-15 seconds",
            "Subaru",
            DOMAIN,
        )
    hass.bus.async_fire(
        EVENT_SUBARU_COMMAND_SENT, {"command": cmd, "car_name": car_name}
    )
    _LOGGER.debug("Sending %s command command to %s", cmd, car_name)
    success = False
    err_msg = ""
    try:
        if cmd == REMOTE_SERVICE_POLL_VEHICLE:
            success = await poll_subaru(vehicle_info, controller, update_interval=0)
        elif cmd in [REMOTE_SERVICE_REMOTE_START, REMOTE_SERVICE_UNLOCK]:
            success = await getattr(controller, cmd)(vin, arg)
        elif cmd == REMOTE_SERVICE_REFRESH:
            success = True
        else:
            success = await getattr(controller, cmd)(vin)

    except SubaruException as err:
        err_msg = err.message

    finally:
        await refresh_subaru(vehicle_info, controller, refresh_interval=0)

    if notify in [NotificationOptions.PENDING, NotificationOptions.SUCCESS]:
        persistent_notification.dismiss(hass, DOMAIN)

    if success:
        if notify == NotificationOptions.SUCCESS:
            persistent_notification.create(
                hass,
                f"{cmd} command successfully completed for {car_name}",
                "Subaru",
            )
        hass.bus.async_fire(
            EVENT_SUBARU_COMMAND_SUCCESS, {"command": cmd, "car_name": car_name}
        )
        _LOGGER.debug("%s command successfully completed for %s", cmd, car_name)
        return

    if notify != NotificationOptions.DISABLE:
        persistent_notification.create(
            hass, f"{cmd} command failed for {car_name}: {err_msg}", "Subaru"
        )
    hass.bus.async_fire(
        EVENT_SUBARU_COMMAND_FAIL,
        {"command": cmd, "car_name": car_name, "message": err_msg},
    )
    raise HomeAssistantError(f"Service {cmd} failed for {car_name}: {err_msg}")


async def poll_subaru(vehicle, controller, update_interval=UPDATE_INTERVAL):
    """Commands remote vehicle update (polls the vehicle to update subaru API cache)."""
    cur_time = time.time()
    last_update = vehicle[VEHICLE_LAST_UPDATE]
    success = False

    if (cur_time - last_update) > update_interval:
        success = await controller.update(vehicle[VEHICLE_VIN], force=True)
        vehicle[VEHICLE_LAST_UPDATE] = cur_time

    return success


async def refresh_subaru(
    vehicle: dict, controller: Controller, refresh_interval: int = FETCH_INTERVAL
) -> bool:
    """Refresh data from Subaru servers."""
    cur_time = time.time()
    last_fetch = vehicle[VEHICLE_LAST_FETCH]
    vin = vehicle[VEHICLE_VIN]
    success = False

    if (cur_time - last_fetch) > refresh_interval:
        success = await controller.fetch(vin, force=True)
        vehicle[VEHICLE_LAST_FETCH] = cur_time

    return success
