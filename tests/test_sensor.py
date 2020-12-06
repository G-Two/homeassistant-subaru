"""Test Subaru sensors."""

from homeassistant.util import slugify
from homeassistant.util.unit_system import IMPERIAL_SYSTEM
from pytest_homeassistant_custom_component.async_mock import patch

from custom_components.subaru.const import DOMAIN, ENTRY_COORDINATOR, VEHICLE_NAME
from custom_components.subaru.sensor import (
    API_GEN_2_SENSORS,
    EV_SENSORS,
    SAFETY_SENSORS,
    SENSOR_FIELD,
    SENSOR_NAME,
)

from .api_responses import (
    EXPECTED_STATE_EV_IMPERIAL,
    EXPECTED_STATE_EV_METRIC,
    TEST_VIN_2_EV,
    VEHICLE_DATA,
    VEHICLE_STATUS_EV,
)
from .common import ev_entry

VEHICLE_NAME = VEHICLE_DATA[TEST_VIN_2_EV][VEHICLE_NAME]


async def test_sensors_ev_imperial(hass, ev_entry):
    """Test sensors supporting imperial units."""
    with patch("custom_components.subaru.SubaruAPI.fetch"), patch(
        "custom_components.subaru.SubaruAPI.get_data", return_value=VEHICLE_STATUS_EV,
    ):
        hass.config.units = IMPERIAL_SYSTEM
        coordinator = hass.data[DOMAIN][ev_entry.entry_id][ENTRY_COORDINATOR]
        await coordinator.async_refresh()
        await hass.async_block_till_done()

    _assert_data(hass, EXPECTED_STATE_EV_IMPERIAL)


async def test_sensors_ev_metric(hass, ev_entry):
    """Test sensors supporting metric units."""
    _assert_data(hass, EXPECTED_STATE_EV_METRIC)


def _assert_data(hass, expected_state):
    sensor_list = EV_SENSORS
    sensor_list.extend(API_GEN_2_SENSORS)
    sensor_list.extend(SAFETY_SENSORS)
    expected_states = {}
    for item in sensor_list:
        expected_states[
            f"sensor.{slugify(f'{VEHICLE_NAME} {item[SENSOR_NAME]}')}"
        ] = expected_state[item[SENSOR_FIELD]]

    for sensor in expected_states:
        actual = hass.states.get(sensor)
        assert actual.state == expected_states[sensor]
