# Subaru STARLINK Integration for Home Assistant
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

**NOTE:** The [Subaru](https://www.home-assistant.io/integrations/subaru/) integration is now part of Home Assistant Core (as of release [2021.3](https://www.home-assistant.io/blog/2021/03/03/release-20213/)), however not all features have been implemented. Currently, only the sensor and lock platforms are available. Additional PRs will be submitted to include all features of this custom component into Home Assistant Core.

Users that desire full functionality should continue to use this custom component until all functionality is merged into the official integration. This custom component will override the HA Core built-in integration.

***

* [Description](#description)
* [Installation](#installation)
  * [HACS](#hacs)
  * [Manual](#manual)
* [Configuration](#configuration)
* [Options](#options)
* [Services](#services)

## Description
The Subaru integration retrieves information provided by Subaru connected vehicle services.  Before using this integration, you must first register and have login credentials to [MySubaru](https://www.mysubaru.com).

This integration requires an active vehicle subscription to the [Subaru STARLINK](https://www.subaru.com/engineering/starlink/safety-security.html) service (available in USA and Canada).

Subaru has deployed two generations of telematics, Gen 1 and Gen 2. Use the tables below to determine which capabilities are available for your vehicle.

NOTE: There now appears to be a Gen 3, although it is unclear which model years have this capability. From analysis of the official Android mobile app, Gen 3 uses the same API endpoints as Gen 2, but may offer additional capability (tailgate unlock and hints of future remote window open/close?).

| Model     | Gen 1     | Gen 2 | Gen 3 |
|-----------|-----------|-------|-------|
| Ascent    |           | 2019+ |   ?   |    
| Crosstrek | 2016-2018 | 2019+ |   ?   | 
| Forester  | 2016-2018 | 2019+ |   ?   | 
| Impreza   | 2016-2018 | 2019+ |   ?   | 
| Legacy    | 2016-2019 | 2020+ |   ?   | 
| Outback   | 2016-2019 | 2020+ |   ?   | 
| WRX       | 2017+     |       |   ?   | 


| Sensor                   | Gen 1   | Gen 2   | Gen 3   |
|--------------------------|---------|---------|---------|
| Average fuel consumption |         | &check; | &check; |
| Distance to empty        |         | &check; | &check; |
| EV battery level         |         | &check; | &check; |
| EV range                 |         | &check; | &check; |
| EV time to full charge   |         | &check; | &check; |
| Odometer                 | &check;*| &check; | &check; |
| Tire pressures           |         | &check; | &check; |

\* Gen 1 odometer only updates every 500 miles <br>


| Binary Sensor            | Gen 1   | Gen 2   | Gen 3   |
|--------------------------|---------|---------|---------|
| Door/Trunk/Hood Status   |         | &check; | &check; |
| Window Status            |         | &check;*| &check; |
| Ignition Status          |         | &check; | &check; |
| EV Plug/Charging Status  |         | &check;*| &check; |

\* Not supported by all vehicles <br>


Device tracker, lock, and buttons (except refresh) all require a STARLINK Security Plus subscription:
| Device Tracker           | Gen 1   | Gen 2   | Gen 3   |
|--------------------------|---------|---------|---------|
| Vehicle Location         | &check; | &check; | &check; |


| Lock                     | Gen 1   | Gen 2   | Gen 3   |
|--------------------------|---------|---------|---------|
| Remote lock/unlock       | &check; | &check; | &check; |


| Buttons                  | Gen 1   | Gen 2   | Gen 3   |
|--------------------------|---------|---------|---------|
| Lock/Unlock              | &check; | &check; | &check; |
| Start/Stop Horn/Lights   | &check; | &check; | &check; |
| Poll vehicle             | &check; | &check; | &check; |
| Refresh data             | &check; | &check; | &check; |
| Start/Stop Horn/Lights   | &check; | &check; | &check; |
| Start/Stop Engine        |         | &check;*| &check;*|
| Start EV charging        |         | &check;*| &check;*|

\* Not supported by all vehicles <br>



## Installation
### HACS
Add `https://github.com/G-Two/homeassistant-subaru` as a custom integration repository and install the **Subaru (HACS)** integration. Restart Home Assistant.
### Manual
Clone or download this repository, and copy the `custom_components/subaru` directory into the `config/custom_components` directory of your Home Assistant instance. Restart Home Assistant.

## Configuration

Once installed, the Subaru integration is configured via the Home Assistant UI:

**Configuration** -> **Devices & Services** -> **Add Integration** -> **Subaru (HACS)**

**NOTE:** After installation and HA restart, you may need to clear your browser cache for the new integration to appear.

When prompted, enter the following configuration parameters:

- **Email Address:** The email address associated with your MySubaru account
- **Password:** The password associated with your MySubaru account
- **Country:** The country your MySubaru account is associated with

After your account is authenticated, you will need to authorize the application with Subaru's two factor authentication. Follow the prompts to select a phone number or email address to receive a verification code and enter when prompted. This should only need to be accomplished during initial configuration.

After successful authorization, if a supported remote services vehicle with active subscription is found in your account, an additional prompt will appear:
- **PIN:** The PIN associated with your MySubaru account

    **NOTE:** If your account includes multiple vehicles, the same PIN will be used for all vehicles. Ensure that you have configured all vehicles in your account to have the same PIN.

If the PIN prompt does not appear, no supported remote services vehicles were found in your account. Limited vehicle data may still appear as sensors.

## Options

Subaru integration options are set via:

**Configuration** -> **Devices & Services** -> **Subaru (HACS)** -> **Configure**.

All options involve remote commands, thus only apply to vehicles with Security Plus subscriptions:

- **Enable vehicle polling:**  Sensor data reported by the Subaru API only returns what is cached on Subaru servers, and does not necessarily reflect current conditions. The cached data is updated when the engine is shutdown, or when a location update is requested. This options enables automatic periodic updates.
  - **Disable *[Default]*:** New sensor data is only received when the vehicle automatically pushes data (normally after engine shutdown). The user may still manually poll the vehicle anytime with the Locate button.
  - **Charging:** For PHEVs, during charging, the integration will poll every 30 minutes to obtain updated charging status. Polling will only occur during charging.
  - **Enable:** Every 2 hours, the integration will send a remote command (equivalent to pressing the Locate button), "waking" your vehicle obtain new sensor data. *WARNING:* Vehicle polling draws power from the 12V battery. Long term use without driving may drain the battery resulting in the inability to start your vehicle.

- **Lovelace UI notifications for remote commands:**  It takes 10-15 seconds for remote commands to be processed by the Subaru API and transmitted over the cellular network to your vehicle. Some users may desire UI feedback that the integration is working. This option provides three levels of increasing verbosity:
  - **Disable *[Default]*:** Lovelace notifications are disabled. Errors will still be logged.
  - **Failure :** Only notify when the remote command has failed.
  - **Pending:** Failure + temporary notification that the command is "working" that will automatically disappear when the Subaru API confirms success (10 to 15 seconds).
  - **Success:** Pending + persistent notification of success in Lovelace. This is the same behavior as v0.5.1 and earlier releases.

## Services

The following Subaru entities use built-in Home Assistant services:
- Lock
- Button (Remote Start/Stop, Lights/Horn, Locate, Refresh)
- Select (Climate Control Preset)

The Lock entity's "Unlock" will unlock all doors. The Subaru API supports selecting a specific door to unlock. Users that wish to use this functionality may call an integration specific service which allows the user to choose the door to unlock. See the Services UI in Developer Tools for usage. Example YAML for this service is:
```yaml
service: subaru.unlock_specific_door
target:
  entity_id: lock.subaru_door_locks
data:
  # Valid values for door are 'all', 'driver', 'tailgate' (note that 'tailgate' is not supported by all vehicles)
  door: driver
```
### Remote Climate Control

For supported vehicles, this integration supports selecting specific remote climate control presets when remotely starting the engine. See the Services UI in Developer Tools for usage. Example YAML for this service is:
```yaml
service: subaru.remote_start
data:
  # preset_name is case sensitive
  preset_name: Full Heat
  # Use the Services UI to populate device_id
  device_id: 0cce5d5135ac6459ce620654362e45b8
```

There are 3 pre-configured Subaru climate presets, **Auto** (not available for EVs), **Full Cool**, and **Full Heat**. In addition you may configure up to 4 additional custom presets from the MySubaru website or the
official mobile app. Although the underlying subarulink python package does support the creation of new presets, that functionality has not yet been implemented in this
integration.
