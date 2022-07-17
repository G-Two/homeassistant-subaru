"""Constants for the Subaru integration."""
import subarulink.const as sc

from homeassistant.const import Platform

DOMAIN = "subaru"
FETCH_INTERVAL = 300
UPDATE_INTERVAL = 7200
UPDATE_INTERVAL_CHARGING = 1800
CONF_POLLING_OPTION = "polling_option"
CONF_NOTIFICATION_OPTION = "notification_option"
CONF_COUNTRY = "country"

# entry fields
ENTRY_CONTROLLER = "controller"
ENTRY_COORDINATOR = "coordinator"
ENTRY_VEHICLES = "vehicles"
ENTRY_LISTENER = "listener"

# update coordinator name
COORDINATOR_NAME = "subaru_data"

# info fields
VEHICLE_VIN = "vin"
VEHICLE_MODEL_NAME = "model_name"
VEHICLE_MODEL_YEAR = "model_year"
VEHICLE_NAME = "display_name"
VEHICLE_HAS_EV = "is_ev"
VEHICLE_API_GEN = "api_gen"
VEHICLE_HAS_REMOTE_START = "has_res"
VEHICLE_HAS_REMOTE_SERVICE = "has_remote"
VEHICLE_HAS_SAFETY_SERVICE = "has_safety"
VEHICLE_LAST_UPDATE = "last_update"
VEHICLE_LAST_FETCH = "last_fetch"
VEHICLE_STATUS = "status"
VEHICLE_CLIMATE = "climate"
VEHICLE_CLIMATE_PRESET_NAME = "name"
VEHICLE_CLIMATE_SELECTED_PRESET = "preset_name"

API_GEN_1 = "g1"
API_GEN_2 = "g2"
MANUFACTURER = "Subaru"

ATTR_DOOR = "door"

REMOTE_SERVICE_FETCH = "fetch"
REMOTE_SERVICE_UPDATE = "update"
REMOTE_SERVICE_LOCK = "lock"
REMOTE_SERVICE_UNLOCK = "unlock"
REMOTE_SERVICE_LIGHTS = "lights"
REMOTE_SERVICE_LIGHTS_STOP = "lights_stop"
REMOTE_SERVICE_HORN = "horn"
REMOTE_SERVICE_HORN_STOP = "horn_stop"
REMOTE_SERVICE_REMOTE_START = "remote_start"
REMOTE_SERVICE_REMOTE_STOP = "remote_stop"
REMOTE_SERVICE_CHARGE_START = "charge_start"
REMOTE_CLIMATE_PRESET_NAME = "preset_name"

SERVICE_UNLOCK_SPECIFIC_DOOR = "unlock_specific_door"
UNLOCK_DOOR_ALL = "all"
UNLOCK_DOOR_DRIVERS = "driver"
UNLOCK_DOOR_TAILGATE = "tailgate"
UNLOCK_VALID_DOORS = {
    UNLOCK_DOOR_ALL: sc.ALL_DOORS,
    UNLOCK_DOOR_DRIVERS: sc.DRIVERS_DOOR,
    UNLOCK_DOOR_TAILGATE: sc.TAILGATE_DOOR,
}

SUPPORTED_PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.DEVICE_TRACKER,
    Platform.LOCK,
    Platform.SENSOR,
    Platform.BUTTON,
    Platform.SELECT,
]

ICONS = {
    "Horn Start": "mdi:volume-high",
    "Horn Stop": "mdi:volume-off",
    "Lights Start": "mdi:lightbulb-on",
    "Lights Stop": "mdi:lightbulb-off",
    "Locate": "mdi:car-connected",
    "Refresh": "mdi:refresh",
    "Remote Start": "mdi:power",
    "Remote Stop": "mdi:stop-circle-outline",
    "Charge EV": "mdi:ev-station",
    "Climate Preset": "mdi:thermometer-lines",
}
