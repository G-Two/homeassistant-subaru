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
* [Lovelace Example](#lovelace-example)

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
| 12V battery voltage      |         | &check; | &check; |
| Average fuel consumption |         | &check; | &check; |
| Distance to empty        |         | &check; | &check; |
| EV battery level         |         | &check; | &check; |
| EV range                 |         | &check; | &check; |
| EV time to full charge   |         | &check; | &check; |
| External temperature     |         | &check; | &check; |
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
  - **Disabled *[Default]*:** New sensor data is only received when the vehicle automatically pushes data (normally after engine shutdown). The user may still manually poll the vehicle anytime with the `subaru.update` service.
  - **Enabled:** Every 2 hours, the integration will send a remote command (equivalent to running the `subaru.update` service), "waking" your vehicle obtain new sensor data. *WARNING:* Vehicle polling draws power from the 12V battery. Long term use without driving may drain the battery resulting in the inability to start your vehicle.

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

---
### Legacy Services
**NOTE:** All the legacy services below will be removed in release v0.7.0:

| Service                | Description |
| ---------------------- | ----------- |
|`subaru.charge_start`   | Starts EV charging (this cannot be stopped remotely) |
|`subaru.fetch`          | Fetches vehicle data cached on Subaru servers (does not request update from vehicle) |
|`subaru.horn`           | Sound the horn and flash the lights of the vehicle |
|`subaru.horn_cancel`    | Stop sounding the horn and flash the lights of the vehicle |
|`subaru.lights`         | Flash the lights of the vehicle |
|`subaru.lights_cancel`  | Stop flashing the lights of the vehicle |
|`subaru.remote_stop`    | Stop the engine and climate control of the vehicle |
|`subaru.update`         | Sends request to vehicle to update data which will update cache on Subaru servers |

All of the legacy services require the same service data attribute shown below. The service will be invoked on the vehicle identified by `vin`.

| Service Data Attribute | Required | Type   | Description                                        |
| ---------------------- | -------- | ------ | -------------------------------------------------- |
| `vin`                  |   yes    | String | The vehicle identification number (VIN) of the vehicle, 17 characters |



## Lovelace Example
<img src="https://user-images.githubusercontent.com/7310260/148698672-48cdc85f-623b-4f06-88e2-6e1949b4a522.png" width="1024" />

<details><summary>Example Lovelace YAML</summary>
<p>

```yaml
# Example YAML for the dashboard shown above.
title: Status
views:
  - icon: ''
    title: Status
    badges: []
    cards:
      - type: horizontal-stack
        cards:
          - entity: button.subaru_refresh
            hold_action:
              action: more-info
            show_icon: true
            show_name: false
            show_state: false
            tap_action:
              action: call-service
              service: button.press
              service_data: {}
              target:
                entity_id: button.subaru_refresh
            type: button
            icon_height: 48px
          - entity: button.subaru_locate
            hold_action:
              action: more-info
            show_icon: true
            show_name: false
            show_state: false
            tap_action:
              action: call-service
              confirmation:
                text: Poll Vehicle?
              service: button.press
              service_data: {}
              target:
                entity_id: button.subaru_locate
            type: button
            icon_height: 48px
        title: Update Data
      - cards:
          - entity: sensor.subaru_odometer
            name: Odometer
            type: entity
          - entity: sensor.subaru_avg_fuel_consumption
            name: Avg Fuel Consumption
            type: entity
          - entity: sensor.subaru_range
            name: Distance to Empty
            type: entity
        type: vertical-stack
        title: Mileage
      - cards:
          - cards:
              - entity: sensor.subaru_tire_pressure_fl
                max: 38
                min: 24
                name: FL
                severity:
                  green: 36
                  red: 2
                  yellow: 32
                type: gauge
                needle: true
              - entity: sensor.subaru_tire_pressure_fr
                name: FR
                severity:
                  green: 36
                  red: 0
                  yellow: 32
                type: gauge
                needle: true
                min: 24
                max: 38
            type: horizontal-stack
          - cards:
              - entity: sensor.subaru_tire_pressure_rl
                name: RL
                type: gauge
                needle: true
                min: 24
                severity:
                  green: 36
                  yellow: 32
                  red: 0
                max: 38
              - entity: sensor.subaru_tire_pressure_rr
                name: RR
                severity:
                  green: 36
                  red: 0
                  yellow: 32
                type: gauge
                needle: true
                min: 24
                max: 38
            type: horizontal-stack
        type: vertical-stack
        title: Tire Pressure
      - type: vertical-stack
        title: Remote Commands
        cards:
          - cards:
              - type: button
                tap_action:
                  action: more-info
                entity: lock.subaru_door_locks
                show_state: false
                show_name: false
                icon_height: 48px
            type: horizontal-stack
          - cards:
              - type: button
                tap_action:
                  action: call-service
                  confirmation:
                    text: Flash lights?
                  service: button.press
                  service_data: {}
                  target:
                    entity_id:
                      - button.subaru_lights_start
                entity: button.subaru_lights_start
                show_state: false
                show_name: false
                icon_height: 48px
              - entity: button.subaru_lights_stop
                icon_height: 48px
                show_icon: true
                show_name: false
                tap_action:
                  action: call-service
                  confirmation:
                    text: Stop lights?
                  service: button.press
                  service_data: {}
                  target:
                    entity_id: button.subaru_lights_stop
                type: button
            type: horizontal-stack
          - cards:
              - type: button
                tap_action:
                  action: call-service
                  confirmation:
                    text: Sound horn?
                  service: button.press
                  service_data: {}
                  target:
                    entity_id: button.subaru_horn_start
                entity: button.subaru_horn_start
                show_state: false
                show_name: false
                icon_height: 48px
              - entity: button.subaru_horn_stop
                icon_height: 48px
                show_icon: true
                show_name: false
                tap_action:
                  action: call-service
                  confirmation:
                    text: Stop horn?
                  service: button.press
                  service_data: {}
                  target:
                    entity_id: button.subaru_horn_stop
                type: button
            type: horizontal-stack
          - cards:
              - entity: button.subaru_remote_start
                icon_height: 48px
                show_icon: true
                show_name: false
                tap_action:
                  action: call-service
                  confirmation:
                    text: Remote Start Car?
                  service: button.press
                  service_data: {}
                  target:
                    entity_id: button.subaru_remote_start
                type: button
              - type: button
                tap_action:
                  action: call-service
                  confirmation:
                    text: Remote Stop Car?
                  service: button.press
                  service_data: {}
                  target:
                    entity_id: button.subaru_remote_stop
                entity: button.subaru_remote_stop
                show_state: false
                show_name: false
                icon_height: 48px
            type: horizontal-stack
          - type: entities
            entities:
              - entity: select.subaru_climate_preset
            show_header_toggle: true
      - type: vertical-stack
        cards:
          - detail: -2
            entity: sensor.subaru_12v_battery_voltage
            graph: line
            name: Auxiliary Battery
            type: sensor
          - entity: sensor.subaru_external_temp
            graph: line
            name: External Temp
            type: sensor
          - type: entity
            entity: binary_sensor.subaru_ignition
            name: ' '
        title: Miscellaneous Data
      - card:
          type: glance
          title: Door(s) Open
        type: entity-filter
        entities:
          - entity: binary_sensor.subaru_front_left_door
            name: FL Door
            show_state: false
            show_icon: false
            icon: None
          - entity: binary_sensor.subaru_hood
            name: Hood
            show_state: false
            show_icon: false
            icon: None
          - entity: binary_sensor.subaru_front_right_door
            name: FR Door
            show_state: false
            show_icon: false
            icon: None
          - entity: binary_sensor.subaru_rear_left_door
            name: RL Door
            show_state: false
            show_icon: false
            icon: None
          - entity: binary_sensor.subaru_trunk
            name: Trunk
            show_state: false
            show_icon: false
            icon: None
          - entity: binary_sensor.subaru_rear_right_door
            name: RR Door
            show_state: false
            show_icon: false
            icon: None
        state_filter:
          - 'on'
        show_empty: false
      - type: vertical-stack
        title: EV Functions
        cards:
          - cards:
              - entity: button.subaru_charge_ev
                hold_action:
                  action: more-info
                show_icon: true
                show_name: false
                show_state: false
                tap_action:
                  action: call-service
                  confirmation:
                    text: Begin Charging?
                  service: button.press
                  service_data: {}
                  target:
                    entity_id: button.subaru_charge_ev
                type: button
                icon_height: 48px
              - entity: sensor.subaru_ev_battery_level
                name: EV Battery Level
                type: entity
            type: horizontal-stack
          - type: vertical-stack
            cards:
              - type: horizontal-stack
                cards:
                  - type: entity
                    entity: binary_sensor.subaru_ev_charge_port
                    name: Plugged In
                  - type: conditional
                    conditions:
                      - entity: sensor.subaru_ev_time_to_full_charge
                        state_not: 'unavailable'
                    card:
                      type: entity
                      entity: sensor.subaru_ev_time_to_full_charge
      - type: map
        entities:
          - entity: device_tracker.subaru_location
        hours_to_show: 0
        default_zoom: 3
```
</p>
</details>
