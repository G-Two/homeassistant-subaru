"""Test Subaru buttons."""

from unittest.mock import patch

from pytest import raises
from subarulink import InvalidPIN

from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.exceptions import HomeAssistantError

from .api_responses import VEHICLE_STATUS_EV
from .conftest import (
    MOCK_API_FETCH,
    MOCK_API_GET_DATA,
    MOCK_API_LIGHTS,
    MOCK_API_REMOTE_START,
    MOCK_API_UPDATE,
)

REMOTE_START_BUTTON = "button.test_vehicle_2_remote_start"
REMOTE_LIGHTS_BUTTON = "button.test_vehicle_2_lights_start"
REMOTE_START_BUTTON = "button.test_vehicle_2_remote_start"
REMOTE_REFRESH_BUTTON = "button.test_vehicle_2_refresh"
REMOTE_POLL_VEHICLE_BUTTON = "button.test_vehicle_2_poll_vehicle"


async def test_device_exists(hass, ev_entry):
    """Test subaru button entity exists."""
    entity_registry = hass.helpers.entity_registry.async_get(hass)
    entry = entity_registry.async_get(REMOTE_START_BUTTON)
    assert entry


async def test_button_with_fetch(hass, ev_entry):
    """Test subaru button function."""
    with (
        patch(MOCK_API_REMOTE_START) as mock_remote_start,
        patch(MOCK_API_FETCH) as mock_fetch,
    ):
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


async def test_button_update(hass, ev_entry):
    """Test subaru fetch button function."""
    with (
        patch(MOCK_API_FETCH),
        patch(MOCK_API_GET_DATA, return_value=VEHICLE_STATUS_EV),
        patch(MOCK_API_UPDATE, return_value=True) as mock_update,
    ):
        await hass.services.async_call(
            BUTTON_DOMAIN,
            "press",
            {ATTR_ENTITY_ID: REMOTE_POLL_VEHICLE_BUTTON},
            blocking=True,
        )
        await hass.async_block_till_done()
        mock_update.assert_called_once()


async def test_button_fetch(hass, ev_entry):
    """Test subaru fetch button function."""
    with patch(MOCK_API_FETCH) as mock_fetch:
        await hass.services.async_call(
            BUTTON_DOMAIN,
            "press",
            {ATTR_ENTITY_ID: REMOTE_REFRESH_BUTTON},
            blocking=True,
        )
        await hass.async_block_till_done()
        mock_fetch.assert_called_once()


async def test_button_remote_start(hass, ev_entry):
    """Test subaru remote start button function."""
    with (
        patch(MOCK_API_REMOTE_START) as mock_remote_start,
        patch(MOCK_API_FETCH) as mock_fetch,
    ):
        await hass.services.async_call(
            BUTTON_DOMAIN,
            "press",
            {ATTR_ENTITY_ID: REMOTE_START_BUTTON},
            blocking=True,
        )
        await hass.async_block_till_done()
        mock_remote_start.assert_called_once()
        mock_fetch.assert_called()


async def test_button_remote_start_failed(hass, ev_entry):
    """Test subaru remote start button function."""
    with (
        patch(MOCK_API_REMOTE_START, return_value=False) as mock_remote_start,
        patch(MOCK_API_FETCH) as mock_fetch,
    ):
        with raises(HomeAssistantError):
            await hass.services.async_call(
                BUTTON_DOMAIN,
                "press",
                {ATTR_ENTITY_ID: REMOTE_START_BUTTON},
                blocking=True,
            )
            await hass.async_block_till_done()
            mock_remote_start.assert_called_once()
            mock_fetch.assert_called()


async def test_button_invalid_pin(hass, ev_entry):
    """Test remote button with invalid PIN."""
    with patch(
        MOCK_API_LIGHTS,
        side_effect=InvalidPIN("invalid PIN"),
    ) as mock_horn:
        with raises(HomeAssistantError):
            await hass.services.async_call(
                BUTTON_DOMAIN,
                "press",
                {ATTR_ENTITY_ID: REMOTE_LIGHTS_BUTTON},
                blocking=True,
            )
            await hass.async_block_till_done()
            mock_horn.assert_called_once()
