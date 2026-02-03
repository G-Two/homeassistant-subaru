"""Test Subaru sensors."""

from typing import Any
from unittest.mock import patch

import pytest

from custom_components.subaru.const import FETCH_INTERVAL, VEHICLE_HAS_TPMS
from custom_components.subaru.sensor import (
    API_GEN_2_SENSORS,
    API_GEN_3_SENSORS,
    DOMAIN as SUBARU_DOMAIN,
    EV_SENSORS,
    SAFETY_SENSORS,
    TPMS_SENSORS,
)
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .api_responses import (
    EXPECTED_STATE_EV_UNAVAILABLE,
    TEST_VIN_2_EV,
    TEST_VIN_4_G4,
    VEHICLE_DATA,
    VEHICLE_STATUS_G4,
)
from .conftest import (
    MOCK_API_FETCH,
    MOCK_API_GET_DATA,
    advance_time,
    setup_subaru_config_entry,
)


async def test_sensors_missing_vin_data(hass: HomeAssistant, ev_entry) -> None:
    """Test for missing VIN dataset."""
    with patch(MOCK_API_FETCH), patch(MOCK_API_GET_DATA, return_value=None):
        advance_time(hass, FETCH_INTERVAL)
        await hass.async_block_till_done()

    _assert_data(hass, EXPECTED_STATE_EV_UNAVAILABLE)


@pytest.mark.parametrize(
    ("entitydata", "old_unique_id", "new_unique_id"),
    [
        (
            {
                "domain": SENSOR_DOMAIN,
                "platform": SUBARU_DOMAIN,
                "unique_id": f"{TEST_VIN_2_EV}_Avg fuel consumption",
            },
            f"{TEST_VIN_2_EV}_Avg fuel consumption",
            f"{TEST_VIN_2_EV}_{API_GEN_2_SENSORS[0].key}",
        ),
    ],
)
async def test_sensor_migrate_unique_ids(
    hass: HomeAssistant, entitydata, old_unique_id, new_unique_id, subaru_config_entry
) -> None:
    """Test successful migration of entity unique_ids."""
    entity_registry = er.async_get(hass)
    entity: er.RegistryEntry = entity_registry.async_get_or_create(
        **entitydata,
        config_entry=subaru_config_entry,
    )
    assert entity.unique_id == old_unique_id

    await setup_subaru_config_entry(hass, subaru_config_entry)

    entity_migrated = entity_registry.async_get(entity.entity_id)
    assert entity_migrated
    assert entity_migrated.unique_id == new_unique_id


@pytest.mark.parametrize(
    ("entitydata", "old_unique_id", "new_unique_id"),
    [
        (
            {
                "domain": SENSOR_DOMAIN,
                "platform": SUBARU_DOMAIN,
                "unique_id": f"{TEST_VIN_2_EV}_Avg fuel consumption",
            },
            f"{TEST_VIN_2_EV}_Avg fuel consumption",
            f"{TEST_VIN_2_EV}_{API_GEN_2_SENSORS[0].key}",
        )
    ],
)
async def test_sensor_migrate_unique_ids_duplicate(
    hass: HomeAssistant, entitydata, old_unique_id, new_unique_id, subaru_config_entry
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
        SENSOR_DOMAIN,
        SUBARU_DOMAIN,
        unique_id=new_unique_id,
        config_entry=subaru_config_entry,
    )

    await setup_subaru_config_entry(hass, subaru_config_entry)

    entity_migrated = entity_registry.async_get(entity.entity_id)
    assert entity_migrated
    assert entity_migrated.unique_id == old_unique_id

    entity_not_changed = entity_registry.async_get(existing_entity.entity_id)
    assert entity_not_changed
    assert entity_not_changed.unique_id == new_unique_id

    assert entity_migrated != entity_not_changed


async def test_gen4_vehicle_sensors(
    hass: HomeAssistant, subaru_config_entry
) -> None:
    """Test that Gen4 vehicles get the expected sensor sets (Gen2/Gen3 sensors)."""
    await setup_subaru_config_entry(
        hass,
        subaru_config_entry,
        vehicle_list=[TEST_VIN_4_G4],
        vehicle_data=VEHICLE_DATA[TEST_VIN_4_G4],
        vehicle_status=VEHICLE_STATUS_G4,
    )

    entity_registry = er.async_get(hass)

    # Gen4 vehicles should have all SAFETY_SENSORS
    for sensor_desc in SAFETY_SENSORS:
        entity_id = entity_registry.async_get_entity_id(
            SENSOR_DOMAIN, SUBARU_DOMAIN, f"{TEST_VIN_4_G4}_{sensor_desc.key}"
        )
        assert entity_id is not None, f"Missing SAFETY sensor: {sensor_desc.key}"

    # Gen4 vehicles should have all API_GEN_2_SENSORS
    for sensor_desc in API_GEN_2_SENSORS:
        entity_id = entity_registry.async_get_entity_id(
            SENSOR_DOMAIN, SUBARU_DOMAIN, f"{TEST_VIN_4_G4}_{sensor_desc.key}"
        )
        assert entity_id is not None, f"Missing API_GEN_2 sensor: {sensor_desc.key}"

    # Gen4 vehicles should have all API_GEN_3_SENSORS
    for sensor_desc in API_GEN_3_SENSORS:
        entity_id = entity_registry.async_get_entity_id(
            SENSOR_DOMAIN, SUBARU_DOMAIN, f"{TEST_VIN_4_G4}_{sensor_desc.key}"
        )
        assert entity_id is not None, f"Missing API_GEN_3 sensor: {sensor_desc.key}"

    # Gen4 vehicles should have TPMS_SENSORS if vehicle has TPMS
    if VEHICLE_DATA[TEST_VIN_4_G4][VEHICLE_HAS_TPMS]:
        for sensor_desc in TPMS_SENSORS:
            entity_id = entity_registry.async_get_entity_id(
                SENSOR_DOMAIN, SUBARU_DOMAIN, f"{TEST_VIN_4_G4}_{sensor_desc.key}"
            )
            assert entity_id is not None, f"Missing TPMS sensor: {sensor_desc.key}"


def _assert_data(hass: HomeAssistant, expected_state: dict[str, Any]) -> None:
    sensor_list = []
    sensor_list.extend(EV_SENSORS)
    sensor_list.extend(API_GEN_2_SENSORS)
    sensor_list.extend(SAFETY_SENSORS)
    expected_states = {}
    entity_registry = er.async_get(hass)
    for item in sensor_list:
        entity = entity_registry.async_get_entity_id(
            SENSOR_DOMAIN, SUBARU_DOMAIN, f"{TEST_VIN_2_EV}_{item.key}"
        )
        expected_states[entity] = expected_state[item.key]

    for sensor, value in expected_states.items():
        actual = hass.states.get(sensor)
        assert actual.state == str(value)
