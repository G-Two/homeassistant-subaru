# Subaru STARLINK for Home Assistant

**NOTE:** An [initial PR](https://github.com/home-assistant/core/pull/35760/) to add this component to Home Assistant Core is currently in progress.  This repo was created to continue development while the PR is in progress. After the initial PR is complete, additional PRs will follow based upon this repo.

The Subaru custom component connects to the [MySubaru](https://www.mysubuaru.com) service to provide vehicle sensor information as well as the capability to actuate remote features. This integration requires an active subscription to Subaru's [STARLINK](https://www.subaru.com/engineering/starlink/safety-security.html) service, which is currently only available in the United States and Canada. 

This integration provides the following platforms:

- Binary Sensors - Door, trunk, hood, window, ignition, and EV status
- Device Tracker - GPS location reported by the vehicle
- Lock - Remotely lock or unlock doors (unfortunately no state information is reported by the Subaru API)
- Sensors - Outside temperature, average fuel consumption, tire pressure, odometer, estimated range, and EV information (battery level, range, charging rate)

This integration also provides services to perform the following tasks:
- Lock and unlock doors
- Sound horn and/or flash lights
- Start and stop engine
- Start EV charging
- Poll vehicle for new data
- Refresh data

![hass_screenshot](https://user-images.githubusercontent.com/7310260/102023873-50fd5f80-3d5c-11eb-93ca-4b2bb6f27e92.png)

The entities and services made available to Home Assistant will be based upon the vehicle's model year and subscription status. 

| Model Year   | Safety Plus | Security Plus |
|--------------|-------------|---------------|
| 2016-2018    |  No Support | Device Tracker <br> Lock<br> Sensors* <br> Services 
| 2019+        |  Sensors**  | Binary Sensors <br> Device Tracker <br> Lock<br> Sensors <br>  Services |

\* Odometer sensor only (updates every 500 miles) <br>
\*\* Update interval unknown

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
- **Country:** The country your Subaru is associated with
The initial device registration process may take up to 20 seconds.

After successful authentication, if a supported remote services vehicle with active subscription is found in your account, an additional prompt will appear:
- **PIN:** The PIN associated with your MySubaru account
The PIN validation, if successful, will be followed by a vehicle update, which may up to 20 seconds.

If the PIN prompt does not appear, no supported remote services vehicles were found in your account. Limited vehicle data may still appear as sensors.

## Options

Subaru integration options are set via:

**Configuration** -> **Integrations** -> **Subaru** -> **Options**.

The options are:

- **Seconds between API polling *[Default: 300, Minimum: 60]*:** Controls how frequently Home Assistant will poll the MySubaru API for vehicle data they have cached on their servers. This does not invoke a remote service request to your vehicle, and the data may be stale. Your vehicle will still send new information during certain state changes, such as being turned off or having a charging cable plugged in.  Excessive API calls will not yield fresh data.
- **Seconds between vehicle polling *[Default: 7200, Minimum: 300]*:** Controls how frequently Home Assistant will invoke a remote service request to poll your vehicle to request an information update. This involves "waking" your vehicle and powering on electronics momentarily. Performing this action too frequently may drain your battery. 

## [Services](services.md)
