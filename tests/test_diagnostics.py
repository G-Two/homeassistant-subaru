"""Test Subaru diagnostics."""
import json

import pytest
from pytest_homeassistant_custom_component.common import load_fixture

from custom_components.subaru.const import DOMAIN, ENTRY_COORDINATOR
from custom_components.subaru.diagnostics import (
    async_get_config_entry_diagnostics,
    async_get_device_diagnostics,
)
from homeassistant.core import HomeAssistant, HomeAssistantError
from homeassistant.helpers import device_registry as dr

from .api_responses import TEST_VIN_2_EV


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

    expected = json.loads(load_fixture("diagnostics_device.json"))

    result = await async_get_device_diagnostics(hass, config_entry, reg_device)
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

    # Remove vehicle info from hass.data so that vehicle will not be found
    hass.data[DOMAIN][config_entry.entry_id][ENTRY_COORDINATOR].data.pop(TEST_VIN_2_EV)

    with pytest.raises(HomeAssistantError):
        await async_get_device_diagnostics(hass, config_entry, reg_device)
