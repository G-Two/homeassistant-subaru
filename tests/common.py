"""Common functions needed to setup tests for Subaru component."""
from datetime import datetime

from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_PASSWORD,
    CONF_PIN,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)
from homeassistant.setup import async_setup_component
import pytest
from pytest_homeassistant_custom_component.async_mock import patch
from pytest_homeassistant_custom_component.common import MockConfigEntry
from subarulink import InvalidCredentials

from custom_components.subaru.const import (
    CONF_HARD_POLL_INTERVAL,
    DEFAULT_HARD_POLL_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    VEHICLE_API_GEN,
    VEHICLE_HAS_EV,
    VEHICLE_HAS_REMOTE_SERVICE,
    VEHICLE_HAS_REMOTE_START,
    VEHICLE_HAS_SAFETY_SERVICE,
    VEHICLE_NAME,
)

from tests.api_responses import TEST_VIN_2_EV, VEHICLE_DATA, VEHICLE_STATUS_EV

TEST_CONFIG = {
    CONF_USERNAME: "user",
    CONF_PASSWORD: "password",
    CONF_PIN: "1234",
    CONF_DEVICE_ID: int(datetime.now().timestamp()),
}

TEST_OPTIONS = {
    CONF_HARD_POLL_INTERVAL: DEFAULT_HARD_POLL_INTERVAL,
    CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
}


async def setup_subaru_integration(
    hass,
    vehicle_list=None,
    vehicle_data=None,
    vehicle_status=None,
    connect_success=True,
):
    """Create Subaru entry."""
    assert await async_setup_component(hass, DOMAIN, {})

    config_entry = MockConfigEntry(
        domain=DOMAIN, data=TEST_CONFIG, options=TEST_OPTIONS, entry_id=1,
    )
    config_entry.add_to_hass(hass)

    with patch(
        "custom_components.subaru.SubaruAPI.connect",
        return_value=connect_success,
        side_effect=None
        if connect_success
        else InvalidCredentials("Invalid Credentials"),
    ), patch(
        "custom_components.subaru.SubaruAPI.get_vehicles", return_value=vehicle_list,
    ), patch(
        "custom_components.subaru.SubaruAPI.vin_to_name",
        return_value=vehicle_data[VEHICLE_NAME],
    ), patch(
        "custom_components.subaru.SubaruAPI.get_api_gen",
        return_value=vehicle_data[VEHICLE_API_GEN],
    ), patch(
        "custom_components.subaru.SubaruAPI.get_ev_status",
        return_value=vehicle_data[VEHICLE_HAS_EV],
    ), patch(
        "custom_components.subaru.SubaruAPI.get_res_status",
        return_value=vehicle_data[VEHICLE_HAS_REMOTE_START],
    ), patch(
        "custom_components.subaru.SubaruAPI.get_remote_status",
        return_value=vehicle_data[VEHICLE_HAS_REMOTE_SERVICE],
    ), patch(
        "custom_components.subaru.SubaruAPI.get_safety_status",
        return_value=vehicle_data[VEHICLE_HAS_SAFETY_SERVICE],
    ), patch(
        "custom_components.subaru.SubaruAPI.get_data", return_value=vehicle_status,
    ), patch(
        "custom_components.subaru.SubaruAPI.update",
    ), patch(
        "custom_components.subaru.SubaruAPI.fetch",
    ):
        success = await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    if success:
        return config_entry
    return None


@pytest.fixture
async def ev_entry(hass):
    """Create a Subaru entry representing an EV vehicle with full STARLINK subscription."""
    entry = await setup_subaru_integration(
        hass,
        vehicle_list=[TEST_VIN_2_EV],
        vehicle_data=VEHICLE_DATA[TEST_VIN_2_EV],
        vehicle_status=VEHICLE_STATUS_EV,
    )
    assert hass.data[DOMAIN][entry.entry_id]
    return entry
