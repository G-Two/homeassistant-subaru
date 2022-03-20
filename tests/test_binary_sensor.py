"""Test Subaru binary sensors."""
from copy import deepcopy
from unittest.mock import patch

from subarulink.const import DOOR_ENGINE_HOOD_POSITION, VEHICLE_STATUS

from custom_components.subaru.binary_sensor import API_GEN_2_SENSORS, EV_SENSORS
from custom_components.subaru.const import VEHICLE_NAME
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.util import slugify

from .api_responses import (
    EXPECTED_STATE_EV_BINARY_SENSORS,
    EXPECTED_STATE_EV_UNAVAILABLE,
    TEST_VIN_2_EV,
    VEHICLE_DATA,
    VEHICLE_STATUS_EV,
)

from tests.conftest import MOCK_API_FETCH, MOCK_API_GET_DATA, advance_time_to_next_fetch

VEHICLE_NAME = VEHICLE_DATA[TEST_VIN_2_EV][VEHICLE_NAME]


async def test_binary_sensors_ev(hass, ev_entry):
    """Test binary sensors."""
    _assert_data(hass, EXPECTED_STATE_EV_BINARY_SENSORS)


async def test_binary_sensors_missing_vin_data(hass, ev_entry):
    """Test for missing VIN dataset."""
    with patch(MOCK_API_FETCH), patch(MOCK_API_GET_DATA, return_value=None):
        advance_time_to_next_fetch(hass)
        await hass.async_block_till_done()

    _assert_data(hass, EXPECTED_STATE_EV_UNAVAILABLE)


async def test_binary_sensors_missing_field(hass, ev_entry):
    """Test for missing field."""
    with patch(MOCK_API_FETCH), patch(MOCK_API_GET_DATA, return_value=None):
        advance_time_to_next_fetch(hass)
        await hass.async_block_till_done()
    missing_field_set = deepcopy(VEHICLE_STATUS_EV)
    missing_field_set[VEHICLE_STATUS].pop(DOOR_ENGINE_HOOD_POSITION)

    with patch(MOCK_API_FETCH), patch(
        MOCK_API_GET_DATA, return_value=missing_field_set
    ):
        advance_time_to_next_fetch(hass)
        await hass.async_block_till_done()
        expected_state_missing_field = deepcopy(EXPECTED_STATE_EV_BINARY_SENSORS)
        expected_state_missing_field[DOOR_ENGINE_HOOD_POSITION] = STATE_UNAVAILABLE
        _assert_data(hass, expected_state_missing_field)


def _assert_data(hass, expected_state):
    sensor_list = EV_SENSORS
    sensor_list.extend(API_GEN_2_SENSORS)
    expected_states = {}
    for item in sensor_list:
        expected_states[
            f"binary_sensor.{slugify(f'{VEHICLE_NAME} {item.suffix}')}"
        ] = expected_state[item.key]

    for sensor in expected_states:
        actual = hass.states.get(sensor)
        if actual:
            assert actual.state == expected_states[sensor]
