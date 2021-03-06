"""Test Subaru component setup and updates."""
from unittest.mock import patch

from subarulink import InvalidCredentials, SubaruException

from custom_components.subaru_hacs.const import DOMAIN
from homeassistant.components.homeassistant import (
    DOMAIN as HA_DOMAIN,
    SERVICE_UPDATE_ENTITY,
)
from homeassistant.config_entries import (
    ENTRY_STATE_LOADED,
    ENTRY_STATE_NOT_LOADED,
    ENTRY_STATE_SETUP_ERROR,
    ENTRY_STATE_SETUP_RETRY,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.setup import async_setup_component

from .api_responses import (
    TEST_VIN_1_G1,
    TEST_VIN_2_EV,
    TEST_VIN_3_G2,
    VEHICLE_DATA,
    VEHICLE_STATUS_EV,
    VEHICLE_STATUS_G2,
)
from .conftest import (
    MOCK_API_FETCH,
    MOCK_API_UPDATE,
    TEST_ENTITY_ID,
    setup_subaru_integration,
)


async def test_setup_with_no_config(hass):
    """Test DOMAIN is empty if there is no config."""
    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()
    assert DOMAIN not in hass.config_entries.async_domains()


async def test_setup_ev(hass, ev_entry):
    """Test setup with an EV vehicle."""
    check_entry = hass.config_entries.async_get_entry(ev_entry.entry_id)
    assert check_entry
    assert check_entry.state == ENTRY_STATE_LOADED


async def test_setup_g2(hass):
    """Test setup with a G2 vehicle ."""
    entry = await setup_subaru_integration(
        hass,
        vehicle_list=[TEST_VIN_3_G2],
        vehicle_data=VEHICLE_DATA[TEST_VIN_3_G2],
        vehicle_status=VEHICLE_STATUS_G2,
    )
    check_entry = hass.config_entries.async_get_entry(entry.entry_id)
    assert check_entry
    assert check_entry.state == ENTRY_STATE_LOADED


async def test_setup_g1(hass):
    """Test setup with a G1 vehicle."""
    entry = await setup_subaru_integration(
        hass, vehicle_list=[TEST_VIN_1_G1], vehicle_data=VEHICLE_DATA[TEST_VIN_1_G1]
    )
    check_entry = hass.config_entries.async_get_entry(entry.entry_id)
    assert check_entry
    assert check_entry.state == ENTRY_STATE_LOADED


async def test_unsuccessful_connect(hass):
    """Test unsuccessful connect due to connectivity."""
    entry = await setup_subaru_integration(
        hass,
        connect_effect=SubaruException("Service Unavailable"),
        vehicle_list=[TEST_VIN_2_EV],
        vehicle_data=VEHICLE_DATA[TEST_VIN_2_EV],
        vehicle_status=VEHICLE_STATUS_EV,
    )
    check_entry = hass.config_entries.async_get_entry(entry.entry_id)
    assert check_entry
    assert check_entry.state == ENTRY_STATE_SETUP_RETRY


async def test_invalid_credentials(hass):
    """Test invalid credentials."""
    entry = await setup_subaru_integration(
        hass,
        connect_effect=InvalidCredentials("Invalid Credentials"),
        vehicle_list=[TEST_VIN_2_EV],
        vehicle_data=VEHICLE_DATA[TEST_VIN_2_EV],
        vehicle_status=VEHICLE_STATUS_EV,
    )
    check_entry = hass.config_entries.async_get_entry(entry.entry_id)
    assert check_entry
    assert check_entry.state == ENTRY_STATE_SETUP_ERROR


async def test_update_skip_unsubscribed(hass):
    """Test update function skips vehicles without subscription."""
    await setup_subaru_integration(
        hass, vehicle_list=[TEST_VIN_1_G1], vehicle_data=VEHICLE_DATA[TEST_VIN_1_G1]
    )
    with patch(MOCK_API_FETCH) as mock_fetch:
        await hass.services.async_call(
            HA_DOMAIN,
            SERVICE_UPDATE_ENTITY,
            {ATTR_ENTITY_ID: TEST_ENTITY_ID},
            blocking=True,
        )

        await hass.async_block_till_done()
        mock_fetch.assert_not_called()


async def test_update_disabled(hass, ev_entry):
    """Test update function disable option."""
    with patch(MOCK_API_FETCH, side_effect=SubaruException("403 Error"),), patch(
        MOCK_API_UPDATE,
    ) as mock_update:
        await hass.services.async_call(
            HA_DOMAIN,
            SERVICE_UPDATE_ENTITY,
            {ATTR_ENTITY_ID: TEST_ENTITY_ID},
            blocking=True,
        )
        await hass.async_block_till_done()
        mock_update.assert_not_called()


async def test_fetch_failed(hass):
    """Tests when fetch fails."""
    await setup_subaru_integration(
        hass,
        vehicle_list=[TEST_VIN_2_EV],
        vehicle_data=VEHICLE_DATA[TEST_VIN_2_EV],
        vehicle_status=VEHICLE_STATUS_EV,
        fetch_effect=SubaruException("403 Error"),
    )

    test_entity = hass.states.get(TEST_ENTITY_ID)
    assert test_entity.state == "unavailable"


async def test_unload_entry(hass, ev_entry):
    """Test that entry is unloaded."""
    assert ev_entry.state == ENTRY_STATE_LOADED
    assert await hass.config_entries.async_unload(ev_entry.entry_id)
    await hass.async_block_till_done()
    assert ev_entry.state == ENTRY_STATE_NOT_LOADED
