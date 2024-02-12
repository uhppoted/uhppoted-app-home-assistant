![build](https://github.com/uhppoted/uhppoted-app-home-assistant/workflows/build/badge.svg)

# uhppoted-app-home-assistant

UHPPOTE controller HACS integration for Home Assistant.

(_IN DEVELOPMENT_)

---
The _uhppoted-app-home-assistant_ is something of an awkward fit into the _Home Assistant_ conceptual model - it turns out
an access control system (ACS) has a lot more moving parts than e.g. the average thermostat. Having said which, it is 
functional and usable just not as clean and elegant as one would like. However, it is still in the early alpha stage of
development...

The current version is only really suitable for managing a small home ACS - a couple of controllers with half a dozen doors 
and maybe five or ten or so access cards i.e. not a ginormous mansion or an office building.

---
**Contents**
1. [Installation](#installation)
    - [Alpha release](#alpha-release)
    - [Development version](#development-version)

**Screenshot**

<img width="1024" src="doc/images/screenshot.png">

## Installation

### Alpha Release

**NOTE**: The _Alpha_ release is a first release and is entirely a **use at your own risk/discretion**. It has had
**very limited** testing and you could quite conceivably lock yourself out of your own home. i.e. have a backup 
plan (and/or a fire axe ready). It is also quite likely that you will have to reconfigure your system again with
each new release i.e. it is for the brave and adventurous who like living on the edge.

The installation below is entirely manual and installs the project as a _Home Assistant_ _custom component_.


1. Create the `config/custom_components` subdirectory under the _Home Assistant_ folder, if it does not already
   exist and create the `__init.py__` file:

```
cd <Home Assistant>
mkdir -p config/custom_components
touch config/custom_components/__init.py__
```

2. Download the _.tar.gz_ archive from the [_Releases]() section of the repository and extract it to the
   `config/custom_components` folder under the _Home Assistant_ folder, e.g.:

```
cd <Home Assistant>
cd config/custom_components
tar xvzf uhppoted-app-homeassistant.tar.gz .
```
3. (Optionally), add the default configuration to the `configuration.yaml` file in the `config` folder of
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

4. Start (or restart) _Home Assistant_ and confirm there are no errors in the logs.

5. Configure your UHPPOTE controllers:
   - Open the _Settings_ page
   - From the _Settings_ page, open the _Devices and Services_ page
   - Click on the _Add Integration_ button
   - Search for _uhppoted_
   - Step through the configuration flow to set up the initial system configuration
   - Add the entities to cards on the desktop (an example is show below)


### Development Version

The suggested installation for the development version installs the cloned project as a symbolic link under the 
_Home Assistant_ `config/custom_components` folder. Be warned - the development version changes almost daily and
is completely NOT guaranteed to be any kind of stable. You could quite conceivably lock yourself out of your 
apartment, your house, the planet or possibly the entire galaxy. At the very least expect to have to reconfigure
your system often. You have been warned :-). 

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

