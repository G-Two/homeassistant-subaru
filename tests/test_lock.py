"""Test Subaru locks."""

from unittest.mock import patch

from custom_components.subaru.const import (
    ATTR_DOOR,
    DOMAIN as SUBARU_DOMAIN,
    SERVICE_UNLOCK_SPECIFIC_DOOR,
    UNLOCK_DOOR_DRIVERS,
)
from homeassistant.components.lock import DOMAIN as LOCK_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_LOCK, SERVICE_UNLOCK

from .conftest import MOCK_API

MOCK_API_LOCK = f"{MOCK_API}lock"
MOCK_API_UNLOCK = f"{MOCK_API}unlock"
DEVICE_ID = "lock.test_vehicle_2_door_locks"


async def test_device_exists(hass, ev_entry):
    """Test subaru lock entity exists."""
    entity_registry = hass.helpers.entity_registry.async_get(hass)
    entry = entity_registry.async_get(DEVICE_ID)
    assert entry


async def test_lock(hass, ev_entry):
    """Test subaru lock function."""
    with patch(MOCK_API_LOCK) as mock_lock:
        await hass.services.async_call(
            LOCK_DOMAIN, SERVICE_LOCK, {ATTR_ENTITY_ID: DEVICE_ID}, blocking=True
        )
        await hass.async_block_till_done()
        mock_lock.assert_called_once()


async def test_unlock(hass, ev_entry):
    """Test subaru unlock function."""
    with patch(MOCK_API_UNLOCK) as mock_unlock:
        await hass.services.async_call(
            LOCK_DOMAIN, SERVICE_UNLOCK, {ATTR_ENTITY_ID: DEVICE_ID}, blocking=True
        )
        await hass.async_block_till_done()
        mock_unlock.assert_called_once()


async def test_unlock_specific_door(hass, ev_entry):
    """Test subaru unlock specific door function."""
    with patch(MOCK_API_UNLOCK) as mock_unlock:
        await hass.services.async_call(
            SUBARU_DOMAIN,
            SERVICE_UNLOCK_SPECIFIC_DOOR,
            {ATTR_ENTITY_ID: DEVICE_ID, ATTR_DOOR: UNLOCK_DOOR_DRIVERS},
            blocking=True,
        )
        await hass.async_block_till_done()
        mock_unlock.assert_called_once()
