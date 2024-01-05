![build](https://github.com/uhppoted/uhppoted-app-home-assistant/workflows/build/badge.svg)

# uhppoted-app-home-assistant

UHPPOTE controller HACS integration for Home Assistant.

### Status

(_IN DEVELOPMENT_)

### Contents

1. [Installation](#installation)
    - [Alpha Release](#alpha-release)
    - [Development version](#developmnet-version)

2. [Configuration](#configuration)


## Installation

### Alpha Release

The suggested installation for the _Alpha_ release installs the `alpha` branch of the cloned project as a symbolic link
under the _Home Assistant_ `config/custom_components` folder. The `alpha` branch is _slightly_ more stable than the `main`
branch.

1. Clone the _uhppoted-app-home-assistant_ repo to a folder that is **NOT* _under_ the _Home Assistant_ folder and
   switch to the _alpha_ branch, e.g.:

```
cd ~/experimental-stuff
git clone https://github.com/uhppoted/uhppoted-app-home-assistant
git switch alpha
```

2. Create the `config/custom_components` subdirectory under the _Home Assistant_ folder, if it does not already
   exist and create the `__init.py__` file:

```
cd <Home Assistant>
mkdir -p config/custom_components
touch config/custom_components/__init.py__
```

3. Create a symbolic link to the _uhppoted-add-home-assistant_ folder in the `config/custom_components` folder.

```
ln -s ~/experimental-stuff/uhppoted-app-home-assistant/custom_components/uhppoted config/custom_components/uhppoted
```

(for _Windows_ users: https://superuser.com/questions/1020821/how-can-i-create-a-symbolic-link-on-windows-10)

4. (Optionally), add the default configuration to the `configuration.yaml` file in the `config` folder of
   _Home Assistant_, e.g.:
```
...
uhppoted:
    bind_address: 192.168.1.100
    broadcast_address: 192.168.1.255:60000
    listen_address: 192.168.1.100:60001
    debug: false
...
```

### Development Version

The suggested installation for the development version installs the cloned project as a symbolic link under the 
_Home Assistant_ `config/custom_components` folder.

1. Clone the _uhppoted-app-home-assistant_ repo to a folder that is **NOT* _under_ the _Home Assistant_ folder, e.g.:

```
cd ~/experimental-stuff
git clone https://github.com/uhppoted/uhppoted-app-home-assistant
```

2. Create the `config/custom_components` subdirectory under the _Home Assistant_ folder, if it does not already
   exist and create the `__init.py__` file:

```
cd <Home Assistant>
mkdir -p config/custom_components
touch config/custom_components/__init.py__
```

3. Create a symbolic link to the _uhppoted-add-home-assistant_ folder in the `config/custom_components` folder.

```
ln -s ~/experimental-stuff/uhppoted-app-home-assistant/custom_components/uhppoted config/custom_components/uhppoted
```

4. (Optionally), add the default configuration to the `configuration.yaml` file in the `config` folder of
   _Home Assistant_, e.g.:
```
...
uhppoted:
    bind_address: 192.168.1.100
    broadcast_address: 192.168.1.255:60000
    listen_address: 192.168.1.100:60001
    debug: false
...
```

## Configuration

1. Open the _Home Assistant/Settings_ page.
2. Open the _Devices & Services_ page.
3. Select the _Integrations_ tab and then select _Add integration_.
4. Search for _uhppoted_ and open the _uhppoted_ custom integration item.
5. Enter the bind, broadcast, listen addresses and (optionally) enable debug.
6. Select the controllers to manage with _Home Assistant_ from the list of controllers found on the LAN.
7. For each controller:
   - choose a unique name e.g. Main, Controller #1, etc.
   - (optionally) set the controller IP address
   - (optionally) set the controller timezone (defaults to _Local_)
8. For each controller, select the doors to manage with _Home Assistant_
9. For each selected door:
   - choose a unique name e.g. Entrance, Garage, Workshop
10. Cards .....
999. Add selected information to the dashboard from the entities listed below.
   
## Entities

### Controllers

1. uhppoted.controller.{controller}.info
2. uhppoted.controller.{controller}.datetime


### Doors

1. uhppoted.door.{door}
2. uhppoted.door.{door}.open
3. uhppoted.door.{door}.lock
4. uhppoted.door.{door}.button
5. uhppoted.door.{door}.mode
6. uhppoted.door.{door}.delay
7. uhppoted.door.{door}.unlock

