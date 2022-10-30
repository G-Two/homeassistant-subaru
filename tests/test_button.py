"""Test Subaru buttons."""
from unittest.mock import patch

import pytest

from custom_components.subaru.button import G1_REMOTE_BUTTONS
from custom_components.subaru.const import DOMAIN as SUBARU_DOMAIN
from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID

from .api_responses import TEST_VIN_2_EV
from .conftest import (
    MOCK_API_FETCH,
    MOCK_API_LIGHTS,
    MOCK_API_REMOTE_START,
    migrate_unique_ids,
    migrate_unique_ids_duplicate,
)

REMOTE_START_BUTTON = "button.test_vehicle_2_remote_start"
REMOTE_LIGHTS_BUTTON = "button.test_vehicle_2_lights_start"
REMOTE_REFRESH_BUTTON = "button.test_vehicle_2_refresh"


async def test_device_exists(hass, ev_entry):
    """Test subaru button entity exists."""
    entity_registry = hass.helpers.entity_registry.async_get(hass)
    entry = entity_registry.async_get(REMOTE_START_BUTTON)
    assert entry


async def test_button_with_fetch(hass, ev_entry):
    """Test subaru button function."""
    with patch(MOCK_API_REMOTE_START) as mock_remote_start, patch(
        MOCK_API_FETCH
    ) as mock_fetch:
        await hass.services.async_call(
            BUTTON_DOMAIN, "press", {ATTR_ENTITY_ID: REMOTE_START_BUTTON}, blocking=True
        )
        await hass.async_block_till_done()
        mock_remote_start.assert_called_once()
        mock_fetch.assert_called_once()


async def test_button_without_fetch(hass, ev_entry):
    """Test subaru button function."""
    with patch(MOCK_API_LIGHTS) as mock_lights, patch(MOCK_API_FETCH) as mock_fetch:
        await hass.services.async_call(
            BUTTON_DOMAIN,
            "press",
            {ATTR_ENTITY_ID: REMOTE_LIGHTS_BUTTON},
            blocking=True,
        )
        await hass.async_block_till_done()
        mock_lights.assert_called_once()
        mock_fetch.assert_not_called()


async def test_button_fetch(hass, ev_entry):
    """Test subaru button function."""
    with patch(MOCK_API_FETCH) as mock_fetch:
        await hass.services.async_call(
            BUTTON_DOMAIN,
            "press",
            {ATTR_ENTITY_ID: REMOTE_REFRESH_BUTTON},
            blocking=True,
        )
        await hass.async_block_till_done()
        mock_fetch.assert_called_once()


@pytest.mark.parametrize(
    "entitydata,old_unique_id,new_unique_id",
    [
        (
            {
                "domain": BUTTON_DOMAIN,
                "platform": SUBARU_DOMAIN,
                "unique_id": f"{TEST_VIN_2_EV}_{G1_REMOTE_BUTTONS[0].name}",
            },
            f"{TEST_VIN_2_EV}_{G1_REMOTE_BUTTONS[0].name}",
            f"{TEST_VIN_2_EV}_{G1_REMOTE_BUTTONS[0].key}",
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
                "domain": BUTTON_DOMAIN,
                "platform": SUBARU_DOMAIN,
                "unique_id": f"{TEST_VIN_2_EV}_{G1_REMOTE_BUTTONS[0].name}",
            },
            f"{TEST_VIN_2_EV}_{G1_REMOTE_BUTTONS[0].name}",
            f"{TEST_VIN_2_EV}_{G1_REMOTE_BUTTONS[0].key}",
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
