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

from .api_responses import TEST_VIN_2_EV, TEST_VIN_3_G2, VEHICLE_DATA
from .common import setup_subaru_integration


async def test_remote_service_horn(hass):
    """Test remote service horn."""
    entry = await setup_subaru_integration(
        hass, vehicle_list=[TEST_VIN_2_EV], vehicle_data=VEHICLE_DATA[TEST_VIN_2_EV]
    )
    assert hass.data[DOMAIN][entry.entry_id]

    with patch("custom_components.subaru.SubaruAPI.horn") as mock_horn:
        await hass.services.async_call(
            DOMAIN, REMOTE_SERVICE_HORN, {VEHICLE_VIN: TEST_VIN_2_EV}, blocking=True,
        )
        await hass.async_block_till_done()
        mock_horn.assert_called_once()


async def test_remote_service_fetch(hass):
    """Test remote service fetch."""
    entry = await setup_subaru_integration(
        hass, vehicle_list=[TEST_VIN_2_EV], vehicle_data=VEHICLE_DATA[TEST_VIN_2_EV]
    )
    assert hass.data[DOMAIN][entry.entry_id]

    with patch("custom_components.subaru.SubaruAPI.fetch") as mock_fetch:
        await hass.services.async_call(
            DOMAIN, REMOTE_SERVICE_FETCH, {VEHICLE_VIN: TEST_VIN_2_EV}, blocking=True,
        )
        await hass.async_block_till_done()
        mock_fetch.assert_called_once()


async def test_remote_service_update(hass):
    """Test remote service update."""
    entry = await setup_subaru_integration(
        hass, vehicle_list=[TEST_VIN_2_EV], vehicle_data=VEHICLE_DATA[TEST_VIN_2_EV]
    )
    assert hass.data[DOMAIN][entry.entry_id]

    with patch("custom_components.subaru.SubaruAPI.update") as mock_update:
        await hass.services.async_call(
            DOMAIN, REMOTE_SERVICE_UPDATE, {VEHICLE_VIN: TEST_VIN_2_EV}, blocking=True,
        )
        await hass.async_block_till_done()
        mock_update.assert_called_once()


async def test_remote_service_invalid_vin(hass):
    """Test remote service request with invalid VIN."""
    entry = await setup_subaru_integration(
        hass, vehicle_list=[TEST_VIN_2_EV], vehicle_data=VEHICLE_DATA[TEST_VIN_2_EV]
    )
    assert hass.data[DOMAIN][entry.entry_id]

    with patch("custom_components.subaru.SubaruAPI.horn") as mock_horn:
        await hass.services.async_call(
            DOMAIN, REMOTE_SERVICE_HORN, {VEHICLE_VIN: TEST_VIN_3_G2}, blocking=True,
        )
        await hass.async_block_till_done()
        mock_horn.assert_not_called()


async def test_remote_service_invalid_pin(hass):
    """Test remote service request with invalid PIN."""
    entry = await setup_subaru_integration(
        hass, vehicle_list=[TEST_VIN_2_EV], vehicle_data=VEHICLE_DATA[TEST_VIN_2_EV]
    )
    assert hass.data[DOMAIN][entry.entry_id]

    with patch(
        "custom_components.subaru.SubaruAPI.horn",
        side_effect=InvalidPIN("invalid PIN"),
    ) as mock_horn:
        await hass.services.async_call(
            DOMAIN, REMOTE_SERVICE_HORN, {VEHICLE_VIN: TEST_VIN_2_EV}, blocking=True,
        )
        await hass.async_block_till_done()
        mock_horn.assert_called_once()


async def test_remote_service_fails(hass):
    """Test remote service request that initiates but fails."""
    entry = await setup_subaru_integration(
        hass, vehicle_list=[TEST_VIN_2_EV], vehicle_data=VEHICLE_DATA[TEST_VIN_2_EV]
    )
    assert hass.data[DOMAIN][entry.entry_id]

    with patch(
        "custom_components.subaru.SubaruAPI.horn", return_value=False
    ) as mock_horn:
        await hass.services.async_call(
            DOMAIN, REMOTE_SERVICE_HORN, {VEHICLE_VIN: TEST_VIN_2_EV}, blocking=True,
        )
        await hass.async_block_till_done()
        mock_horn.assert_called_once()
