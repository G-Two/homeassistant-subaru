# Subaru STARLINK integration for Home Assistant

**NOTE:** The [Subaru integration](https://www.home-assistant.io/integrations/subaru/) is now part of the Home Assistant Core (as of release [2021.3](https://www.home-assistant.io/blog/2021/03/03/release-20213/)), however not all features have been implemented. Currently, only the sensor platform is available. Users that desire full functionality should continue to use this custom component until all platforms are merged into the official integration. As of v0.4.0, the domain for this custom component has been changed to `subaru_hacs` to deconflict with the Home Assistant Core (which uses `subaru`).

The Subaru integration retrieves information provided by Subaru connected vehicle services.  Before using this integration, you must first register and have login credentials to [MySubaru](https://www.mysubaru.com).

This integration requires an active vehicle subscription to the [Subaru STARLINK](https://www.subaru.com/engineering/starlink/safety-security.html) service (available in USA and Canada).

![hass_screenshot](https://user-images.githubusercontent.com/7310260/102023873-50fd5f80-3d5c-11eb-93ca-4b2bb6f27e92.png)


Subaru has deployed two generations of telematics, Gen 1 and Gen 2. Use the tables below to determine which capabilities are available for your vehicle.

| Model     | Gen 1     | Gen 2 |
|-----------|-----------|-------|
| Ascent    |           | 2019+ |
| Crosstrek | 2016-2018 | 2019+ |
| Forester  | 2016-2018 | 2019+ |
| Impreza   | 2016-2018 | 2019+ |
| Legacy    | 2016-2019 | 2020+ |
| Outback   | 2016-2019 | 2020+ |
| WRX       | 2017+     |       |


| Sensor                   | Gen 1   | Gen 2   |
|--------------------------|---------|---------|
| 12V battery voltage      |         | &check; |
| Average fuel consumption |         | &check; |
| Distance to empty        |         | &check; |
| EV battery level         |         | &check; |
| EV range                 |         | &check; |
| EV time to full charge   |         | &check; |
| External temperature     |         | &check; |
| Odometer                 | &check;*| &check; |
| Tire pressures           |         | &check; |

\* Gen 1 odometer only updates every 500 miles <br>


| Binary Sensor            | Gen 1   | Gen 2   |
|--------------------------|---------|---------|
| Door/Trunk/Hood Status   |         | &check; |
| Window Status            |         | &check;*|
| Ignition Status          |         | &check; |
| EV Plug/Charging Status  |         | &check;*|

\* Not supported by all vehicles <br>


The following features require a STARLINK Security Plus subscription:
| Device Tracker           | Gen 1   | Gen 2   |
|--------------------------|---------|---------|
| Vehicle Location         | &check; | &check; |


| Lock                     | Gen 1   | Gen 2   |
|--------------------------|---------|---------|
| Remote lock/unlock       | &check; | &check; |


This integration also provides services to perform the following tasks:

| Services                 | Gen 1   | Gen 2   |
|--------------------------|---------|---------|
| Lock/Unlock              | &check; | &check; |
| Start/Stop Horn/Lights   | &check; | &check; |
| Poll vehicle             | &check; | &check; |
| Refresh data             | &check; | &check; |
| Start/Stop Horn/Lights   | &check; | &check; |
| Start/Stop Engine        |         | &check;*|
| Start EV charging        |         | &check;*|

\* Not supported by all vehicles <br>



## Installation
### HACS
Add `https://github.com/G-Two/homeassistant-subaru` as a custom integration repository and install the Subaru STARLINK integration.
### Manual
Clone or download this repository, and copy the `custom_components/subaru` directory into the `config/custom_components` directory of your Home Assistant instance. Restart Home Assistant.

## Configuration

Once installed, the Subaru integration is configured via the Home Assistant UI:
    
**Configuration** -> **Integrations** -> **Add** -> **Subaru**

When prompted, enter the following configuration parameters:

- **Email Address:** The email address associated with your MySubaru account
- **Password:** The password associated with your MySubaru account
- **Country:** The country your MySubaru account is associated with

The initial device registration process may take up to 20 seconds.

After successful authentication, if a supported remote services vehicle with active subscription is found in your account, an additional prompt will appear:
- **PIN:** The PIN associated with your MySubaru account

    **NOTE:** If your account includes multiple vehicles, the same PIN will be used for all vehicles. Ensure that you have configured all vehicles in your account to have the same PIN.

If the PIN prompt does not appear, no supported remote services vehicles were found in your account. Limited vehicle data may still appear as sensors.

## Options

Subaru integration options are set via:

**Configuration** -> **Integrations** -> **Subaru** -> **Options**.

The options are:

- **Enable vehicle polling *[Default: off]*:**  When enabled, vehicle polling will send a remote command to your vehicle every 2 hours to obtain new sensor data. This involves “waking” your vehicle and requesting that it send new data to Subaru servers. Without vehicle polling, new sensor data is only received when the vehicle automatically pushes data (normally after engine shutdown). This option only applies to vehicles with Security Plus subscriptions.

    **WARNING:** Vehicle polling draws power from the 12V battery. Long term use without driving may drain the battery resulting in the inability to start.

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


