# CHANGELOG

## [0.8.9.3](https://github.com/uhppoted/uhppoted-app-home-assistant/releases/tag/v0.8.9.3) - 2024-12-05

### Added
1. Docker compose scripts.
2. _hacs.json_ file for HACS integration.

### Updated
1. Fixed deprecated TIME_SECONDS units.
2. Fixed deprecated `async_forward_entry_setup`
3. Fixed deprecated `async_config_entry_first_refresh`


## [0.8.9](https://github.com/uhppoted/uhppoted-app-home-assistant/releases/tag/v0.8.9) - 2024-09-06

### Added
1. Implements (optional) support for TCP/IP connections to controllers.

### Updated
1. Fixed support for multiple _uhppoted_ instances.
2. Removed _port_ from config- and option-flow UI (can still be configured in _configuration.yaml_).


## [0.8.8.1](https://github.com/uhppoted/uhppoted-app-home-assistant/releases/tag/v0.8.8.1) - 2024-04-17

### Added
1. Implements 'discovering' off-LAN controllers configured in the _configuration.yaml_ file.

### Updated
1. Reworked `uhppoted` to use controller IP addresses and UDP `sendto`.
2. Reworked `preferred_cards` in _configuration.yaml_ to be a YAML list.
3. Added check for valid'ish event listener address in `set-event-listener.


## [0.8.8](https://github.com/uhppoted/uhppoted-app-home-assistant/releases/tag/v0.8.8) - 2024-03-27

1. Initial release.




