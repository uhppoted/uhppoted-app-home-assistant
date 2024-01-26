# TODO

- [ ] Shutdown while waiting for controller response
      - e.g. if simulator is off
      - (?) asyncio maybe
      - (?) move from polled to event model
      - https://community.home-assistant.io/t/hass-async-create-task/428301
```
TimeoutError: timed out
^C2023-11-29 12:44:52.365 ERROR (MainThread) [root] Uncaught exception
...               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyboardInterrupt

```

- [ ] _config-flow_
      - [ ] Use _self.options_ struct and _self.configured_ list
      - [ ] (somehow) commonalise config-flow and options-flow
      - [ ] Integration icon
      - https://developers.home-assistant.io/docs/dev_101_states/

- [x] _options-flow_

- [ ] DataCoordinator
      - [ ] parallelize requests
      - [ ] communalize coordinators/data
      - [x] getters
      - [ ] events
            - [x] DoorOpened
            - [ ] DoorUnlocked
            - [ ] DoorButtonPressed
            - [ ] CardSwipeEvent
            - [ ] AccessEvent
      - [ ] setters
            - await self.coordinator.async_request_refresh()
            - [ ] ControllerDateTime
            - [ ] DoorDelay
            - [ ] DoorMode
            - [ ] DoorUnlock
            - [ ] CardStartDate
            - [ ] CardEndDate
            - [ ] CardPin
            - [ ] CardPermission

- [ ] Controller
      - [ ] Rework as Device
      - [ ] device_info
      - [ ] entity_category
      - [ ] Set default timezone in configuration.yaml
      - [ ] Name translation

- [ ] Doors
      - [ ] unlock
            - [x] `ControllerDoorUnlock`
            - [ ] Update other entities (data coordinator)
                  - await self.coordinator.async_request_refresh()
                  - https://developers.home-assistant.io/docs/integration_fetching_data
            - [ ] service call
      - [ ] Name translation
            - https://developers.home-assistant.io/docs/core/entity
            - https://github.com/home-assistant/core/issues/98993
            - https://developers.home-assistant.io/docs/core/entity
            - python3 -m script.hassfest
      - [ ] Update on event

- [ ] Cards
      - [ ] set max cards in _configuration.yaml_
      - [ ] set preferred cards in _configuration.yaml_
      - [ ] Enable PIN in configuration.yaml
      - [ ] Name translation
      - (?) Only set PIN in _options-flow_

- [ ] Service

## ToDo

- [ ] Custom card
- [ ] Discovery
      - https://developers.home-assistant.io/docs/data_entry_flow_index/#initializing-a-config-flow-from-an-external-source
- [ ] Icon
      - https://developers.home-assistant.io/blog/2020/05/08/logos-custom-integrations/
      - https://smarthomescene.com/guides/how-to-add-custom-icons-in-home-assistant
      - https://www.reddit.com/r/homeassistant/comments/lqoxoy/how_can_i_use_custom_images_for_icons/
- [ ] ACL
- [ ] HACS
      - Python wheel repo (https://developers.home-assistant.io/blog/2020/05/08/logos-custom-integrations)
      - Icon (https://developers.home-assistant.io/blog/2020/05/08/logos-custom-integrations)
- [ ] Ad hoc controllers
      - [ ] From configuration.yaml
      - (?) when internal list is empty

## Notes

1.  https://www.home-assistant.io/integrations/python_script
2.  https://github.com/AlexxIT/PythonScriptsPro
3.  https://aarongodfrey.dev/home%20automation/building_a_home_assistant_custom_component_part_1
4.  https://stackoverflow.com/questions/57819352/docker-desktop-for-macos-cant-add-usr-local-folder-in-preferences-file-sharing
5.  https://www.reddit.com/r/homeassistant/comments/xyloo0/how_do_i_arrange_the_cards_in_a_way_i_want
6.  https://dev.to/adafycheng/write-custom-component-for-home-assistant-4fce
7.  https://community.home-assistant.io/t/optionsflowhandler-single-select-radio-buttons/610623
8.  https://community.home-assistant.io/t/how-do-you-modify-configuration-of-integrations-its-impossible/445070/6
9.  https://community.home-assistant.io/t/config-flow-how-to-update-an-existing-entity/522442/5
10. https://community.home-assistant.io/t/configflowhandler-and-optionsflowhandler-managing-the-same-parameter/365582/10
11. Add card number to Person entity
    - https://community.home-assistant.io/t/request-give-the-ability-to-add-attributes-to-people-entities/297483
    - https://www.home-assistant.io/integrations/person
    - https://community.home-assistant.io/t/is-there-a-way-to-create-custom-attributes-for-entities/142875

