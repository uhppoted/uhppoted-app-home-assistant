# TODO

1. _github_ workflow
2. README
3. Install
4. Icon
   - https://developers.home-assistant.io/blog/2020/05/08/logos-custom-integrations/
   - https://smarthomescene.com/guides/how-to-add-custom-icons-in-home-assistant
   - https://www.reddit.com/r/homeassistant/comments/lqoxoy/how_can_i_use_custom_images_for_icons/

- [ ] Controller
      - [ ] Rework as Device

      - [ ] config flow
            - [ ] Rethink using controller ID for unique ID
                  - Do want unique controller IDs
                  - But also need to be able to change controller ID without redoing configuration
            - [x] Get default bind, broadcast, listen from configuration.yaml
            - [x] Validate controller ID
            - [x] (optional) controller address
            - [x] bind, broadcast, listen as optional second step
            - [x] (optional) controller name
            - [ ] Make bind, broadcast, etc step optional
            - [ ] Integration icon
            - [ ] Set integration name to controller name
            - [ ] PLATFORM_SCHEMA
            - 201020304
            - 303986753
            - 405419896
            - https://developers.home-assistant.io/docs/dev_101_states/

      - [ ] Entities
            - [x] ID
            - [x] address
            - [x] datetime
                  - (?) Derive from TimeEntity
            - [x] Figure out entity IDs for multiple controllers
            - [ ] door
                  - [ ] open/closed sensor
                        - [ ] test with real controller
                        - [ ] string translation
                  - [ ] delay
                  - [ ] mode
            - [ ] card
            - [ ] Name translation
                  - https://developers.home-assistant.io/docs/core/entity
                  - https://github.com/home-assistant/core/issues/98993
                  - https://developers.home-assistant.io/docs/core/entity
                  - python3 -m script.hassfest

      - [ ] Service

      - [ ] device_info
      - [ ] entity_category
      - [ ] custom card
      - [ ] discovery

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
