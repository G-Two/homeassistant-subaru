# Subaru STARLINK for Home Assistant

**NOTE:** An [initial PR](https://github.com/home-assistant/core/pull/35760/) to add this component to Home Assistant Core is currently in progress.  This repo was created to continue development while the PR is in progress. After the initial PR is complete, additional PRs will follow based upon this repo.

The Subaru custom component connects to the [MySubaru](https://www.mysubuaru.com) service to provide vehicle sensor information as well as the capability to actuate remote features. This integration requires an active subscription to Subaru of America's [STARLINK](https://www.subaru.com/engineering/starlink/safety-security.html) service, which is currently only available in the United States and Canada. 

This integration provides the following platforms:

- Sensors - Outside temperature, average fuel consumption, tire pressure, odometer, estimated range, and EV information (battery level, range, charging rate)
- Binary Sensors - Door, trunk, hood, ignition, and EV information (plug and charge status)
- Device Tracker - GPS location reported by the vehicle
- Lock - Remotely lock or unlock doors (unfortunately no state information is reported by the Subaru API)

This integration also provides services to perform the following tasks:
- Lock and unlock doors
- Sound horn and/or flash lights
- Start and stop engine
- Start EV charging
- Poll vehicle for new data
- Refresh data 

The entities and services made available to your Home Assistant instance will be based upon your vehicle's capability and your subscription status. 

## Installation
Clone or download this repository, and copy the `custom_components\subaru` directory into the `config\custom_components` directory of your Home Assistant instance. Restart Home Assistant.

## Configuration

The Subaru integration offers configuration through the Home Assistant UI:
    
**Configuration** -> **Integrations** -> **Add** -> **Subaru**

When prompted, enter the following configuration parameters:

- **Email Address:** The email address associated with your MySubaru account.
- **Password:** The password associated with your MySubaru account.
- **PIN:** The PIN associated with your MySubaru account.
  - Note: If your account does not support remote services, then the PIN will not be used for anything.

First-time validation of your credentials may take up to 30 seconds. 

## Options

Subaru integration options are set via:

**Configuration** -> **Integrations** -> **Subaru** -> **Options**.

The options are:

- **Seconds between API polling *[Default: 300, Minimum: 60]*:** Controls how frequently Home Assistant will poll the MySubaru API for vehicle data they have cached on their servers. This does not invoke a remote service request to your vehicle, and the data may be stale. Your vehicle will still send new information during certain state changes, such as being turned off or having a charging cable plugged in.  Excessive API calls will not yield fresh data.
- **Seconds between vehicle polling *[Default: 7200, Minimum: 300]*:** Controls how frequently Home Assistant will invoke a remote service request to poll your vehicle to request an information update. This involves "waking" your vehicle and powering on electronics momentarily. Performing this action too frequently may drain your battery. 
