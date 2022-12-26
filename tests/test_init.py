"""Test Subaru component setup and updates."""
from unittest.mock import patch

from subarulink import InvalidCredentials, SubaruException

from custom_components.subaru.const import DOMAIN, UPDATE_INTERVAL_CHARGING
from homeassistant.components.homeassistant import (
    DOMAIN as HA_DOMAIN,
    SERVICE_UPDATE_ENTITY,
)
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import ATTR_ENTITY_ID, STATE_OFF, STATE_ON
from homeassistant.setup import async_setup_component

from .api_responses import (
    TEST_VIN_1_G1,
    TEST_VIN_2_EV,
    TEST_VIN_3_G3,
    VEHICLE_DATA,
    VEHICLE_STATUS_EV,
    VEHICLE_STATUS_G3,
)
from .conftest import (
    MOCK_API_FETCH,
    MOCK_API_GET_DATA,
    MOCK_API_UPDATE,
    TEST_ENTITY_ID,
    advance_time,
    setup_subaru_config_entry,
)


async def test_setup_with_no_config(hass, enable_custom_integrations):
    """Test DOMAIN is empty if there is no config."""
    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()
    assert DOMAIN not in hass.config_entries.async_domains()


async def test_setup_ev(hass, ev_entry):
    """Test setup with an EV vehicle."""
    check_entry = hass.config_entries.async_get_entry(ev_entry.entry_id)
    assert check_entry
    assert check_entry.state is ConfigEntryState.LOADED


async def test_setup_g3(hass, subaru_config_entry, enable_custom_integrations):
    """Test setup with a G3 vehicle ."""
    await setup_subaru_config_entry(
        hass,
        subaru_config_entry,
        vehicle_list=[TEST_VIN_3_G3],
        vehicle_data=VEHICLE_DATA[TEST_VIN_3_G3],
        vehicle_status=VEHICLE_STATUS_G3,
    )
    check_entry = hass.config_entries.async_get_entry(subaru_config_entry.entry_id)
    assert check_entry
    assert check_entry.state is ConfigEntryState.LOADED


async def test_setup_g1(hass, subaru_config_entry, enable_custom_integrations):
    """Test setup with a G1 vehicle."""
    await setup_subaru_config_entry(
        hass,
        subaru_config_entry,
        vehicle_list=[TEST_VIN_1_G1],
        vehicle_data=VEHICLE_DATA[TEST_VIN_1_G1],
    )
    check_entry = hass.config_entries.async_get_entry(subaru_config_entry.entry_id)
    assert check_entry
    assert check_entry.state is ConfigEntryState.LOADED


async def test_unsuccessful_connect(
    hass, subaru_config_entry, enable_custom_integrations
):
    """Test unsuccessful connect due to connectivity."""
    await setup_subaru_config_entry(
        hass,
        subaru_config_entry,
        connect_effect=SubaruException("Service Unavailable"),
        vehicle_list=[TEST_VIN_2_EV],
        vehicle_data=VEHICLE_DATA[TEST_VIN_2_EV],
        vehicle_status=VEHICLE_STATUS_EV,
    )
    check_entry = hass.config_entries.async_get_entry(subaru_config_entry.entry_id)
    assert check_entry
    assert check_entry.state is ConfigEntryState.SETUP_RETRY


async def test_invalid_credentials(
    hass, subaru_config_entry, enable_custom_integrations
):
    """Test invalid credentials."""
    await setup_subaru_config_entry(
        hass,
        subaru_config_entry,
        connect_effect=InvalidCredentials("Invalid Credentials"),
        vehicle_list=[TEST_VIN_2_EV],
        vehicle_data=VEHICLE_DATA[TEST_VIN_2_EV],
        vehicle_status=VEHICLE_STATUS_EV,
    )
    check_entry = hass.config_entries.async_get_entry(subaru_config_entry.entry_id)
    assert check_entry
    assert check_entry.state is ConfigEntryState.SETUP_ERROR


async def test_update_skip_unsubscribed(
    hass, subaru_config_entry, enable_custom_integrations
):
    """Test update function skips vehicles without subscription."""
    await setup_subaru_config_entry(
        hass,
        subaru_config_entry,
        vehicle_list=[TEST_VIN_1_G1],
        vehicle_data=VEHICLE_DATA[TEST_VIN_1_G1],
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


async def test_fetch_failed(hass, subaru_config_entry, enable_custom_integrations):
    """Tests when fetch fails."""
    await setup_subaru_config_entry(
        hass,
        subaru_config_entry,
        vehicle_list=[TEST_VIN_2_EV],
        vehicle_data=VEHICLE_DATA[TEST_VIN_2_EV],
        vehicle_status=VEHICLE_STATUS_EV,
        fetch_effect=SubaruException("403 Error"),
    )

    test_entity = hass.states.get(TEST_ENTITY_ID)
    assert test_entity.state == "unavailable"


async def test_unload_entry(hass, ev_entry):
    """Test that entry is unloaded."""
    assert ev_entry.state is ConfigEntryState.LOADED
    assert await hass.config_entries.async_unload(ev_entry.entry_id)
    await hass.async_block_till_done()
    assert ev_entry.state is ConfigEntryState.NOT_LOADED


async def test_charging_polling(hass, ev_entry_charge_polling):
    """Test charging polling option."""
    hass.states.async_set(
        "binary_sensor.test_vehicle_2_ev_battery_charging", STATE_OFF, force_update=True
    )

    with patch(MOCK_API_UPDATE, return_value=True) as mock_update, patch(
        MOCK_API_GET_DATA, return_value=VEHICLE_STATUS_EV
    ) as mock_get_data:
        # Charging state is off, so update shouldn't happen, but state will be updated by get_data
        assert (
            hass.states.get("binary_sensor.test_vehicle_2_ev_battery_charging").state
            == STATE_OFF
        )
        advance_time(hass, UPDATE_INTERVAL_CHARGING)
        await hass.async_block_till_done()
        mock_update.assert_not_called()
        mock_get_data.assert_called_once()
        assert (
            hass.states.get("binary_sensor.test_vehicle_2_ev_battery_charging").state
            == STATE_ON
        )

        # Charging state is now on, so update should hppen
        advance_time(hass, UPDATE_INTERVAL_CHARGING)
        await hass.async_block_till_done()
        mock_update.assert_called_once()
