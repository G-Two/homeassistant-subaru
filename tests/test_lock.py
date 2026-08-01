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
from subarulink.exceptions import SubaruException

from custom_components.subaru.const import (
    ATTR_DOOR,
    DOMAIN as SUBARU_DOMAIN,
    ENTRY_COORDINATOR,
    SERVICE_UNLOCK_SPECIFIC_DOOR,
    UNLOCK_DOOR_DRIVERS,
    VEHICLE_STATUS,
)
from custom_components.subaru.lock import UNLOCK_VERIFY_DELAY_SEC
from homeassistant.components.lock import DOMAIN as LOCK_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_LOCK, SERVICE_UNLOCK
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er

from .api_responses import TEST_VIN_1_G1, TEST_VIN_2_EV, VEHICLE_DATA
from .conftest import MOCK_API, advance_time, setup_subaru_config_entry

MOCK_API_FETCH = f"{MOCK_API}fetch"
MOCK_API_LOCK = f"{MOCK_API}lock"
MOCK_API_UNLOCK = f"{MOCK_API}unlock"
MOCK_API_UPDATE = f"{MOCK_API}update"
DEVICE_ID = "lock.test_vehicle_2_door_locks"
G1_DEVICE_ID = "lock.test_vehicle_1_door_locks"


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


async def test_is_locked_any_door_unknown(hass, ev_entry):
    """Test is_locked returns None when any door reports UNKNOWN."""
    coordinator = hass.data[SUBARU_DOMAIN][ev_entry.entry_id][ENTRY_COORDINATOR]
    status = coordinator.data[TEST_VIN_2_EV][VEHICLE_STATUS]
    for door in ALL_LOCK_DOORS:
        status[door] = "LOCKED"
    status[LOCK_BOOT_STATUS] = "UNKNOWN"

    lock_entity = hass.data["entity_components"][LOCK_DOMAIN].get_entity(DEVICE_ID)
    assert lock_entity is not None
    assert lock_entity.is_locked is None


async def test_lock_polls_vehicle_when_state_unknown(hass, ev_entry):
    """Test that the lock command issues a vehicle poll when state is still unknown after refresh."""
    coordinator = hass.data[SUBARU_DOMAIN][ev_entry.entry_id][ENTRY_COORDINATOR]
    status = coordinator.data[TEST_VIN_2_EV][VEHICLE_STATUS]
    for door in ALL_LOCK_DOORS:
        status[door] = "UNKNOWN"

    with (
        patch(MOCK_API_LOCK) as mock_lock,
        patch(MOCK_API_FETCH) as mock_fetch,
        patch(MOCK_API_UPDATE) as mock_update,
    ):
        await hass.services.async_call(
            LOCK_DOMAIN, SERVICE_LOCK, {ATTR_ENTITY_ID: DEVICE_ID}, blocking=True
        )
        await hass.async_block_till_done()
        mock_lock.assert_called_once()
        mock_update.assert_called_once()
        assert mock_fetch.call_count == 2


async def test_lock_does_not_poll_when_state_known(hass, ev_entry):
    """Test that the lock command does not extra-poll when the state is already known."""
    coordinator = hass.data[SUBARU_DOMAIN][ev_entry.entry_id][ENTRY_COORDINATOR]
    status = coordinator.data[TEST_VIN_2_EV][VEHICLE_STATUS]
    for door in ALL_LOCK_DOORS:
        status[door] = "LOCKED"

    with (
        patch(MOCK_API_LOCK) as mock_lock,
        patch(MOCK_API_FETCH) as mock_fetch,
        patch(MOCK_API_UPDATE) as mock_update,
    ):
        await hass.services.async_call(
            LOCK_DOMAIN, SERVICE_LOCK, {ATTR_ENTITY_ID: DEVICE_ID}, blocking=True
        )
        await hass.async_block_till_done()
        mock_lock.assert_called_once()
        mock_fetch.assert_called_once()
        mock_update.assert_not_called()


async def test_unlock_schedules_delayed_verify_poll(hass, ev_entry):
    """Test that unlock schedules a delayed poll past the auto-relock window."""
    with (
        patch(MOCK_API_UNLOCK) as mock_unlock,
        patch(MOCK_API_FETCH) as mock_fetch,
        patch(MOCK_API_UPDATE) as mock_update,
    ):
        await hass.services.async_call(
            LOCK_DOMAIN, SERVICE_UNLOCK, {ATTR_ENTITY_ID: DEVICE_ID}, blocking=True
        )
        await hass.async_block_till_done()
        mock_unlock.assert_called_once()
        # Immediate post-command refresh only; no extra poll yet
        mock_fetch.assert_called_once()
        mock_update.assert_not_called()

        # After the auto-relock window, the scheduled verify poll fires
        advance_time(hass, UNLOCK_VERIFY_DELAY_SEC)
        await hass.async_block_till_done()
        mock_update.assert_called_once()
        assert mock_fetch.call_count == 2


async def test_unlock_specific_door_schedules_delayed_verify_poll(hass, ev_entry):
    """Test that unlock_specific_door also schedules the delayed verify poll."""
    with (
        patch(MOCK_API_UNLOCK) as mock_unlock,
        patch(MOCK_API_FETCH) as mock_fetch,
        patch(MOCK_API_UPDATE) as mock_update,
    ):
        await hass.services.async_call(
            SUBARU_DOMAIN,
            SERVICE_UNLOCK_SPECIFIC_DOOR,
            {ATTR_ENTITY_ID: DEVICE_ID, ATTR_DOOR: UNLOCK_DOOR_DRIVERS},
            blocking=True,
        )
        await hass.async_block_till_done()
        mock_unlock.assert_called_once()
        mock_update.assert_not_called()

        advance_time(hass, UNLOCK_VERIFY_DELAY_SEC)
        await hass.async_block_till_done()
        mock_update.assert_called_once()
        assert mock_fetch.call_count == 2


async def test_unlock_failure_does_not_schedule_verify_poll(hass, ev_entry):
    """Test that a failed unlock command does not schedule a verify poll."""
    with (
        patch(MOCK_API_UNLOCK, return_value=False),
        patch(MOCK_API_FETCH),
        patch(MOCK_API_UPDATE) as mock_update,
    ):
        with raises(HomeAssistantError):
            await hass.services.async_call(
                LOCK_DOMAIN, SERVICE_UNLOCK, {ATTR_ENTITY_ID: DEVICE_ID}, blocking=True
            )
            await hass.async_block_till_done()

        advance_time(hass, UNLOCK_VERIFY_DELAY_SEC)
        await hass.async_block_till_done()
        mock_update.assert_not_called()


async def test_verify_poll_handles_subaru_exception(hass, ev_entry, caplog):
    """Test that a SubaruException during the verify poll is caught and logged."""
    with (
        patch(MOCK_API_UNLOCK),
        patch(MOCK_API_FETCH),
        patch(MOCK_API_UPDATE, side_effect=SubaruException("poll failed")),
    ):
        await hass.services.async_call(
            LOCK_DOMAIN, SERVICE_UNLOCK, {ATTR_ENTITY_ID: DEVICE_ID}, blocking=True
        )
        await hass.async_block_till_done()

        advance_time(hass, UNLOCK_VERIFY_DELAY_SEC)
        await hass.async_block_till_done()

    assert "Lock state verification poll failed" in caplog.text
    assert "poll failed" in caplog.text


async def test_unlock_without_lock_status_notifies_listeners(
    hass, subaru_config_entry, enable_custom_integrations
):
    """Test unlock on a vehicle without lock status reporting notifies listeners without scheduling a verify poll."""
    await setup_subaru_config_entry(
        hass,
        subaru_config_entry,
        vehicle_list=[TEST_VIN_1_G1],
        vehicle_data=VEHICLE_DATA[TEST_VIN_1_G1],
    )
    with (
        patch(MOCK_API_UNLOCK) as mock_unlock,
        patch(MOCK_API_FETCH) as mock_fetch,
        patch(MOCK_API_UPDATE) as mock_update,
    ):
        await hass.services.async_call(
            LOCK_DOMAIN, SERVICE_UNLOCK, {ATTR_ENTITY_ID: G1_DEVICE_ID}, blocking=True
        )
        await hass.async_block_till_done()
        mock_unlock.assert_called_once()
        # Single refresh from the command itself; no verify scheduled
        mock_fetch.assert_called_once()

        advance_time(hass, UNLOCK_VERIFY_DELAY_SEC)
        await hass.async_block_till_done()
        mock_update.assert_not_called()
        assert mock_fetch.call_count == 1


async def test_unlock_specific_door_without_lock_status_notifies_listeners(
    hass, subaru_config_entry, enable_custom_integrations
):
    """Test unlock_specific_door on a vehicle without lock status reporting notifies listeners without scheduling a verify poll."""
    await setup_subaru_config_entry(
        hass,
        subaru_config_entry,
        vehicle_list=[TEST_VIN_1_G1],
        vehicle_data=VEHICLE_DATA[TEST_VIN_1_G1],
    )
    with (
        patch(MOCK_API_UNLOCK) as mock_unlock,
        patch(MOCK_API_FETCH) as mock_fetch,
        patch(MOCK_API_UPDATE) as mock_update,
    ):
        await hass.services.async_call(
            SUBARU_DOMAIN,
            SERVICE_UNLOCK_SPECIFIC_DOOR,
            {ATTR_ENTITY_ID: G1_DEVICE_ID, ATTR_DOOR: UNLOCK_DOOR_DRIVERS},
            blocking=True,
        )
        await hass.async_block_till_done()
        mock_unlock.assert_called_once()
        mock_fetch.assert_called_once()

        advance_time(hass, UNLOCK_VERIFY_DELAY_SEC)
        await hass.async_block_till_done()
        mock_update.assert_not_called()
        assert mock_fetch.call_count == 1


async def test_repeated_unlock_replaces_pending_verify_poll(hass, ev_entry):
    """Test that issuing another unlock cancels the prior pending verify poll."""
    with (
        patch(MOCK_API_UNLOCK),
        patch(MOCK_API_FETCH),
        patch(MOCK_API_UPDATE) as mock_update,
    ):
        await hass.services.async_call(
            LOCK_DOMAIN, SERVICE_UNLOCK, {ATTR_ENTITY_ID: DEVICE_ID}, blocking=True
        )
        await hass.async_block_till_done()

        # Re-issue the unlock before the first scheduled verify fires
        await hass.services.async_call(
            LOCK_DOMAIN, SERVICE_UNLOCK, {ATTR_ENTITY_ID: DEVICE_ID}, blocking=True
        )
        await hass.async_block_till_done()

        advance_time(hass, UNLOCK_VERIFY_DELAY_SEC)
        await hass.async_block_till_done()
        # Only one verify poll should have fired (from the second unlock)
        mock_update.assert_called_once()


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
