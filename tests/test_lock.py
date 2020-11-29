"""Test Subaru locks."""

from homeassistant.components.lock import DOMAIN as LOCK_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_LOCK, SERVICE_UNLOCK
from homeassistant.util.unit_system import IMPERIAL_SYSTEM, METRIC_SYSTEM
from pytest_homeassistant_custom_component.async_mock import patch

from .api_responses import TEST_VIN_2_EV, VEHICLE_DATA, VEHICLE_STATUS_EV
from .common import setup_subaru_integration

DEVICE_ID = "lock.test_vehicle_2_door_lock"


async def test_device_exists(hass):
    """Test subaru lock entity exists."""
    await _setup_ev(hass, unit_system=IMPERIAL_SYSTEM)

    entity_registry = await hass.helpers.entity_registry.async_get_registry()
    entry = entity_registry.async_get(DEVICE_ID)
    assert entry


async def test_lock(hass):
    """Test subaru lock function."""
    with patch(
        "custom_components.subaru.SubaruAPI.get_data", return_value=VEHICLE_STATUS_EV,
    ), patch("custom_components.subaru.SubaruAPI.lock",) as mock_lock:
        await _setup_ev(hass, unit_system=IMPERIAL_SYSTEM)

        await hass.services.async_call(
            LOCK_DOMAIN, SERVICE_LOCK, {ATTR_ENTITY_ID: DEVICE_ID}, blocking=True
        )
        await hass.async_block_till_done()
        mock_lock.assert_called_once()


async def test_unlock(hass):
    """Test subaru unlock function."""
    with patch(
        "custom_components.subaru.SubaruAPI.get_data", return_value=VEHICLE_STATUS_EV,
    ), patch("custom_components.subaru.SubaruAPI.unlock",) as mock_unlock:
        await _setup_ev(hass, unit_system=IMPERIAL_SYSTEM)

        await hass.services.async_call(
            LOCK_DOMAIN, SERVICE_UNLOCK, {ATTR_ENTITY_ID: DEVICE_ID}, blocking=True
        )
        await hass.async_block_till_done()
        mock_unlock.assert_called_once()


async def _setup_ev(hass, unit_system=METRIC_SYSTEM):
    hass.config.units = unit_system
    return await setup_subaru_integration(
        hass,
        vehicle_list=[TEST_VIN_2_EV],
        vehicle_data=VEHICLE_DATA[TEST_VIN_2_EV],
        vehicle_status=VEHICLE_STATUS_EV,
    )
