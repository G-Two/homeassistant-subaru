"""Test Subaru binary sensors."""
from copy import deepcopy
from unittest.mock import patch

import pytest
from subarulink.const import DOOR_ENGINE_HOOD_POSITION, VEHICLE_STATUS

from custom_components.subaru.binary_sensor import (
    API_GEN_2_SENSORS,
    DOMAIN as BINARY_SENSOR_DOMAIN,
    EV_SENSORS,
)
from custom_components.subaru.const import (
    DOMAIN as SUBARU_DOMAIN,
    FETCH_INTERVAL,
    VEHICLE_NAME,
)
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.helpers import entity_registry as er
from homeassistant.util import slugify

from .api_responses import (
    EXPECTED_STATE_EV_BINARY_SENSORS,
    EXPECTED_STATE_EV_UNAVAILABLE,
    TEST_VIN_2_EV,
    VEHICLE_DATA,
    VEHICLE_STATUS_EV,
)
from .conftest import (
    MOCK_API_FETCH,
    MOCK_API_GET_DATA,
    advance_time,
    setup_default_ev_entry,
)

VEHICLE_NAME = VEHICLE_DATA[TEST_VIN_2_EV][VEHICLE_NAME]


async def test_binary_sensors_ev(hass, ev_entry):
    """Test binary sensors."""
    _assert_data(hass, EXPECTED_STATE_EV_BINARY_SENSORS)


async def test_binary_sensors_missing_vin_data(hass, ev_entry):
    """Test for missing VIN dataset."""
    with patch(MOCK_API_FETCH), patch(MOCK_API_GET_DATA, return_value=None):
        advance_time(hass, FETCH_INTERVAL)
        await hass.async_block_till_done()

    _assert_data(hass, EXPECTED_STATE_EV_UNAVAILABLE)


async def test_binary_sensors_missing_field(hass, ev_entry):
    """Test for missing field."""
    with patch(MOCK_API_FETCH), patch(MOCK_API_GET_DATA, return_value=None):
        advance_time(hass, FETCH_INTERVAL)
        await hass.async_block_till_done()
    missing_field_set = deepcopy(VEHICLE_STATUS_EV)
    missing_field_set[VEHICLE_STATUS].pop(DOOR_ENGINE_HOOD_POSITION)

    with patch(MOCK_API_FETCH), patch(
        MOCK_API_GET_DATA, return_value=missing_field_set
    ):
        advance_time(hass, FETCH_INTERVAL)
        await hass.async_block_till_done()
        expected_state_missing_field = deepcopy(EXPECTED_STATE_EV_BINARY_SENSORS)
        expected_state_missing_field[DOOR_ENGINE_HOOD_POSITION] = STATE_UNAVAILABLE
        _assert_data(hass, expected_state_missing_field)


@pytest.mark.parametrize(
    "entitydata,old_unique_id,new_unique_id",
    [
        (
            {
                "domain": BINARY_SENSOR_DOMAIN,
                "platform": SUBARU_DOMAIN,
                "unique_id": f"{TEST_VIN_2_EV}_{API_GEN_2_SENSORS[3].name}",
            },
            f"{TEST_VIN_2_EV}_{API_GEN_2_SENSORS[3].name}",
            f"{TEST_VIN_2_EV}_{API_GEN_2_SENSORS[3].key}",
        ),
    ],
)
async def test_binary_sensor_migrate_unique_ids(
    hass, entitydata, old_unique_id, new_unique_id, subaru_config_entry
) -> None:
    """Test successful migration of entity unique_ids."""
    entity_registry = er.async_get(hass)
    entity: er.RegistryEntry = entity_registry.async_get_or_create(
        **entitydata,
        config_entry=subaru_config_entry,
    )
    assert entity.unique_id == old_unique_id

    await setup_default_ev_entry(hass, subaru_config_entry)

    entity_migrated = entity_registry.async_get(entity.entity_id)
    assert entity_migrated
    assert entity_migrated.unique_id == new_unique_id


@pytest.mark.parametrize(
    "entitydata,old_unique_id,new_unique_id",
    [
        (
            {
                "domain": BINARY_SENSOR_DOMAIN,
                "platform": SUBARU_DOMAIN,
                "unique_id": f"{TEST_VIN_2_EV}_{API_GEN_2_SENSORS[3].name}",
            },
            f"{TEST_VIN_2_EV}_{API_GEN_2_SENSORS[3].name}",
            f"{TEST_VIN_2_EV}_{API_GEN_2_SENSORS[3].key}",
        )
    ],
)
async def test_binary_sensor_migrate_unique_ids_duplicate(
    hass, entitydata, old_unique_id, new_unique_id, subaru_config_entry
) -> None:
    """Test unsuccessful migration of entity unique_ids due to duplicate."""
    entity_registry = er.async_get(hass)
    entity: er.RegistryEntry = entity_registry.async_get_or_create(
        **entitydata,
        config_entry=subaru_config_entry,
    )
    assert entity.unique_id == old_unique_id

    # create existing entry with new_unique_id that conflicts with migrate
    existing_entity = entity_registry.async_get_or_create(
        BINARY_SENSOR_DOMAIN,
        SUBARU_DOMAIN,
        unique_id=new_unique_id,
        config_entry=subaru_config_entry,
    )

    await setup_default_ev_entry(hass, subaru_config_entry)

    entity_migrated = entity_registry.async_get(entity.entity_id)
    assert entity_migrated
    assert entity_migrated.unique_id == old_unique_id

    entity_not_changed = entity_registry.async_get(existing_entity.entity_id)
    assert entity_not_changed
    assert entity_not_changed.unique_id == new_unique_id

    assert entity_migrated != entity_not_changed


def _assert_data(hass, expected_state):
    sensor_list = EV_SENSORS
    sensor_list.extend(API_GEN_2_SENSORS)
    expected_states = {}
    for item in sensor_list:
        expected_states[
            f"binary_sensor.{slugify(f'{VEHICLE_NAME} {item.name}')}"
        ] = expected_state[item.key]

    for sensor, state in expected_states.items():
        actual = hass.states.get(sensor)
        if actual:
            assert actual.state == state
