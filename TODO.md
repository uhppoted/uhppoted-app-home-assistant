# TODO

```
201020304
303986753
405419896
```

1. _github_ workflow
2. README
3. Install
4. Icon
   - https://developers.home-assistant.io/blog/2020/05/08/logos-custom-integrations/
   - https://smarthomescene.com/guides/how-to-add-custom-icons-in-home-assistant
   - https://www.reddit.com/r/homeassistant/comments/lqoxoy/how_can_i_use_custom_images_for_icons/
5. Shutdown while waiting for controller response
   - asyncio maybe ????
     - https://community.home-assistant.io/t/hass-async-create-task/428301
```
TimeoutError: timed out
^C2023-11-29 12:44:52.365 ERROR (MainThread) [root] Uncaught exception
...               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyboardInterrupt

```

- [ ] Controller
      - [ ] Rework as Device
      - [ ] device_info
      - [ ] entity_category
      - [x] Figure out entity IDs for multiple controllers
      - [x] ID
      - [x] address
      - [x] datetime
            - [x] Handle controller without valid date/time
            - (?) Derive from TimeEntity
            - [ ] Name translation
                  - https://developers.home-assistant.io/docs/core/entity
                  - https://github.com/home-assistant/core/issues/98993
                  - https://developers.home-assistant.io/docs/core/entity
                  - python3 -m script.hassfest

      - [ ] config flow
            - [ ] Rethink using controller ID for unique ID
                  - Do want unique controller IDs
                  - But also need to be able to change controller ID without redoing configuration
            - [x] Get default bind, broadcast, listen from configuration.yaml
            - [x] Validate controller ID
            - [x] (optional) controller address
            - [x] bind, broadcast, listen as optional second step
            - [x] (optional) controller name
            - [ ] Multiple doors
            - [ ] Make bind, broadcast, etc step optional
            - [ ] Integration icon
            - [ ] Set integration name to controller name
            - [ ] PLATFORM_SCHEMA
            - https://developers.home-assistant.io/docs/dev_101_states/

- [ ] Doors
      - [x] open/locked/button sensor
      - [x] seperate open/locked/pressed sensors
      - [x] mode
      - [ ] delay
      - [ ] Seperate from controller
      - [ ] Config flow
      - [ ] Link to controller
      - [ ] string translation
      - [ ] update on event

- [ ] Cards
- [ ] Service
- [ ] Custom card
- [ ] Discovery

- [ ] Add card number to Person entity
      - https://community.home-assistant.io/t/request-give-the-ability-to-add-attributes-to-people-entities/297483
      - https://www.home-assistant.io/integrations/person
      - https://community.home-assistant.io/t/is-there-a-way-to-create-custom-attributes-for-entities/142875

- [ ] HACS
      - Python wheel repo (https://developers.home-assistant.io/blog/2020/05/08/logos-custom-integrations)
      - Icon (https://developers.home-assistant.io/blog/2020/05/08/logos-custom-integrations)

## Notes

1. https://www.home-assistant.io/integrations/python_script
2. https://github.com/AlexxIT/PythonScriptsPro
3. https://aarongodfrey.dev/home%20automation/building_a_home_assistant_custom_component_part_1
4. https://stackoverflow.com/questions/57819352/docker-desktop-for-macos-cant-add-usr-local-folder-in-preferences-file-sharing
5. https://www.reddit.com/r/homeassistant/comments/xyloo0/how_do_i_arrange_the_cards_in_a_way_i_want
6. https://dev.to/adafycheng/write-custom-component-for-home-assistant-4fce
