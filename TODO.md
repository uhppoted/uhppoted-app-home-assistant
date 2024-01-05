# TODO

- [ ] Shutdown while waiting for controller response
      - (?) asyncio maybe
      - (?) move from polled to event model
      - https://community.home-assistant.io/t/hass-async-create-task/428301
```
TimeoutError: timed out
^C2023-11-29 12:44:52.365 ERROR (MainThread) [root] Uncaught exception
...               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyboardInterrupt

```

- [ ] Config flow
      - [ ] Figure out why _hass_ is using name for unique ID ?????
      - [x] Don't show door page for e.g. Beta if none selected
      - [x] Rework to configure multiple controllers, doors, etc
      - [ ] Cards
      - [ ] Ad hoc controller
            - when internal list is empty
            - address is required
      - [ ] Use _self.options_ struct and _self.configured_ list
      - [ ] (somehow) commonalise config-flow and options-flow
      - [ ] Integration icon
      - https://developers.home-assistant.io/docs/dev_101_states/

- [ ] Options flow
      - [ ] show menu
            - https://developers.home-assistant.io/docs/data_entry_flow_index/#show-menu
      - [x] Rework to configure multiple controllers
      - [x] Check for duplicate controller names
      - [x] Rework to configure multiple doors
      - [x] Remove controller from door entity id
      - [x] Validate controllers
            - [x] Check for duplicate controllers at start and end of section
            - [x] Loop back to start of controllers
            - [x] Allow controller to be removed
      - [x] Validate doors
            - [x] on error, keep the supplied door/controller names
            - [x] Check for duplicate doors at start and end of section
            - [x] Loop back to start of doors
            - [x] Allow door to be removed


- [ ] Controller
      - [ ] Rework as Device
      - [ ] device_info
      - [ ] entity_category
      - [ ] Set timezone in config-flow/configuration.yaml

- [ ] Doors
      - [ ] Rework open/pressed as event entities
      - [ ] unlock
            - [x] `ControllerDoorUnlock`
            - [ ] Update other entities (data coordinator)
      - [ ] Name translation
            - https://developers.home-assistant.io/docs/core/entity
            - https://github.com/home-assistant/core/issues/98993
            - https://developers.home-assistant.io/docs/core/entity
            - python3 -m script.hassfest
      - [ ] Somehow seperate from controller and then just link to controller name
      - [ ] Update on event

- [ ] Cards
      - (?) Add card number to Person entity
            - https://community.home-assistant.io/t/request-give-the-ability-to-add-attributes-to-people-entities/297483
            - https://www.home-assistant.io/integrations/person
            - https://community.home-assistant.io/t/is-there-a-way-to-create-custom-attributes-for-entities/142875
- [ ] Service
- [ ] Custom card
- [ ] Discovery

- [ ] README
      - [ ] Installation

- [ ] Icon
      - https://developers.home-assistant.io/blog/2020/05/08/logos-custom-integrations/
      - https://smarthomescene.com/guides/how-to-add-custom-icons-in-home-assistant
      - https://www.reddit.com/r/homeassistant/comments/lqoxoy/how_can_i_use_custom_images_for_icons/

- [ ] HACS
      - Python wheel repo (https://developers.home-assistant.io/blog/2020/05/08/logos-custom-integrations)
      - Icon (https://developers.home-assistant.io/blog/2020/05/08/logos-custom-integrations)

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

