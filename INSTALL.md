## Installation

- [HACS](#hacs)
- [Docker](#docker)
- [Manual Installation](#manual-installation)
- [Building from source](#building-from-source)


### HACS

Installing via [HACS](https://www.hacs.xyz/) is by far the simplest:
1. [Install](https://www.hacs.xyz/docs/use/) the HACS integration.
2. Open the _HACS_ tab in the _Home Assistant_ sidebar. and add the [_uhppoted-app-home-assistant_](https://github.com/uhppoted/uhppoted-app-home-assistant)
   github repository as a custom repository (under the menu).
3. Open the _Settings_ tab in the _Home Assistant_ sidebar.
4. Open the _Devices and Integrations_ section.
5. Select _Add integration_ and choose _uhppoted_.
6. Step through the configuration flow to set up the initial system configuration
7. Add/edit the entities to the desktop.

### Docker

The repository includes a sample _Docker Compose_ [`compose.yml`](https://github.com/uhppoted/uhppoted-app-home-assistant/docker/compose/compose.yml) script.

1. Copy the [`compose.yml`](https://github.com/uhppoted/uhppoted-app-home-assistant/blob/main/docker/compose/compose.yml) 
   to an _install_ folder.
2. Copy the [`configuration.yaml`](https://github.com/uhppoted/uhppoted-app-home-assistant/blob/main/docker/compose/configuration.yaml) 
   file to the _install_ folder.
3. Download and unzip the latest release of _uhppoted-app-home-assistant_ from the
   [Releases](https://github.com/uhppoted/uhppoted-app-home-assistant/releases) page to the install folder.
4. Edit the `compose.yml` file as required.
5. Edit the configuration.yaml file as required.
6. Run `docker compose up` to start _Home Assistant_ in _console_ mode.
7. Open the _Settings_ tab in the _Home Assistant_ sidebar.
8. Open the _Devices and Integrations_ section.
9. Select _Add integration_ and choose _uhppoted_.
10. Step through the configuration flow to set up the initial system configuration
11. Add/edit the entities to the desktop.

### Manual Installation

The installation below is entirely manual and installs the project as a _Home Assistant_ _custom component_.


1. Create the `config/custom_components` subdirectory under the _Home Assistant_ folder (if it does not already
   exist) and create the `__init.py__` file:

```
cd <Home Assistant>
mkdir -p config/custom_components
touch config/custom_components/__init.py__
```

2. Download the _.tar.gz_ archive from the [_Releases_]() section of the repository (or the most recent [nightly build](https://github.com/uhppoted/uhppoted-app-home-assistant/actions/workflows/nightly.yaml)) and extract it to the `config/custom_components` folder under 
the _Home Assistant_ folder, e.g.:

```
cd <Home Assistant>
cd config/custom_components
tar xvzf uhppoted-app-homeassistant.tar.gz .
```
3. _(Optionally)_, add the default configuration to the `configuration.yaml` file in the `config` folder of
   _Home Assistant_, e.g.:
```
...
uhppoted:
    bind_address: 192.168.1.100
    broadcast_address: 192.168.1.255:60000
    listen_address: 192.168.1.100:60001
    timezone: LOCAL
    debug: false
    max_cards: 10
    preferred_cards: 
        - 10058400
        - 10058401
    card_PINs: false
    controllers_poll_interval: 30
    doors_poll_interval: 30
    cards_poll_interval: 30
    events_poll_interval: 30
...
```

4. Start (or restart) _Home Assistant_ and confirm there are no errors in the logs.

5. Configure your UHPPOTE controllers:
   - Open the _Settings_ page
   - From the _Settings_ page, open the _Devices and Services_ page
   - Click on the _Add Integration_ button
   - Search for _uhppoted_
   - Step through the configuration flow to set up the initial system configuration
   - Add the entities to cards on the desktop (examples in the screenshots above)


### Building from source

The suggested installation for the development version installs the cloned project as a symbolic link under the 
_Home Assistant_ `config/custom_components` folder. Be warned - the development version changes almost daily and
is completely NOT guaranteed to be any kind of stable. You could quite conceivably lock yourself out of your 
apartment, your house, the planet or possibly the entire galaxy. At the very least expect to have to reconfigure
your system often. You have been warned :-). 

1. Clone the _uhppoted-app-home-assistant_ repo to a folder that is **NOT** _under_ the _Home Assistant_ folder, e.g.:

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
    timezone: LOCAL
    debug: false
    max_cards: 10
    preferred_cards: 
        - 10058400
        - 10058401
    card_PINs: false
    controllers_poll_interval: 30
    doors_poll_interval: 30
    cards_poll_interval: 30
    events_poll_interval: 30
...
```
