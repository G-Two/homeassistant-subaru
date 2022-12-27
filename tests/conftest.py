"""Common functions needed to setup tests for Subaru component."""
from datetime import timedelta
from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
    mock_restore_cache,
)
from subarulink.const import COUNTRY_USA

from custom_components.subaru.const import (
    CONF_COUNTRY,
    CONF_NOTIFICATION_OPTION,
    CONF_POLLING_OPTION,
    DOMAIN,
    VEHICLE_API_GEN,
    VEHICLE_HAS_EV,
    VEHICLE_HAS_POWER_WINDOWS,
    VEHICLE_HAS_REMOTE_SERVICE,
    VEHICLE_HAS_REMOTE_START,
    VEHICLE_HAS_SAFETY_SERVICE,
    VEHICLE_HAS_SUNROOF,
    VEHICLE_MODEL_NAME,
    VEHICLE_MODEL_YEAR,
    VEHICLE_NAME,
)
from custom_components.subaru.options import NotificationOptions, PollingOptions
from homeassistant import config_entries
from homeassistant.components.homeassistant import DOMAIN as HA_DOMAIN
from homeassistant.const import CONF_DEVICE_ID, CONF_PASSWORD, CONF_PIN, CONF_USERNAME
from homeassistant.core import State
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component
import homeassistant.util.dt as dt_util

from tests.api_responses import TEST_VIN_2_EV, VEHICLE_DATA, VEHICLE_STATUS_EV

MOCK_API = "custom_components.subaru.SubaruAPI."
MOCK_API_CONNECT = f"{MOCK_API}connect"
MOCK_API_DEVICE_REGISTERED = f"{MOCK_API}device_registered"
MOCK_API_2FA_CONTACTS = f"{MOCK_API}contact_methods"
MOCK_API_2FA_REQUEST = f"{MOCK_API}request_auth_code"
MOCK_API_2FA_VERIFY = f"{MOCK_API}submit_auth_code"
MOCK_API_IS_PIN_REQUIRED = f"{MOCK_API}is_pin_required"
MOCK_API_TEST_PIN = f"{MOCK_API}test_pin"
MOCK_API_UPDATE_SAVED_PIN = f"{MOCK_API}update_saved_pin"
MOCK_API_GET_VEHICLES = f"{MOCK_API}get_vehicles"
MOCK_API_GET_MODEL_NAME = f"{MOCK_API}get_model_name"
MOCK_API_GET_MODEL_YEAR = f"{MOCK_API}get_model_year"
MOCK_API_VIN_TO_NAME = f"{MOCK_API}vin_to_name"
MOCK_API_GET_API_GEN = f"{MOCK_API}get_api_gen"
MOCK_API_GET_EV_STATUS = f"{MOCK_API}get_ev_status"
MOCK_API_GET_RES_STATUS = f"{MOCK_API}get_res_status"
MOCK_API_GET_REMOTE_STATUS = f"{MOCK_API}get_remote_status"
MOCK_API_GET_SAFETY_STATUS = f"{MOCK_API}get_safety_status"
MOCK_API_HAS_POWER_WINDOWS = f"{MOCK_API}has_power_windows"
MOCK_API_HAS_SUNROOF = f"{MOCK_API}has_sunroof"
MOCK_API_GET_DATA = f"{MOCK_API}get_data"
MOCK_API_UPDATE = f"{MOCK_API}update"
MOCK_API_FETCH = f"{MOCK_API}fetch"
MOCK_API_REMOTE_START = f"{MOCK_API}remote_start"
MOCK_API_LIGHTS = f"{MOCK_API}lights"
MOCK_API_GET_RAW_DATA = f"{MOCK_API}get_raw_data"

TEST_USERNAME = "user@email.com"
TEST_PASSWORD = "password"  # nosec
TEST_PIN = "1234"
TEST_DEVICE_ID = 1613183362
TEST_COUNTRY = COUNTRY_USA

TEST_CREDS = {
    CONF_USERNAME: TEST_USERNAME,
    CONF_PASSWORD: TEST_PASSWORD,
    CONF_COUNTRY: TEST_COUNTRY,
}

TEST_CONFIG = {
    CONF_USERNAME: TEST_USERNAME,
    CONF_PASSWORD: TEST_PASSWORD,
    CONF_COUNTRY: TEST_COUNTRY,
    CONF_PIN: TEST_PIN,
    CONF_DEVICE_ID: TEST_DEVICE_ID,
}

TEST_OPTIONS = {
    CONF_POLLING_OPTION: PollingOptions.ENABLE.value,
    CONF_NOTIFICATION_OPTION: NotificationOptions.SUCCESS.value,
}

TEST_CONFIG_ENTRY = {
    "entry_id": "1",
    "domain": DOMAIN,
    "title": TEST_CONFIG[CONF_USERNAME],
    "data": TEST_CONFIG,
    "options": TEST_OPTIONS,
    "source": config_entries.SOURCE_USER,
}

TEST_DEVICE_NAME = "test_vehicle_2"
TEST_ENTITY_ID = f"sensor.{TEST_DEVICE_NAME}_odometer"


def advance_time(hass, seconds):
    """Fast forward time."""
    future = dt_util.utcnow() + timedelta(seconds=seconds + 30)
    async_fire_time_changed(hass, future)


async def setup_subaru_config_entry(
    hass,
    config_entry,
    vehicle_list=None,
    vehicle_data=None,
    vehicle_status=None,
    connect_effect=None,
    fetch_effect=None,
):
    """Run async_setup with API mocks in place."""
    with patch(
        MOCK_API_CONNECT,
        return_value=connect_effect is None,
        side_effect=connect_effect,
    ), patch(MOCK_API_GET_VEHICLES, return_value=vehicle_list,), patch(
        MOCK_API_VIN_TO_NAME,
        return_value=vehicle_data[VEHICLE_NAME],
    ), patch(
        MOCK_API_GET_API_GEN,
        return_value=vehicle_data[VEHICLE_API_GEN],
    ), patch(
        MOCK_API_GET_MODEL_NAME,
        return_value=vehicle_data[VEHICLE_MODEL_NAME],
    ), patch(
        MOCK_API_GET_MODEL_YEAR,
        return_value=vehicle_data[VEHICLE_MODEL_YEAR],
    ), patch(
        MOCK_API_GET_EV_STATUS,
        return_value=vehicle_data[VEHICLE_HAS_EV],
    ), patch(
        MOCK_API_HAS_POWER_WINDOWS,
        return_value=vehicle_data[VEHICLE_HAS_POWER_WINDOWS],
    ), patch(
        MOCK_API_HAS_SUNROOF,
        return_value=vehicle_data[VEHICLE_HAS_SUNROOF],
    ), patch(
        MOCK_API_GET_RES_STATUS,
        return_value=vehicle_data[VEHICLE_HAS_REMOTE_START],
    ), patch(
        MOCK_API_GET_REMOTE_STATUS,
        return_value=vehicle_data[VEHICLE_HAS_REMOTE_SERVICE],
    ), patch(
        MOCK_API_GET_SAFETY_STATUS,
        return_value=vehicle_data[VEHICLE_HAS_SAFETY_SERVICE],
    ), patch(
        MOCK_API_GET_DATA,
        return_value=vehicle_status,
    ), patch(
        MOCK_API_UPDATE,
    ), patch(
        MOCK_API_FETCH, side_effect=fetch_effect
    ):
        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()


async def setup_default_ev_entry(hass, config_entry):
    """Run async_setup with API mocks in place and EV subscription responses."""
    await setup_subaru_config_entry(
        hass,
        config_entry,
        vehicle_list=[TEST_VIN_2_EV],
        vehicle_data=VEHICLE_DATA[TEST_VIN_2_EV],
        vehicle_status=VEHICLE_STATUS_EV,
    )


@pytest.fixture(name="subaru_config_entry", scope="function")
async def fixture_subaru_config_entry(hass, enable_custom_integrations):
    """Create a Subaru config entry prior to setup."""
    await async_setup_component(hass, HA_DOMAIN, {})
    config_entry = MockConfigEntry(**TEST_CONFIG_ENTRY)
    config_entry.add_to_hass(hass)
    return config_entry


@pytest.fixture
async def ev_entry(hass, subaru_config_entry, enable_custom_integrations):
    """Create a Subaru entry representing an EV vehicle with full STARLINK subscription."""
    await setup_default_ev_entry(hass, subaru_config_entry)
    return subaru_config_entry


@pytest.fixture
async def ev_entry_with_saved_climate(
    hass, subaru_config_entry, enable_custom_integrations
):
    """Create Subaru EV entity with saved climate preset."""
    mock_restore_cache(
        hass,
        (State("select.test_vehicle_2_climate_preset", "Full Heat"),),
    )
    await setup_default_ev_entry(
        hass,
        subaru_config_entry,
    )
    return subaru_config_entry


@pytest.fixture
async def ev_entry_charge_polling(
    hass, subaru_config_entry, enable_custom_integrations
):
    """Create a Subaru EV entity with charge polling option enabled."""
    options_form = await hass.config_entries.options.async_init(
        subaru_config_entry.entry_id
    )
    await hass.config_entries.options.async_configure(
        options_form["flow_id"],
        user_input={
            CONF_NOTIFICATION_OPTION: NotificationOptions.SUCCESS.value,
            CONF_POLLING_OPTION: PollingOptions.CHARGING.value,
        },
    )
    await setup_default_ev_entry(
        hass,
        subaru_config_entry,
    )
    return subaru_config_entry


async def migrate_unique_ids(
    hass, entitydata, old_unique_id, new_unique_id, subaru_config_entry
) -> None:
    """Test successful migration of entity unique_ids."""
    entity_registry = er.async_get(hass)
    entity: er.RegistryEntry = entity_registry.async_get_or_create(
        **entitydata,
        config_entry=subaru_config_entry,
    )
    assert entity.unique_id == old_unique_id

    await setup_default_ev_entry(hass, subaru_config_entry)

    entity_migrated = entity_registry.async_get(entity.entity_id)
    assert entity_migrated
    assert entity_migrated.unique_id == new_unique_id


async def migrate_unique_ids_duplicate(
    hass, entitydata, old_unique_id, new_unique_id, subaru_config_entry
) -> None:
    """Test unsuccessful migration of entity unique_ids due to duplicate."""
    entity_registry = er.async_get(hass)
    entity: er.RegistryEntry = entity_registry.async_get_or_create(
        **entitydata,
        config_entry=subaru_config_entry,
    )
    assert entity.unique_id == old_unique_id

    # create existing entry with new_unique_id that conflicts with migrate
    existing_entity = entity_registry.async_get_or_create(
        entitydata["domain"],
        entitydata["platform"],
        unique_id=new_unique_id,
        config_entry=subaru_config_entry,
    )

    await setup_default_ev_entry(hass, subaru_config_entry)

    entity_migrated = entity_registry.async_get(entity.entity_id)
    assert entity_migrated
    assert entity_migrated.unique_id == old_unique_id

    entity_not_changed = entity_registry.async_get(existing_entity.entity_id)
    assert entity_not_changed
    assert entity_not_changed.unique_id == new_unique_id

    assert entity_migrated != entity_not_changed
