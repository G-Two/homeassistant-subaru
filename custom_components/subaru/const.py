"""Constants for the Subaru integration."""

DOMAIN = "subaru"
DEFAULT_SCAN_INTERVAL = 300
MIN_SCAN_INTERVAL = 60
DEFAULT_HARD_POLL_INTERVAL = 7200
MIN_HARD_POLL_INTERVAL = 300
CONF_HARD_POLL_INTERVAL = "hard_poll_interval"

# entry fields
ENTRY_CONTROLLER = "controller"
ENTRY_COORDINATOR = "coordinator"
ENTRY_VEHICLES = "vehicles"
ENTRY_LISTENER = "listener"

# update coordinator name
COORDINATOR_NAME = "subaru_data"

# info fields
VEHICLE_VIN = "vin"
VEHICLE_NAME = "display_name"
VEHICLE_HAS_EV = "is_ev"
VEHICLE_API_GEN = "api_gen"
VEHICLE_HAS_REMOTE_START = "has_res"
VEHICLE_HAS_REMOTE_SERVICE = "has_remote"
VEHICLE_HAS_SAFETY_SERVICE = "has_safety"
VEHICLE_LAST_UPDATE = "last_update"

API_GEN_1 = "g1"
API_GEN_2 = "g2"

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

SUPPORTED_PLATFORMS = [
    "binary_sensor",
    "device_tracker",
    "lock",
    "sensor",
]

ICONS = {
    "12V Battery Voltage": "mdi:car-battery",
    "Avg Fuel Consumption": "mdi:leaf",
    "EV Battery Level": "mdi:battery-high",
    "EV Time to Full Charge": "mdi:car-electric",
    "EV Range": "mdi:ev-station",
    "External Temp": "mdi:thermometer",
    "Odometer": "mdi:road-variant",
    "Range": "mdi:gas-station",
    "Tire Pressure FL": "mdi:gauge",
    "Tire Pressure FR": "mdi:gauge",
    "Tire Pressure RL": "mdi:gauge",
    "Tire Pressure RR": "mdi:gauge",
}
