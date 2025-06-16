# CHANGELOG

## Unreleased

### Added
1. Added (optional) _controller interlock_ settting to manage controller door interlocks.
2. Added (optional) _controller anti-passback_ settting to manage controller card anti-passback.

### Updated
1. Fixed logic around request timeout initialisation.
2. Removed cardholder name from card start.
3. Added cache and background queue to mitigate unavailability issues when running
   virtualized (Docker/Proxmox).


## [0.8.10.3](https://github.com/uhppoted/uhppoted-app-home-assistant/releases/tag/v0.8.10.3) - 2025-04-05

### Updated
1. Fired `uhppoted.card.swipe.decorated` event for all card events.
2. Added (provisional) `card.configured` field to `uhppoted.card.swipe.decorated`
3. Included unit tests in github workflow.

## [0.8.10.2](https://github.com/uhppoted/uhppoted-app-home-assistant/releases/tag/v0.8.10.2) - 2025-04-03

### Updated
1. Fixed bug in door lookup for decorated event `uhppoted.card.swipe.decorated`.

### Notes
1. As from the next _major_ release a minimum version of 2025.1 (updated _options-flow_ behaviour)


## [0.8.10.1](https://github.com/uhppoted/uhppoted-app-home-assistant/releases/tag/v0.8.10.1) - 2025-03-31

### Added
1. Added decorated event `uhppoted.card.swipe.decorated`.
2. Added check for HAVERSION < 2024.11.99' for deprecated _options-flow_ behaviour.


## [0.8.10](https://github.com/uhppoted/uhppoted-app-home-assistant/releases/tag/v0.8.10) - 2025-01-30

### Added
1. Bumped `uhppoted` dependency to v0.8.10.

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




