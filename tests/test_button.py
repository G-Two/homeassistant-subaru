"""Test Subaru buttons."""

from unittest.mock import patch

from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID

from .conftest import MOCK_API_FETCH, MOCK_API_LIGHTS, MOCK_API_REMOTE_START

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
