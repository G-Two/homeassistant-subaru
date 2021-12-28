"""Test Subaru buttons."""

from unittest.mock import patch

from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID

from .conftest import MOCK_API

MOCK_API_REMOTE_START = f"{MOCK_API}remote_start"
DEVICE_ID = "button.test_vehicle_2_remote_start"


async def test_device_exists(hass, ev_entry):
    """Test subaru button entity exists."""
    entity_registry = await hass.helpers.entity_registry.async_get_registry()
    entry = entity_registry.async_get(DEVICE_ID)
    assert entry


async def test_button(hass, ev_entry):
    """Test subaru button function."""
    with patch(MOCK_API_REMOTE_START) as mock_remote_start:
        await hass.services.async_call(
            BUTTON_DOMAIN, "press", {ATTR_ENTITY_ID: DEVICE_ID}, blocking=True
        )
        await hass.async_block_till_done()
        mock_remote_start.assert_called_once()
