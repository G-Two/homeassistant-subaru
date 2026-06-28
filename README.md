# MySubaru Connected Services Custom Integration for Home Assistant
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

> [!NOTE]
> The [Subaru](https://www.home-assistant.io/integrations/subaru/) integration is now part of Home Assistant Core (as of release [2021.3](https://www.home-assistant.io/blog/2021/03/03/release-20213/)), however not all features have been implemented. Currently, only the device tracker, sensor, and lock platforms are available. Additional PRs will be submitted to include all features of this custom component into Home Assistant Core. Users that desire full functionality should continue to use this custom component until all functionality is merged into Home Assistant Core. When installed, this custom component overrides the Home Assistant Core built-in Subaru integration.

***

* [Description](#description)
* [Installation](#installation)
  * [HACS](#hacs)
  * [Manual](#manual)
* [Configuration](#configuration)
* [Options](#options)
* [Services](#services)
* [Events](#events)
* [Development](#development)

## Description
This Home Assistant custom component retrieves vehicle information and actuates remote services provided by MySubaru Connected Services (formerly known as Subaru STARLINK) available in USA/Canada.

This integration requires a telematics-equipped Subaru and an active vehicle subscription to MySubaru Connected Services. Before using this integration, you must first register and have login credentials to [MySubaru](https://www.mysubaru.com).

Subaru has deployed four generations of telematics. The model-year ranges below are approximate, as generation transitions don't always align cleanly to a model year.

> [!NOTE]
> Subaru rebranded subscription plans in late 2025. Plans formerly known as **Safety Plus** and **Security Plus** are now **MySubaru Safety** and **MySubaru Security** on 2016–2025 (Gen 1–3) vehicles. 2026+ (Gen 4) vehicles use **MySubaru Companion** (Safety tier) and **MySubaru Companion+** (Security tier). A **Concierge** plan also exists for Gen 4; it includes the same remote vehicle features as Companion+.

| Generation | Model Years |
|------------|-------------|
| Gen 1      | 2016–2018   |
| Gen 2      | 2019–2022   |
| Gen 3      | 2023–2025   |
| Gen 4      | 2026+†      |

† Gen 4 support is still being characterized

> [!NOTE]
> Subaru battery-electric vehicles (e.g. Solterra) use the Toyota-based SubaruConnect platform and are **not** supported by this integration. The sole exception is the 2019–2023 Crosstrek PHEV, which uses MySubaru and is supported.

### Sensors
| Sensor                   | Gen 1   | Gen 2   | Gen 3   | Gen 4   |
|--------------------------|---------|---------|---------|---------|
| Average fuel consumption |         | &check; | &check; | &check; |
| Distance to empty        |         | &check; | &check; | &check; |
| EV battery level         |         | &check;*|         |         |
| EV range                 |         | &check;*|         |         |
| EV time to full charge   |         | &check;*|         |         |
| Fuel level               |         |         | &check; | &check; |
| Odometer                 | &check;†| &check; | &check; | &check; |
| Tire pressures           |         | &check; | &check; | &check; |

\* 2019-2023 Crosstrek PHEV only <br>
† Gen 1 odometer only updates every 500 miles <br>

### Binary Sensors
| Binary Sensor            | Gen 1   | Gen 2   | Gen 3   | Gen 4   |
|--------------------------|---------|---------|---------|---------|
| Door/Trunk/Hood Status   |         | &check; | &check; | &check; |
| Lock Status              |         |         | &check;†| &check; |
| Window Status            |         |         | &check; | &check; |
| Ignition Status          |         | &check; | &check; | &check; |
| EV Plug/Charging Status  |         | &check;*|         |         |

\* 2019-2023 Crosstrek PHEV only <br>
† Reported by some Gen 3 vehicles but may not be reliable <br>

### Device Tracker
Device tracker, lock, and buttons (except refresh) all require a remote services subscription (Security Plus or MySubaru Security on Gen 1–3; MySubaru Companion+ or Concierge on Gen 4):
| Device Tracker           | Gen 1   | Gen 2   | Gen 3   | Gen 4   |
|--------------------------|---------|---------|---------|---------|
| Vehicle Location         | &check; | &check; | &check; | &check; |

### Lock
| Lock                     | Gen 1   | Gen 2   | Gen 3   | Gen 4   |
|--------------------------|---------|---------|---------|---------|
| Remote lock/unlock       | &check; | &check; | &check; | &check; |

This integration supports remote locking and unlocking of vehicle doors. If doors are remotely unlocked, they will automatically relock if a door is not opened within a minute. There is no remote notification of this automatic relock.
> [!NOTE]
> Lock status is reported by Gen 4 vehicles and some Gen 3 vehicles, but reporting may not be reliable. On Gen 1–2 vehicles, lock status is always unknown because the Subaru API does not report this data.

### Buttons
| Buttons                  | Gen 1   | Gen 2   | Gen 3   | Gen 4   |
|--------------------------|---------|---------|---------|---------|
| Start/Stop Horn/Lights   | &check; | &check; | &check; | &check; |
| Poll vehicle             | &check; | &check; | &check; | &check; |
| Refresh data             | &check; | &check; | &check; | &check; |
| Remote Start/Stop        |         | &check; | &check; | &check; |
| Start EV charging        |         | &check;*|         |         |

<br>\* 2019-2023 Crosstrek PHEV only <br>

## Installation
### HACS
Add `https://github.com/G-Two/homeassistant-subaru` as a custom integration repository and install the **Subaru (HACS)** integration. Restart Home Assistant.
### Manual
Clone or download this repository, and copy the `custom_components/subaru` directory into the `config/custom_components` directory of your Home Assistant instance. Restart Home Assistant.

## Configuration

Once installed, the Subaru integration is configured via the Home Assistant UI:

**Configuration** -> **Devices & Services** -> **Add Integration** -> **Subaru (HACS)**

> [!IMPORTANT]
> After installation and HA restart, you may need to clear your browser cache for the new integration to appear.

When prompted, enter the following configuration parameters:

- **Email Address:** The email address associated with your MySubaru account
- **Password:** The password associated with your MySubaru account
- **Country:** The country your MySubaru account is associated with

After your account is authenticated, you will need to authorize the application with Subaru's two factor authentication. Follow the prompts to select a phone number or email address to receive a verification code and enter when prompted. This should only need to be accomplished during initial configuration.

After successful authorization, if a supported remote services vehicle with active subscription is found in your account, an additional prompt will appear:
- **PIN:** The PIN associated with your MySubaru account

> [!IMPORTANT]
> If your account includes multiple vehicles, the same PIN will be used for all vehicles. Ensure that you have configured all vehicles in your account to have the same PIN.

If the PIN prompt does not appear, no supported remote services vehicles were found in your account. Limited vehicle data may still appear as sensors.

## Options

Subaru integration options are set via:

**Configuration** -> **Devices & Services** -> **Subaru (HACS)** -> **Configure**.

All options involve remote commands, thus only apply to vehicles with a remote services subscription (Security Plus / MySubaru Security on Gen 1–3; MySubaru Companion+ or Concierge on Gen 4):

- **Enable vehicle polling:**  Sensor data reported by the Subaru API only returns what is cached on Subaru servers, and does not necessarily reflect current conditions. The cached data is updated when the engine is shutdown, or when a location update is requested. This options enables automatic periodic updates.
  - **Disable *[Default]*:** New sensor data is only received when the vehicle automatically pushes data (normally after engine shutdown). The user may still manually poll the vehicle anytime with the Locate button.
  - **Charging:** For PHEVs, during charging, the integration will poll every 30 minutes to obtain updated charging status. Polling will only occur during charging.
  - **Enable:** Every 2 hours, the integration will send a remote command (equivalent to pressing the Locate button), "waking" your vehicle obtain new sensor data.
> [!WARNING]
> Vehicle polling draws power from the 12V battery. Long term use without driving may drain the battery resulting in the inability to start your vehicle.

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

## Events

### subaru_command_sent

This event is fired when a command is called.

| Field      | Description                                                    |
|------------|----------------------------------------------------------------|
| `command`  | The command that was called. See [Command list](#command-list) |
| `car_name` | The name of the vehicle                                        |

### subaru_command_successful

This event is fired when a command is successful.

| Field      | Description                                                    |
|------------|----------------------------------------------------------------|
| `command`  | The command that was called. See [Command list](#command-list) |
| `car_name` | The name of the vehicle                                        |

### subaru_command_failed

This event is fired when a command fails.

| Field      | Description                                                    |
|------------|----------------------------------------------------------------|
| `command`  | The command that was called. See [Command list](#command-list) |
| `car_name` | The name of the vehicle                                        |
| `message`  | The message returned from the failed command                   |

### Command List

This is a list of possible commands for the above events.

`fetch`, `update`, `lock`, `unlock`, `lights`, `lights_stop`, `horn`, `horn_stop`, `remote_start`, `remote_stop`, `charge_start`, `preset_name`


## Development

The devcontainer provides a complete Home Assistant environment for developing and testing the Subaru integration.

### Getting Started

1. Open this folder in VS Code
2. When prompted, click "Reopen in Container" (or run "Remote-Containers: Reopen in Container" from the command palette)
3. Wait for the container to build and start (first time may take several minutes)
4. Run the "Start Home Assistant" task
5. Open your browser to http://localhost:8123
6. Complete the Home Assistant onboarding
7. Go to Configuration → Integrations → Add Integration → Search for "Subaru"
8. Configure the integration with your credentials

### Features

- Full Home Assistant instance running in a container
- Your custom_components/subaru folder is mounted into the container
- Changes to your code are immediately available (will need to restart HA)
- Debug logging enabled for the Subaru integration
- Port 8123 forwarded to your local machine

### Testing Changes

After making changes to your integration code:

1. Go to Developer Tools → YAML in Home Assistant
2. Click "Restart" to restart Home Assistant
3. Your changes will be loaded

### Notes

- The container uses the official Home Assistant devcontainer image
- HA configuration files and logs are stored in `.devcontainer/config` and will persist between container rebuilds
