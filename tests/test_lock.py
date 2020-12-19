"""Test Subaru locks."""

from homeassistant.components.lock import DOMAIN as LOCK_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_LOCK, SERVICE_UNLOCK
from pytest_homeassistant_custom_component.async_mock import patch

from .common import ev_entry

DEVICE_ID = "lock.test_vehicle_2_door_lock"


async def test_device_exists(hass, ev_entry):
    """Test subaru lock entity exists."""
    entity_registry = await hass.helpers.entity_registry.async_get_registry()
    entry = entity_registry.async_get(DEVICE_ID)
    assert entry


async def test_lock(hass, ev_entry):
    """Test subaru lock function."""
    with patch("custom_components.subaru.SubaruAPI.lock",) as mock_lock:
        await hass.services.async_call(
            LOCK_DOMAIN, SERVICE_LOCK, {ATTR_ENTITY_ID: DEVICE_ID}, blocking=True
        )
        await hass.async_block_till_done()
        mock_lock.assert_called_once()


async def test_unlock(hass, ev_entry):
    """Test subaru unlock function."""
    with patch("custom_components.subaru.SubaruAPI.unlock",) as mock_unlock:
        await hass.services.async_call(
            LOCK_DOMAIN, SERVICE_UNLOCK, {ATTR_ENTITY_ID: DEVICE_ID}, blocking=True
        )
        await hass.async_block_till_done()
        mock_unlock.assert_called_once()
