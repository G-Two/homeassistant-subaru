"""Migrate entity unique_ids."""
from __future__ import annotations

import logging
from typing import Any

from custom_components.subaru.binary_sensor import (
    API_GEN_2_BINARY_SENSORS,
    EV_BINARY_SENSORS,
)
from custom_components.subaru.button import (
    EV_REMOTE_BUTTONS,
    G1_REMOTE_BUTTONS,
    RES_REMOTE_BUTTONS,
)
from custom_components.subaru.select import OLD_CLIMATE_SELECT
from custom_components.subaru.sensor import (
    API_GEN_2_SENSORS,
    EV_SENSORS,
    SAFETY_SENSORS,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er

_LOGGER = logging.getLogger(__name__)


async def async_migrate_entries(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Migrate entities from versions prior to 0.6.5 to use preferred unique_id."""
    entity_registry = er.async_get(hass)

    all_entities = []
    all_entities.extend(API_GEN_2_BINARY_SENSORS)
    all_entities.extend(EV_BINARY_SENSORS)
    all_entities.extend(SAFETY_SENSORS)
    all_entities.extend(API_GEN_2_SENSORS)
    all_entities.extend(EV_SENSORS)
    all_entities.extend(G1_REMOTE_BUTTONS)
    all_entities.extend(RES_REMOTE_BUTTONS)
    all_entities.extend(EV_REMOTE_BUTTONS)
    all_entities.extend([OLD_CLIMATE_SELECT])

    # Old unique_id is (previously title-cased) sensor name (e.g. "VIN_Avg Fuel Consumption")
    replacements = {str(s.name).upper(): s.key for s in all_entities}

    @callback
    def update_unique_id(entry: er.RegistryEntry) -> dict[str, Any] | None:
        id_split = entry.unique_id.split("_", maxsplit=1)
        key = id_split[1].upper() if len(id_split) == 2 else None

        if key not in replacements or id_split[1] == replacements[key]:
            return None

        new_unique_id = entry.unique_id.replace(id_split[1], replacements[key])
        _LOGGER.debug(
            "Migrating entity '%s' unique_id from '%s' to '%s'",
            entry.entity_id,
            entry.unique_id,
            new_unique_id,
        )
        if existing_entity_id := entity_registry.async_get_entity_id(
            entry.domain, entry.platform, new_unique_id
        ):
            _LOGGER.warning(
                "Cannot migrate to unique_id '%s', already exists for '%s'",
                new_unique_id,
                existing_entity_id,
            )
            return None
        return {
            "new_unique_id": new_unique_id,
        }

    await er.async_migrate_entries(hass, config_entry.entry_id, update_unique_id)
