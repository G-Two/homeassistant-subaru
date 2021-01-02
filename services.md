# Subaru STARLINK for Home Assistant

## Services

### `subaru.lock`
Lock all doors of the vehicle. The vehicle is identified by the `vin`.

| Service Data Attribute | Required | Description                                        |
| ---------------------- | -------- | -------------------------------------------------- |
| `vin`                  |   yes    | The vehicle identification number (VIN) of the vehicle, 17 characters |

### `subaru.unlock`
Unlock all doors of the vehicle. The vehicle is identified by the `vin`.

| Service Data Attribute | Required | Description                                        |
| ---------------------- | -------- | -------------------------------------------------- |
| `vin`                  |   yes    | The vehicle identification number (VIN) of the vehicle, 17 characters |

### `subaru.lights`
Flash the lights of the vehicle. The vehicle is identified by the `vin`.

| Service Data Attribute | Required | Description                                        |
| ---------------------- | -------- | -------------------------------------------------- |
| `vin`                  |   yes    | The vehicle identification number (VIN) of the vehicle, 17 characters |

### `subaru.lights_cancel`
Stop flashing the lights of the vehicle. The vehicle is identified by the `vin`.

| Service Data Attribute | Required | Description                                        |
| ---------------------- | -------- | -------------------------------------------------- |
| `vin`                  |   yes    | The vehicle identification number (VIN) of the vehicle, 17 characters |

### `subaru.horn`
Sound the horn and flash the lights of the vehicle. The vehicle is identified by the `vin`.

| Service Data Attribute | Required | Description                                        |
| ---------------------- | -------- | -------------------------------------------------- |
| `vin`                  |   yes    | The vehicle identification number (VIN) of the vehicle, 17 characters |

### `subaru.horn_cancel`
Stop sounding the horn and flash the lights of the vehicle. The vehicle is identified by the `vin`.

| Service Data Attribute | Required | Description                                        |
| ---------------------- | -------- | -------------------------------------------------- |
| `vin`                  |   yes    | The vehicle identification number (VIN) of the vehicle, 17 characters |

### `subaru.update`
Sends request to vehicle to update data. The vehicle is identified by the `vin`.

| Service Data Attribute | Required | Description                                        |
| ---------------------- | -------- | -------------------------------------------------- |
| `vin`                  |   yes    | The vehicle identification number (VIN) of the vehicle, 17 characters |

### `subaru.fetch`
Refreshes data (does not request update from vehicle). The vehicle is identified by the `vin`.

| Service Data Attribute | Required | Description                                        |
| ---------------------- | -------- | -------------------------------------------------- |
| `vin`                  |   yes    | The vehicle identification number (VIN) of the vehicle, 17 characters |

### `subaru.remote_start`
Start the engine and climate control of the vehicle.  Uses the climate control settings saved. The vehicle is identified by the `vin`.

| Service Data Attribute | Required | Description                                        |
| ---------------------- | -------- | -------------------------------------------------- |
| `vin`                  |   yes    | The vehicle identification number (VIN) of the vehicle, 17 characters |

### `subaru.remote_stop`
Stop the engine and climate control of the vehicle. The vehicle is identified by the `vin`.

| Service Data Attribute | Required | Description                                        |
| ---------------------- | -------- | -------------------------------------------------- |
| `vin`                  |   yes    | The vehicle identification number (VIN) of the vehicle, 17 characters |

### `subaru.charge_start`
Starts EV charging. This cannot be stopped remotely. The vehicle is identified by the `vin`.

| Service Data Attribute | Required | Description                                        |
| ---------------------- | -------- | -------------------------------------------------- |
| `vin`                  |   yes    | The vehicle identification number (VIN) of the vehicle, 17 characters |

