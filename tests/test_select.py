"""Test Subaru select."""

from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, ATTR_OPTION, SERVICE_SELECT_OPTION

DEVICE_ID = "select.test_vehicle_2_climate_preset"


async def test_device_exists(hass, ev_entry):
    """Test subaru select entity exists."""
    entity_registry = await hass.helpers.entity_registry.async_get_registry()
    entry = entity_registry.async_get(DEVICE_ID)
    assert entry
    await hass.async_block_till_done()


async def test_select(hass, ev_entry_with_saved_climate):
    """Test subaru select function."""
    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {ATTR_ENTITY_ID: DEVICE_ID, ATTR_OPTION: "Full Heat"},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert hass.states.get(DEVICE_ID).state == "Full Heat"
