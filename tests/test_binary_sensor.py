"""Test Subaru binary sensors."""

from unittest.mock import patch

import pytest

from custom_components.subaru.binary_sensor import (
    API_GEN_2_BINARY_SENSORS,
    DOMAIN as BINARY_SENSOR_DOMAIN,
    EV_BINARY_SENSORS,
    POWER_WINDOW_BINARY_SENSORS,
    SUNROOF_BINARY_SENSORS,
    TROUBLE_BINARY_SENSOR,
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
    TEST_VIN_4_G4,
    VEHICLE_DATA,
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


async def test_binary_sensors_g4(hass, g4_entry):
    """Test Gen4 vehicle gets the same binary sensors as Gen2/Gen3."""
    # Gen4 vehicles should have API_GEN_2 sensors + conditionals
    vehicle_info = VEHICLE_DATA[TEST_VIN_4_G4]
    expected_sensors = []
    expected_sensors.extend(TROUBLE_BINARY_SENSOR)
    expected_sensors.extend(API_GEN_2_BINARY_SENSORS)
    
    # Gen4 test vehicle has power windows and sunroof
    if vehicle_info.get("has_power_windows") or vehicle_info.get("has_sunroof"):
        expected_sensors.extend(POWER_WINDOW_BINARY_SENSORS)
    if vehicle_info.get("has_sunroof"):
        expected_sensors.extend(SUNROOF_BINARY_SENSORS)
    
    # Verify all expected sensors are created
    for sensor_desc in expected_sensors:
        entity_id = f"binary_sensor.{slugify(f'{vehicle_info[VEHICLE_NAME]} {sensor_desc.name}')}"
        entity = hass.states.get(entity_id)
        assert entity is not None, f"Expected sensor {entity_id} not found"


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
    sensor_list = []
    sensor_list.extend(EV_BINARY_SENSORS)
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
