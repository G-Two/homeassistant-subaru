"""Test Subaru component services."""
from unittest.mock import patch

from pytest import raises
from subarulink import InvalidPIN

from custom_components.subaru_hacs.const import (
    DOMAIN,
    REMOTE_SERVICE_FETCH,
    REMOTE_SERVICE_HORN,
    REMOTE_SERVICE_UPDATE,
    VEHICLE_VIN,
)
from homeassistant.exceptions import HomeAssistantError

from .api_responses import TEST_VIN_2_EV, TEST_VIN_3_G2, VEHICLE_STATUS_EV

from tests.conftest import MOCK_API, MOCK_API_FETCH, MOCK_API_GET_DATA, MOCK_API_UPDATE

MOCK_API_HORN = f"{MOCK_API}horn"


async def test_remote_service_horn(hass, ev_entry):
    """Test remote service horn."""
    with patch(MOCK_API_HORN) as mock_horn:
        await hass.services.async_call(
            DOMAIN, REMOTE_SERVICE_HORN, {VEHICLE_VIN: TEST_VIN_2_EV}, blocking=True,
        )
        await hass.async_block_till_done()
        mock_horn.assert_called_once()


async def test_remote_service_fetch(hass, ev_entry):
    """Test remote service fetch."""
    with patch(MOCK_API_GET_DATA, return_value=VEHICLE_STATUS_EV), patch(
        MOCK_API_FETCH
    ) as mock_fetch:
        await hass.services.async_call(
            DOMAIN, REMOTE_SERVICE_FETCH, {VEHICLE_VIN: TEST_VIN_2_EV}, blocking=True,
        )
        await hass.async_block_till_done()
        mock_fetch.assert_called_once()


async def test_remote_service_update(hass, ev_entry):
    """Test remote service update."""
    with patch(MOCK_API_FETCH), patch(
        MOCK_API_GET_DATA, return_value=VEHICLE_STATUS_EV
    ), patch(MOCK_API_UPDATE, return_value=True) as mock_update:
        await hass.services.async_call(
            DOMAIN, REMOTE_SERVICE_UPDATE, {VEHICLE_VIN: TEST_VIN_2_EV}, blocking=True,
        )
        await hass.async_block_till_done()
        mock_update.assert_called_once()


async def test_remote_service_invalid_vin(hass, ev_entry):
    """Test remote service request with invalid VIN."""
    with patch(MOCK_API_HORN) as mock_horn:
        with raises(HomeAssistantError):
            await hass.services.async_call(
                DOMAIN,
                REMOTE_SERVICE_HORN,
                {VEHICLE_VIN: TEST_VIN_3_G2},
                blocking=True,
            )
            await hass.async_block_till_done()
            mock_horn.assert_not_called()


async def test_remote_service_invalid_pin(hass, ev_entry):
    """Test remote service request with invalid PIN."""
    with patch(MOCK_API_HORN, side_effect=InvalidPIN("invalid PIN"),) as mock_horn:
        with raises(HomeAssistantError):
            await hass.services.async_call(
                DOMAIN,
                REMOTE_SERVICE_HORN,
                {VEHICLE_VIN: TEST_VIN_2_EV},
                blocking=True,
            )
            await hass.async_block_till_done()
            mock_horn.assert_called_once()


async def test_remote_service_fails(hass, ev_entry):
    """Test remote service request that initiates but fails."""
    with patch(MOCK_API_HORN, return_value=False) as mock_horn:
        with raises(HomeAssistantError):
            await hass.services.async_call(
                DOMAIN,
                REMOTE_SERVICE_HORN,
                {VEHICLE_VIN: TEST_VIN_2_EV},
                blocking=True,
            )
            await hass.async_block_till_done()
            mock_horn.assert_called_once()
