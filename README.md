![build](https://github.com/uhppoted/uhppoted-app-home-assistant/workflows/build/badge.svg)
![nightly](https://github.com/uhppoted/uhppoted-app-home-assistant/workflows/nightly/badge.svg)

# uhppoted-app-home-assistant

UHPPOTE controller custom component for Home Assistant.

Development status: _ALPHA_

---
_uhppoted-app-home-assistant_ is an experimental _Home Assistant_ custom component for the UHPPOTE access controllers,
leveraging the [_uhppoted-lib-python_](https://github.com/uhppoted/uhppoted-lib-python) library. It turns out that an access
control system has quite a lot more moving parts than e.g. your average thermostat, and the current implementation, 
although functional and usable, is intended more for the (brave) early adopter.

The current version is most suited to a small'ish home ACS i.e. a couple of controllers with half a dozen
doors and maybe a ten or so access cards - so, not e.g. a large mansion, minor palace [~~or office building~~](https://github.com/uhppoted/uhppoted-app-home-assistant/issues/1).

**Contents**
1. [Screenshots](#screenshots)
2. [Installation](#installation)
3. [Configuration](#configuration)
    - [Entities](#entities)
       - [controllers](#controllers)
       - [doors](#doors)
       - [cards](#cards)
    - [Off-LAN controllers](#off-lan-controllers)
    - [_configuration.yaml_](#configurationyaml)
4. [Service API](#service-api)
   - [`unlock-door`](#unlock-door)
   - [`add-card`](#add-card)
   - [`delete-card`](#delete-card)
5. [Decorated events](#decorated-events)
6. [Notes](#notes)
   - [Docker](#docker)


---
**Screenshots**

<img width="800" src="doc/images/controllers.png">

---
<img width="800" src="doc/images/doors.png">

---
<img width="800" src="doc/images/cards.png">

## Release Notes

### Current Release

## [0.9.0](https://github.com/uhppoted/uhppoted-app-home-assistant/releases/tag/v0.9.0) - 2025-12-16

1. Reworked to use _uhppoted-lib-python_ _async_ implementation.
2. Fixed incorrect handling of _address in use_ errors for event listener.
3. Bumped `uhppoted` lib dependency to v0.8.11.2.
4. Added _event listener_ disable option to _configuration.yaml_.
5. Reworked to use HA data when setting card start/end date, PIN or permissions.
6. Reduced the amount of _uhppoted_ driver logging.
7. Added '<none>' to _option-flow_ event listener address list.
8. Optimised door entity updates.

## Installation

### Alpha Release

**NOTE**: The _Alpha_ release is entirely **use at your own risk/discretion**. It is functional but not even vaguely pretty and
is a long way from finished. It has had **very limited** testing - nobody has as yet reported being locked out of their own home
but that may just be because it wasn't late at night and pouring with rain, but please do have a backup plan (which may or may
not include a fire axe). It is also reasonably likely that future releases may require you to reconfigure your system again i.e.
it is for the brave and adventurous who enjoy living on the edge.

Installing via [HACS](https://www.hacs.xyz) is by far the simplest:

1. [Install](https://www.hacs.xyz/docs/use/) the HACS integration.
2. Open the _HACS_ tab in the _Home Assistant_ sidebar. and add the 
   [_uhppoted-app-home-assistant_](https://github.com/uhppoted/uhppoted-app-home-assistant)
   github repository as a custom repository (under the _Home Assistant Community Store_ menu).
3. Restart _Home Assistant_ to complete the initial installation.
4. Open the _Settings_ tab in the _Home Assistant_ sidebar.
5. Open the _Devices and Integrations_ section.
6. Select _Add integration_ and choose _uhppoted_.
7. Step through the configuration flow to set up the initial system configuration
8. Add/edit the entities to the desktop.
9. You may need to restart _Home Assistant_ after completing the initial system configuration.

Alternative installation methods are described in the [Installation Guide](INSTALL.md):
- [Docker](INSTALL.md#docker)
- [Manual installation](INSTALL.md#manual-installation)
- [Building from source](INSTALL.md#building-from-source)

## Configuration

1. Open the _Home Assistant/Settings_ page.
2. Open the _Devices & Services_ page.
3. Select the _Integrations_ tab and then select _Add integration_.
4. Search for _uhppoted_ and open the _uhppoted_ custom integration item.
5. Enter the bind, broadcast, listen addresses and (optionally) enable debug.
6. Select the controllers to manage with _Home Assistant_ from the list of controllers found on the LAN.
7. For each controller:
   - choose a unique name e.g. _Main_, _Controller #1_, etc.
   - _(optional)_ set the controller IP address
   - _(optional)_ set the controller protocol (defaults to _UDP_).
   - _(optional)_ set the controller timezone (defaults to _Local_)
8. For each controller, select the doors to manage with _Home Assistant_
9. For each selected door:
   - choose a unique name e.g. _Entrance_, _Garage_, _Man Cave_
10. Select the cards to be managed by _Home Assistant_ from the list of cards found on the controllers
11. For each selected card:
    - enter the name of the person (or other entity) using that card
12. On completion of configuration the _uhppoted_ service will create all the entities for the controllers, doors and
    cards.
13. Add selected information to the dashboard from the entities listed below.
   
### Entities

#### Controllers

1. `uhppoted.controller.{controller}.info`
2. `uhppoted.controller.{controller}.datetime`
3. `uhppoted.controller.{controller}.event`
4. `uhppoted.controller.{controller}.interlock`
5. `uhppoted.controller.{controller}.antipasback`


#### Doors

1.  `uhppoted.door.{door}.info`
2.  `uhppoted.door.{door}.open`
3.  `uhppoted.door.{door}.lock`
4.  `uhppoted.door.{door}.button`
5.  `uhppoted.door.{door}.mode`
6.  `uhppoted.door.{door}.delay`
7.  `uhppoted.door.{door}.unlock`
8.  `uhppoted.door.{door}.open.event`
9.  `uhppoted.door.{door}.button.event`
10. `uhppoted.door.{door}.unlocked.event`

#### Cards

1. `uhppoted.card.{card}.info`
2. `uhppoted.card.{card}.cardholder`
3. `uhppoted.card.{card}.start-date`
4. `uhppoted.card.{card}.end-date`
5. `uhppoted.card.{card}.{door}`
6. `uhppoted.card.{card}.pin`
7. `uhppoted.card.{card}.swipe.event`


### Off-LAN controllers

Controllers that are not on the local LAN segment are not discoverable and have to be added manually to the
_uhppoted_ section of the _Home Assistant_ `configuration.yaml` file (in the _config_ folder), e.g.:
```
...
uhppoted:
    ...
    controllers:
        - 
            controller: 504030201
            address: 192.168.1.100
        - 
            controller: 605040302
            address: 192.168.1.100
            port: 60000
            protocol: UDP
        - 
            controller: 706050403
            address: 192.168.1.100
            port: 54321
            protocol: TCP
            timeout: 0.56
...
```

The `controllers` subsection is a YAML array/list of controllers with the following properties;
- `controller`: controller serial number
- `address`: controller IPv4 address
- `port`: _(optional)_ controller UDP port (defaults to 60000)
- `protocol`: _(optional)_ controller transport protocol (UDP or TCP - defaults to UDP)
- `timeout`: _(optional)_ controller timeout (default to the global uhppoted timeout of 2.5s)

The controllers listed in `configuration.yaml` are included in the list of _discovered_ controllers and
can be configured from the _Home Assistant_ user interface in the same way as local controllers i.e. controllers
listed in `configuration.yaml` are **NOT** automatically added to the list of managed controllers - 
they do still need to be configured.


### _configuration.yaml_

The operational configuration can be customised by the _(entirely optional)_ setttings in the _uhppoted_ section
of the _Home Assistant_ `configuration.yaml` file (in the _Home Assistant_ `config` folder). The full list of
configurable settings comprises:

| Setting                       | Description                                                      | Default value     |
|-------------------------------|------------------------------------------------------------------|-------------------|
| `bind_address`                | Default IPv4 UDP bind address                                    | `0.0.0.0`         |
| `broadcast_address`           | Default IPv4 UDP broadcast address                               | `255.255.255.255` |
| `listen_address`              | Default IPv4 UDP listen address (for events)                     | `0.0.0.0`         |
| `timezone`                    | Default controller timezone                                      | local             |
| `timeout`                     | Default timeout for controller requests/responses (seconds)      | 2.5               |
| `retry_delay`                 | Default delay before retrying a failed fetch (seconds)           | 120               |
| `debug`                       | Enables/disables logging of controller packets                   | false             |
| `max_cards`                   | Max. cards to 'discover' for configuration                       | 10                |
| `preferred_cards`             | YAML list of of cards that take priority for _'discovery'_       | - none -          |
| `card_PINs`                   | Enables/disables retrieving/setting card PINs                    | false             |
| `controllers_poll_interval`   | Interval at which to fetch controller information (seconds)      | 30                |
| `doors_poll_interval`         | Interval at which to fetch door information (seconds)            | 30                |
| `cards_poll_interval`         | Interval at which to fetch card information (seconds)            | 30                |
| `events_poll_interval`        | Interval at which to fetch missed/synthetic events (seconds)     | 30                |
| `controllers`                 | List of off-LAN controllers (see above)                          | -none-            |
| `cache.enabled`               | Enables the entity and background task queue                     | true              |
| `cache.expiry.controller`     | Cache expiry time for cached controller entities (seconds)       | 300  (5 minutes)  |
| `cache.expiry.listener`       | Cache expiry time for cached event listener (seconds)            | 600  (10 minutes) |
| `cache.expiry.datetime`       | Cache expiry time for cached controller date/time (seconds)      | 300  (5 minutes)  |
| `cache.expiry.door`           | Cache expiry time for cached door entities (seconds)             | 600  (10 minutes) |
| `cache.expiry.card`           | Cache expiry time for cached card entities (seconds)             | 900  (15 minutes) |
| `cache.expiry.status`         | Cache expiry time for cached controller status (seconds)         | 120  (2 minutes)  |
| `cache.expiry.interlock`      | Cache expiry for cached controller door interlock mode (seconds) | 900  (15 minutes) |
| `cache.expiry.antipassback`   | Cache expiry time for cached anti-passback mode (seconds)        | 900  (15 minutes) |
| `cache.expiry.event`          | Cache expiry time for cached event entities (seconds)            | 1800 (30 minutes) |
| `events.listener.enabled`     | Enables/disables the event listener                              | true              |
| `events.listener.max_backoff` | Maximum backoff (seconds) when retrying the event listener       | 1800 (30 minutes) |
|                               |                                                                  |                   |
| `events.cards.enabled`        | Opt-out for card swiped events                                   | true              |
| `events.doors.enabled`        | Opt-out for door events                                          | true              |
| `events.controllers.enabled`  | Opt-out for controller events                                    | true              |
|                               |                                                                  |                   |
| `persistend.entities`         | Opt-in list for controller door interlocks                       | -none-            |


e.g.
```
uhppoted:
    bind_address: 192.168.1.100
    broadcast_address: 192.168.1.255:60000
    listen_address: 192.168.1.100:60001
    debug: false
    timezone: CEST
    timeout: 1.23
    retry_delay: 90
    max_cards: 7
    preferred_cards: 
        - 10058400
        - 10058401
    card_PINs: true
    controllers_poll_interval: 29
    doors_poll_interval: 31
    cards_poll_interval: 33
    events_poll_interval: 35
    controllers:
        - 
            controller: 504030201
            address: 192.168.1.100
            port: 54321
        - 
            controller: 605040302
            address: 192.168.1.100
            port: 54321
        - 
            controller: 706050403
            address: 192.168.1.100
            port: 54321
            protocol: TCP
            timeout: 0.56
    cache:
        enabled: true
        expiry:
            controller: 90
            listener: 900
            datetime: 120
            door: 180
            card: 180
            status: 120
            interlock: 600
            antipassback: 600
            event: 3600
    events:
        listener:
            enabled: true
            max_backoff: 300

        cards:
            enabled: true
        doors:
            enabled: true
        controllers:
            enabled: true

    persisted:
        entities:
            - uhppoted.controller.alpha.interlock
            - uhppoted.controller.beta.interlock

```


## Service API

### `unlock-door`

Unlocks a door by name - the name is case- and space-insensitive.

Example:
```
service: uhppoted.unlock_door
data:
  door: Gryffindor
```

### `add-card`

Adds a card to all the controllers configured by the _uhppoted_ service. The card is **not** added to
the list of configured cards - to include the card in the managed cards, open the `CONFIGURE` section 
for the _uhppoted_ service (under _Settings/Devices & Services/uhppoted_).

Example:
```
service: uhppoted.add_card
data:
  card: 10058400
```

### `delete-card`

Delets a card from all the controllers configured by the _uhppoted_ service. The card is **not** removed
from the list of configured cards - to remove the card from the managed cards, open the `CONFIGURE` section 
for the _uhppoted_ service (under _Settings/Devices & Services/uhppoted_).

Example:
```
service: uhppoted.delete_card
data:
  card: 10058400
```

## Decorated events

Decorated events are custom events intended for use with template sensors and automation and include the additional
event information associated with each event.

**NOTE: decorated events fire even if the associated events are disabled in the configuration.yaml.**


### `uhppoted.card.swipe.event.decorated`
Sample event:
```
event_type: uhppoted.card.swipe.decorated
data:
  event:
    index: 74
    timestamp: "2025-03-31 10:54:07"
  card:
    card: 10058400
    name: Hermione
    configured: true
  controller:
    id: 405419896
    name: Alpha
  door:
    id: 1
    name: Gryffindor
  access:
    granted: true
    code: 1
    description: swipe valid
...
```

Sample template sensor:
```
template:
  - trigger:
      - platform: event
        event_type: uhppoted.card.swipe.decorated
    sensor:
      - name: "Card Swipe"
        unique_id: decorated_card_swipe_sensor
        state: "{{ trigger.event.data.controller.id }}.{{trigger.event.data.event.index}}"
        attributes:
          timestamp: "{{ trigger.event.data.event.timestamp }}"
          card:  "#{{ trigger.event.data.card.card | string }}"
          name: "{{ trigger.event.data.card.name }}"
          controller_id: "{{ trigger.event.data.controller.id | string }}"
          controller_name: "{{ trigger.event.data.controller.name }}"
          door_id: "{{ trigger.event.data.door.id }}"
          door_name: "{{ trigger.event.data.door.name }}"
          access_granted: "{{ 'GRANTED' if trigger.event.data.access.granted else 'DENIED' }}"
          access_code: "{{ trigger.event.data.access.code }}"
          access_description: "{{ trigger.event.data.access.description }}"
```

### `uhppoted.door.event.decorated`
Sample event:
```
event_type: uhppoted.door.event.decorated
data:
  event:
    index: 82
    timestamp: "2026-01-06 11:52:55"
    code: 20
    description: push button ok
  controller:
    id: 405419896
    name: Alpha
  door:
    id: 1
    name: Gryffindor
...
```

Sample template sensor:
```
template:
  - trigger:
      - platform: event
        event_type: uhppoted.door.event.decorated
    sensor:
      - name: "Door Event"
        unique_id: uhppoted.door.event.decorated
        state: "{{ trigger.event.data.controller.id }}.{{trigger.event.data.event.index}} {{ trigger.event.data.door.name }}"
        attributes:
          timestamp: "{{ trigger.event.data.event.timestamp }}"
          controller_id: "{{ trigger.event.data.controller.id | string }}"
          controller_name: "{{ trigger.event.data.controller.name }}"
          door_id: "{{ trigger.event.data.door.id }}"
          door_name: "{{ trigger.event.data.door.name }}"
          event_code: "{{ trigger.event.data.event.code }}"
          event_description: "{{ trigger.event.data.event.description }}"

```

### `uhppoted.controller.event.decorated`
Sample event:
```
event_type: uhppoted.controller.event.decorated
data:
  event:
    index: 74
    timestamp: "2026-01-06 11:52:55"
    code: 29
    description: controller reset
  controller:
    id: 405419896
    name: Alpha
...
```

Sample template sensor:
```
template:
  - trigger:
      - platform: event
        event_type: uhppoted.controller.event.decorated
    sensor:
      - name: "Controller Event"
        unique_id: uhppoted.controller.event.decorated
        state: "{{ trigger.event.data.controller.id }}.{{trigger.event.data.event.index}} {{ trigger.event.data.controller.name }}"
        attributes:
          timestamp: "{{ trigger.event.data.event.timestamp }}"
          controller_id: "{{ trigger.event.data.controller.id | string }}"
          controller_name: "{{ trigger.event.data.controller.name }}"
          event_code: "{{ trigger.event.data.event.code }}"
          event_description: "{{ trigger.event.data.event.description }}"

```

## Notes

### Docker

#### UDP

In bridge neworking mode (used on _MacOS_ and _Windows_) the UDP transport in Docker drops UDP replies at a **significantly**
higher rate than typically experienced on a LAN/WAN. In _uhppoted-app-home-assistant_ this manifests as entities going 
intermittently and unecessarily _unavailable_ with a _timeout_ message in the logs. _Host_ mode networking (Linux/RaspberryPi)
doesn't appear to suffer from the same problem.

A cache layer and background scheduling upgrade which mitigates the problem to a more manageable level is included in release 
v0.8.11 - the interim workaround is to configure the controllers to use the TCP transport, if supported (some older 
controllers may not).

Anecdotally, it seems this may also be a problem in _Proxmox_.

#### Shutdown

_HomeAssistant_ needs some time to cleanup and persist the current state - to shutdown cleanly:
```
docker stop -t 30 home-assistant
```

#### Door Interlocks

The UHPPOTE controllers don't provide a `get-door-interlocks` API which makes restoring the state of the _Interlock_ entity across
_Home Assistant_ restarts complicated - in particular, if _Home Assistant_ isn't shutdown properly (e.g. power outage) it may restore
an old state, which is problematic for something like a door interlock.

_uhppoted-app-home-assistant_ takes the following approach:

1. On setting an _Interlock_ entity in the _Home Assistant_ UI, the interlock `mode` is persisted to both the normal _Home Assistant_
   entity state and a _Home Assistant_ store.

2. On startup, _uhppoted-app-home-assistant_ automatically sets the controller door interlock mode provided:
   - the _Interlock_ entity name is listed in the `persisted.entities` section of the _configuration.yaml_.
   - the interlock mode in the restored state matches the interlock mode in the _Home Assistant_ store

By default, _Interlock_ entities are not automatically restored, as being the safer option. To opt-in to restoring _Interlock_ entities,
enable persistence for specific entities in the _configuration.yaml_ file, e.g.

```
    persisted:
        entities:
            - uhppoted.controller.alpha.interlock
            - uhppoted.controller.beta.interlock
```
