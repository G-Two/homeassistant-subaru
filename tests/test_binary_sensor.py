"""Test Subaru binary sensors."""

from unittest.mock import patch

import pytest

from custom_components.subaru.binary_sensor import (
    API_GEN_2_BINARY_SENSORS,
    DOMAIN as BINARY_SENSOR_DOMAIN,
    EV_BINARY_SENSORS,
)
from custom_components.subaru.const import (
    DOMAIN as SUBARU_DOMAIN,
    FETCH_INTERVAL,
    VEHICLE_NAME,
)
from homeassistant.util import slugify

from .api_responses import (
    EXPECTED_STATE_EV_BINARY_SENSORS,
    EXPECTED_STATE_EV_UNAVAILABLE,
    TEST_VIN_2_EV,
)
from .conftest import (
    MOCK_API_FETCH,
    MOCK_API_GET_DATA,
    advance_time,
    migrate_unique_ids,
    migrate_unique_ids_duplicate,
)


async def test_binary_sensors_ev(hass, ev_entry):
    """Test binary sensors."""
    _assert_data(hass, EXPECTED_STATE_EV_BINARY_SENSORS)


async def test_binary_sensors_missing_vin_data(hass, ev_entry):
    """Test for missing VIN dataset."""
    with patch(MOCK_API_FETCH), patch(MOCK_API_GET_DATA, return_value=None):
        advance_time(hass, FETCH_INTERVAL)
        await hass.async_block_till_done()

    _assert_data(hass, EXPECTED_STATE_EV_UNAVAILABLE)


@pytest.mark.parametrize(
    "entitydata,old_unique_id,new_unique_id",
    [
        (
            {
                "domain": BINARY_SENSOR_DOMAIN,
                "platform": SUBARU_DOMAIN,
                "unique_id": f"{TEST_VIN_2_EV}_{API_GEN_2_BINARY_SENSORS[3].name}",
            },
            f"{TEST_VIN_2_EV}_{API_GEN_2_BINARY_SENSORS[3].name}",
            f"{TEST_VIN_2_EV}_{API_GEN_2_BINARY_SENSORS[3].key}",
        ),
    ],
)
async def test_binary_sensor_migrate_unique_ids(
    hass, entitydata, old_unique_id, new_unique_id, subaru_config_entry
) -> None:
    """Test successful migration of entity unique_ids."""
    await migrate_unique_ids(
        hass, entitydata, old_unique_id, new_unique_id, subaru_config_entry
    )


@pytest.mark.parametrize(
    "entitydata,old_unique_id,new_unique_id",
    [
        (
            {
                "domain": BINARY_SENSOR_DOMAIN,
                "platform": SUBARU_DOMAIN,
                "unique_id": f"{TEST_VIN_2_EV}_{API_GEN_2_BINARY_SENSORS[3].name}",
            },
            f"{TEST_VIN_2_EV}_{API_GEN_2_BINARY_SENSORS[3].name}",
            f"{TEST_VIN_2_EV}_{API_GEN_2_BINARY_SENSORS[3].key}",
        )
    ],
)
async def test_binary_sensor_migrate_unique_ids_duplicate(
    hass, entitydata, old_unique_id, new_unique_id, subaru_config_entry
) -> None:
    """Test unsuccessful migration of entity unique_ids due to duplicate."""
    await migrate_unique_ids_duplicate(
        hass, entitydata, old_unique_id, new_unique_id, subaru_config_entry
    )


def _assert_data(hass, expected_state):
    sensor_list = EV_BINARY_SENSORS
    sensor_list.extend(API_GEN_2_BINARY_SENSORS)
    expected_states = {}
    for item in sensor_list:
        expected_states[f"binary_sensor.{slugify(f'{VEHICLE_NAME} {item.name}')}"] = (
            expected_state[item.key]
        )

    for sensor, state in expected_states.items():
        actual = hass.states.get(sensor)
        if actual:
            assert actual.state == state
