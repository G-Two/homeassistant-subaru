"""Test Subaru component services."""
from pytest_homeassistant_custom_component.async_mock import patch
from subarulink import InvalidPIN

from custom_components.subaru.const import (
    DOMAIN,
    REMOTE_SERVICE_FETCH,
    REMOTE_SERVICE_HORN,
    REMOTE_SERVICE_UPDATE,
    VEHICLE_VIN,
)

from .api_responses import TEST_VIN_2_EV, TEST_VIN_3_G2, VEHICLE_STATUS_EV
from .common import ev_entry


async def test_remote_service_horn(hass, ev_entry):
    """Test remote service horn."""
    with patch("custom_components.subaru.SubaruAPI.horn") as mock_horn:
        await hass.services.async_call(
            DOMAIN, REMOTE_SERVICE_HORN, {VEHICLE_VIN: TEST_VIN_2_EV}, blocking=True,
        )
        await hass.async_block_till_done()
        mock_horn.assert_called_once()


async def test_remote_service_fetch(hass, ev_entry):
    """Test remote service fetch."""
    with patch(
        "custom_components.subaru.SubaruAPI.get_data", return_value=VEHICLE_STATUS_EV
    ), patch("custom_components.subaru.SubaruAPI.fetch") as mock_fetch:
        await hass.services.async_call(
            DOMAIN, REMOTE_SERVICE_FETCH, {VEHICLE_VIN: TEST_VIN_2_EV}, blocking=True,
        )
        await hass.async_block_till_done()
        mock_fetch.assert_called_once()


async def test_remote_service_update(hass, ev_entry):
    """Test remote service update."""
    with patch("custom_components.subaru.SubaruAPI.fetch"), patch(
        "custom_components.subaru.SubaruAPI.get_data", return_value=VEHICLE_STATUS_EV
    ), patch(
        "custom_components.subaru.SubaruAPI.update", return_value=True
    ) as mock_update:
        await hass.services.async_call(
            DOMAIN, REMOTE_SERVICE_UPDATE, {VEHICLE_VIN: TEST_VIN_2_EV}, blocking=True,
        )
        await hass.async_block_till_done()
        mock_update.assert_called_once()


async def test_remote_service_invalid_vin(hass, ev_entry):
    """Test remote service request with invalid VIN."""
    with patch("custom_components.subaru.SubaruAPI.horn") as mock_horn:
        await hass.services.async_call(
            DOMAIN, REMOTE_SERVICE_HORN, {VEHICLE_VIN: TEST_VIN_3_G2}, blocking=True,
        )
        await hass.async_block_till_done()
        mock_horn.assert_not_called()


async def test_remote_service_invalid_pin(hass, ev_entry):
    """Test remote service request with invalid PIN."""
    with patch(
        "custom_components.subaru.SubaruAPI.horn",
        side_effect=InvalidPIN("invalid PIN"),
    ) as mock_horn:
        await hass.services.async_call(
            DOMAIN, REMOTE_SERVICE_HORN, {VEHICLE_VIN: TEST_VIN_2_EV}, blocking=True,
        )
        await hass.async_block_till_done()
        mock_horn.assert_called_once()


async def test_remote_service_fails(hass, ev_entry):
    """Test remote service request that initiates but fails."""
    with patch(
        "custom_components.subaru.SubaruAPI.horn", return_value=False
    ) as mock_horn:
        await hass.services.async_call(
            DOMAIN, REMOTE_SERVICE_HORN, {VEHICLE_VIN: TEST_VIN_2_EV}, blocking=True,
        )
        await hass.async_block_till_done()
        mock_horn.assert_called_once()
