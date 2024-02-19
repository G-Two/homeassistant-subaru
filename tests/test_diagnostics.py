"""Test Subaru diagnostics."""

import json
from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import load_fixture

from custom_components.subaru.const import DOMAIN, FETCH_INTERVAL
from custom_components.subaru.diagnostics import (
    async_get_config_entry_diagnostics,
    async_get_device_diagnostics,
)
from homeassistant.core import HomeAssistant, HomeAssistantError
from homeassistant.helpers import device_registry as dr

from .api_responses import TEST_VIN_2_EV
from .conftest import (
    MOCK_API_FETCH,
    MOCK_API_GET_DATA,
    MOCK_API_GET_RAW_DATA,
    advance_time,
)


async def test_config_entry_diagnostics(hass: HomeAssistant, ev_entry):
    """Test config entry diagnostics."""
    assert hass.data[DOMAIN]

    config_entry = hass.config_entries.async_entries(DOMAIN)[0]

    expected = json.loads(load_fixture("diagnostics_config_entry.json"))

    result = await async_get_config_entry_diagnostics(hass, config_entry)
    assert json.dumps(expected) == json.dumps(result, default=str)


async def test_device_diagnostics(hass: HomeAssistant, hass_client, ev_entry):
    """Test device diagnostics."""
    assert hass.data[DOMAIN]

    config_entry = hass.config_entries.async_entries(DOMAIN)[0]

    device_registry = dr.async_get(hass)
    reg_device = device_registry.async_get_device(
        identifiers={(DOMAIN, TEST_VIN_2_EV)},
    )
    assert reg_device is not None

    raw_data = json.loads(load_fixture("raw_api_data.json"))
    with patch(MOCK_API_GET_RAW_DATA, return_value=raw_data) as mock_get_raw_data:
        expected = json.loads(load_fixture("diagnostics_device.json"))
        result = await async_get_device_diagnostics(hass, config_entry, reg_device)
        mock_get_raw_data.assert_called_once()
    assert json.dumps(expected) == json.dumps(result, default=str)


async def test_device_diagnostics_vehicle_not_found(
    hass: HomeAssistant, hass_client, ev_entry
):
    """Test device diagnostics when the vehicle cannot be found."""
    assert hass.data[DOMAIN]

    config_entry = hass.config_entries.async_entries(DOMAIN)[0]

    device_registry = dr.async_get(hass)
    reg_device = device_registry.async_get_device(
        identifiers={(DOMAIN, TEST_VIN_2_EV)},
    )
    assert reg_device is not None

    # Simulate case where Subaru API does not return vehicle data
    with patch(MOCK_API_FETCH), patch(MOCK_API_GET_DATA, return_value=None):
        advance_time(hass, FETCH_INTERVAL)
        await hass.async_block_till_done()

    with pytest.raises(HomeAssistantError):
        await async_get_device_diagnostics(hass, config_entry, reg_device)
