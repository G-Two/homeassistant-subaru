"""Test Subaru locks."""

from unittest.mock import patch

from pytest import raises
from subarulink.const import (
    LOCK_BOOT_STATUS,
    LOCK_FRONT_LEFT_STATUS,
    LOCK_FRONT_RIGHT_STATUS,
    LOCK_REAR_LEFT_STATUS,
    LOCK_REAR_RIGHT_STATUS,
)

from custom_components.subaru.const import (
    ATTR_DOOR,
    DOMAIN as SUBARU_DOMAIN,
    ENTRY_COORDINATOR,
    SERVICE_UNLOCK_SPECIFIC_DOOR,
    UNLOCK_DOOR_DRIVERS,
    VEHICLE_STATUS,
)
from homeassistant.components.lock import DOMAIN as LOCK_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_LOCK, SERVICE_UNLOCK
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er

from .api_responses import TEST_VIN_2_EV
from .conftest import MOCK_API

MOCK_API_FETCH = f"{MOCK_API}fetch"
MOCK_API_LOCK = f"{MOCK_API}lock"
MOCK_API_UNLOCK = f"{MOCK_API}unlock"
DEVICE_ID = "lock.test_vehicle_2_door_locks"


async def test_device_exists(hass, entity_registry: er.EntityRegistry, ev_entry):
    """Test subaru lock entity exists."""
    entry = entity_registry.async_get(DEVICE_ID)
    assert entry


async def test_lock(hass, ev_entry):
    """Test subaru lock function."""
    with patch(MOCK_API_LOCK) as mock_lock, patch(MOCK_API_FETCH) as mock_fetch:
        await hass.services.async_call(
            LOCK_DOMAIN, SERVICE_LOCK, {ATTR_ENTITY_ID: DEVICE_ID}, blocking=True
        )
        await hass.async_block_till_done()
        mock_lock.assert_called_once()
        mock_fetch.assert_called_once()


async def test_unlock(hass, ev_entry):
    """Test subaru unlock function."""
    with patch(MOCK_API_UNLOCK) as mock_unlock, patch(MOCK_API_FETCH) as mock_fetch:
        await hass.services.async_call(
            LOCK_DOMAIN, SERVICE_UNLOCK, {ATTR_ENTITY_ID: DEVICE_ID}, blocking=True
        )
        await hass.async_block_till_done()
        mock_unlock.assert_called_once()
        mock_fetch.assert_called_once()


async def test_unlock_specific_door(hass, ev_entry):
    """Test subaru unlock specific door function."""
    with patch(MOCK_API_UNLOCK) as mock_unlock, patch(MOCK_API_FETCH) as mock_fetch:
        await hass.services.async_call(
            SUBARU_DOMAIN,
            SERVICE_UNLOCK_SPECIFIC_DOOR,
            {ATTR_ENTITY_ID: DEVICE_ID, ATTR_DOOR: UNLOCK_DOOR_DRIVERS},
            blocking=True,
        )
        await hass.async_block_till_done()
        mock_unlock.assert_called_once()
        mock_fetch.assert_called_once()


async def test_lock_failed(hass, ev_entry):
    """Test subaru lock failure path raises HomeAssistantError."""
    with (
        patch(MOCK_API_LOCK, return_value=False) as mock_lock,
        patch(MOCK_API_FETCH) as mock_fetch,
    ):
        with raises(HomeAssistantError):
            await hass.services.async_call(
                LOCK_DOMAIN, SERVICE_LOCK, {ATTR_ENTITY_ID: DEVICE_ID}, blocking=True
            )
            await hass.async_block_till_done()
        mock_lock.assert_called_once()
        mock_fetch.assert_called_once()


async def test_unlock_failed(hass, ev_entry):
    """Test subaru unlock failure path raises HomeAssistantError."""
    with (
        patch(MOCK_API_UNLOCK, return_value=False) as mock_unlock,
        patch(MOCK_API_FETCH) as mock_fetch,
    ):
        with raises(HomeAssistantError):
            await hass.services.async_call(
                LOCK_DOMAIN, SERVICE_UNLOCK, {ATTR_ENTITY_ID: DEVICE_ID}, blocking=True
            )
            await hass.async_block_till_done()
        mock_unlock.assert_called_once()
        mock_fetch.assert_called_once()


async def test_unlock_specific_door_failed(hass, ev_entry):
    """Test subaru unlock specific door failure raises HomeAssistantError."""
    with (
        patch(MOCK_API_UNLOCK, return_value=False) as mock_unlock,
        patch(MOCK_API_FETCH) as mock_fetch,
    ):
        with raises(HomeAssistantError):
            await hass.services.async_call(
                SUBARU_DOMAIN,
                SERVICE_UNLOCK_SPECIFIC_DOOR,
                {ATTR_ENTITY_ID: DEVICE_ID, ATTR_DOOR: UNLOCK_DOOR_DRIVERS},
                blocking=True,
            )
            await hass.async_block_till_done()
        mock_unlock.assert_called_once()
        mock_fetch.assert_called_once()


async def test_is_locked_vin_absent_from_coordinator(hass, ev_entry):
    """Test is_locked returns None when VIN is absent from coordinator data."""
    coordinator = hass.data[SUBARU_DOMAIN][ev_entry.entry_id][ENTRY_COORDINATOR]
    coordinator.data.pop(TEST_VIN_2_EV, None)

    lock_entity = hass.data["entity_components"][LOCK_DOMAIN].get_entity(DEVICE_ID)
    assert lock_entity is not None
    assert lock_entity.is_locked is None


async def test_extra_state_attributes_vin_absent_from_coordinator(hass, ev_entry):
    """Test extra_state_attributes returns None when VIN is absent from coordinator data."""
    coordinator = hass.data[SUBARU_DOMAIN][ev_entry.entry_id][ENTRY_COORDINATOR]
    coordinator.data.pop(TEST_VIN_2_EV, None)

    lock_entity = hass.data["entity_components"][LOCK_DOMAIN].get_entity(DEVICE_ID)
    assert lock_entity is not None
    assert lock_entity.extra_state_attributes is None


ALL_LOCK_DOORS = [
    LOCK_BOOT_STATUS,
    LOCK_FRONT_LEFT_STATUS,
    LOCK_FRONT_RIGHT_STATUS,
    LOCK_REAR_LEFT_STATUS,
    LOCK_REAR_RIGHT_STATUS,
]


async def test_is_locked_all_doors_locked(hass, ev_entry):
    """Test is_locked is True when the vehicle reports every door locked."""
    coordinator = hass.data[SUBARU_DOMAIN][ev_entry.entry_id][ENTRY_COORDINATOR]
    status = coordinator.data[TEST_VIN_2_EV][VEHICLE_STATUS]
    for door in ALL_LOCK_DOORS:
        status[door] = "LOCKED"

    lock_entity = hass.data["entity_components"][LOCK_DOMAIN].get_entity(DEVICE_ID)
    assert lock_entity is not None
    assert lock_entity.is_locked is True


async def test_is_locked_one_door_unlocked(hass, ev_entry):
    """Test is_locked is False when any single door is reported unlocked."""
    coordinator = hass.data[SUBARU_DOMAIN][ev_entry.entry_id][ENTRY_COORDINATOR]
    status = coordinator.data[TEST_VIN_2_EV][VEHICLE_STATUS]
    for door in ALL_LOCK_DOORS:
        status[door] = "LOCKED"
    status[LOCK_BOOT_STATUS] = "UNLOCKED"

    lock_entity = hass.data["entity_components"][LOCK_DOMAIN].get_entity(DEVICE_ID)
    assert lock_entity is not None
    assert lock_entity.is_locked is False


async def test_lock_state_follows_coordinator_update(hass, ev_entry):
    """Test the lock entity re-renders its state when the coordinator updates.

    Regression test: the lock entity must be wired to the coordinator so that a
    correct lock status reported by the vehicle is reflected in Home Assistant,
    rather than remaining stuck at its initial state.
    """
    coordinator = hass.data[SUBARU_DOMAIN][ev_entry.entry_id][ENTRY_COORDINATOR]
    status = coordinator.data[TEST_VIN_2_EV][VEHICLE_STATUS]
    for door in ALL_LOCK_DOORS:
        status[door] = "LOCKED"

    coordinator.async_set_updated_data(coordinator.data)
    await hass.async_block_till_done()
    assert hass.states.get(DEVICE_ID).state == "locked"

    status[LOCK_FRONT_LEFT_STATUS] = "UNLOCKED"
    coordinator.async_set_updated_data(coordinator.data)
    await hass.async_block_till_done()
    assert hass.states.get(DEVICE_ID).state == "unlocked"
