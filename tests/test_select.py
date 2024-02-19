"""Test Subaru select."""

import pytest

from custom_components.subaru.const import DOMAIN as SUBARU_DOMAIN
from custom_components.subaru.select import CLIMATE_SELECT, OLD_CLIMATE_SELECT
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, ATTR_OPTION, SERVICE_SELECT_OPTION

from .api_responses import TEST_VIN_2_EV
from .conftest import migrate_unique_ids, migrate_unique_ids_duplicate

DEVICE_ID = "select.test_vehicle_2_climate_preset"


async def test_device_exists(hass, ev_entry):
    """Test subaru select entity exists."""
    entity_registry = hass.helpers.entity_registry.async_get(hass)
    entry = entity_registry.async_get(DEVICE_ID)
    assert entry
    await hass.async_block_till_done()


async def test_select(hass, ev_entry_with_saved_climate):
    """Test subaru select function."""
    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {ATTR_ENTITY_ID: DEVICE_ID, ATTR_OPTION: "Full Heat"},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert hass.states.get(DEVICE_ID).state == "Full Heat"


@pytest.mark.parametrize(
    "entitydata,old_unique_id,new_unique_id",
    [
        (
            {
                "domain": SELECT_DOMAIN,
                "platform": SUBARU_DOMAIN,
                "unique_id": f"{TEST_VIN_2_EV}_{OLD_CLIMATE_SELECT.name}",
            },
            f"{TEST_VIN_2_EV}_{OLD_CLIMATE_SELECT.name}",
            f"{TEST_VIN_2_EV}_{CLIMATE_SELECT.key}",
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
                "domain": SELECT_DOMAIN,
                "platform": SUBARU_DOMAIN,
                "unique_id": f"{TEST_VIN_2_EV}_{OLD_CLIMATE_SELECT.name}",
            },
            f"{TEST_VIN_2_EV}_{OLD_CLIMATE_SELECT.name}",
            f"{TEST_VIN_2_EV}_{CLIMATE_SELECT.key}",
        ),
    ],
)
async def test_binary_sensor_migrate_unique_ids_duplicate(
    hass, entitydata, old_unique_id, new_unique_id, subaru_config_entry
) -> None:
    """Test unsuccessful migration of entity unique_ids due to duplicate."""
    await migrate_unique_ids_duplicate(
        hass, entitydata, old_unique_id, new_unique_id, subaru_config_entry
    )
