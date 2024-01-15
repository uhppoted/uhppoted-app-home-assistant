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
      - [x] Cards
            - [x] configure in pages of 4 or 5 cards
      - [ ] Ad hoc controllers
            - [ ] From configuration.yaml
            - (?) when internal list is empty
      - [ ] Use _self.options_ struct and _self.configured_ list
      - [ ] (somehow) commonalise config-flow and options-flow
      - [ ] Integration icon
      - https://developers.home-assistant.io/docs/dev_101_states/

- [ ] Options flow
      - [ ] Cards
            - [ ] configure in pages of 4 or 5 cards
      - [ ] show menu
            - https://developers.home-assistant.io/docs/data_entry_flow_index/#show-menu


- [ ] Controller
      - [ ] generate unique id in config-/option-flow
      - [ ] Rework as Device
      - [ ] device_info
      - [ ] entity_category
      - [ ] Set default timezone in configuration.yaml

- [ ] Doors
      - [ ] generate unique id in config-/option-flow
      - [x] Rework opened as EventEntity
      - [ ] Rework button as EventEntity
      - [ ] Rework unlocked as EventEntiy
      - [ ] unlock
            - [x] `ControllerDoorUnlock`
            - [ ] Update other entities (data coordinator)
            - [ ] service call
      - [ ] Name translation
            - https://developers.home-assistant.io/docs/core/entity
            - https://github.com/home-assistant/core/issues/98993
            - https://developers.home-assistant.io/docs/core/entity
            - python3 -m script.hassfest
      - [ ] Update on event

- [ ] Cards
      - [x] Only set cardholder in config-flow
      - [x] unique id should allow sharing across uhppoteds
      - [x] sensor:CardInfo
      - [x] sensor:CardHolder
      - [x] datetime:StartDate
      - [x] datetime:EndDate
      - [x] permissions
      - [x] PIN
      - [ ] set max cards in _configuration.yaml_
      - [ ] set preferred cards in _configuration.yaml_
      - [ ] Only set cardholder and (maybe) PIN in options-flow
      - [ ] Enable PIN in configuration.yaml

- [ ] Service
- [ ] Custom card
- [ ] Discovery
- [ ] ACL

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
11. Add card number to Person entity
    - https://community.home-assistant.io/t/request-give-the-ability-to-add-attributes-to-people-entities/297483
    - https://www.home-assistant.io/integrations/person
    - https://community.home-assistant.io/t/is-there-a-way-to-create-custom-attributes-for-entities/142875

