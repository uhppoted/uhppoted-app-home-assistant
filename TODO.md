# TODO

- [ ] Add support for non-local controllers (cf. https://github.com/uhppoted/uhppoted-app-home-assistant/issues/3)
      - [x] Add controllers to _configuration.yaml_
      - [x] Rework controller address to include port
      - [x] config-flow: doors and cards for off LAN controller
            - [x] default to 4 door controllers
            - [x] use addr:port to retrieve cards
      - [x] options-flow: doors and cards for off LAN controller
            - [x] default to 4 door controllers
            - [x] use addr:port to retrieve cards
      - [x] Rework config_driver to return class
            - [x] Rework cards.py to use driver.controllers()
            - [x] Migrate api functions to class and use controllers list internally
                  - [x] controllers
                  - [x] doors
                  - [x] cards
                  - [x] events
                  - [x] store map of controllers to {controller,address,port}
                  - [x] Use address from controllers list
                  - [x] Use timeout from controllers list
                  - [x] Use `None` if address is broadcast address
            - [x] singleton/cached/shared
            - [x] Error: `error retrieving card 8165535 information (timed out)`
            - [x] Error: `error setting controller 706050403 event listener ('str' object has no attribute 'packed'`
      - [ ] Configure operation timeout
      - [ ] Use UDP.sendto in services
      - [ ] README
      - [x] CHANGELOG
      - [ ] Reworked preferred-cards in configuration.yaml as array

- [ ] DataCoordinator
      - [ ] communalize data
            - [ ] RWLock
                  - https://www.oreilly.com/library/view/python-cookbook/0596001673/ch06s04.html
                  - https://docs.python.org/3/library/threading.html#rlock-objects
                  - https://docs.python.org/3/library/threading.html#condition-objects
      - [ ] Handle timeout on startup
      - [ ] Handle timeout on shutdown
      - (?) Reconnect event listener on connection lost (unless being unloaded)

- [ ] _config-flow_
      - [ ] Commonalise config-flow and options-flow
      - [ ] Use _self.options_ struct and _self.configured_ list
      - [ ] Use options for defaults (Ref. https://developers.home-assistant.io/docs/data_entry_flow_index/#defaults--suggestions)
      - (?) Single instance only (https://developers.home-assistant.io/blog/2024/02/26/single-instance-only-manifest-option)

- [ ] Controller
      - [ ] Rework as Device
      - [ ] device_info
      - [ ] entity_category
      - [ ] Name translation
            - https://developers.home-assistant.io/docs/internationalization/core/#entity-state-attributes

- [ ] Doors
      - [ ] Name translation

- [ ] Cards
      - [ ] Name translation
            - https://developers.home-assistant.io/blog/2024/01/19/entity-translations-placeholders/
            - https://developers.home-assistant.io/blog/2023/03/27/entity_name_translations/
            - https://developers.home-assistant.io/docs/internationalization/core/#name-of-entities
            - https://developers.home-assistant.io/docs/internationalization/core/#entity-state-attributes
            - https://developers.home-assistant.io/docs/core/entity/#generic-properties
            - https://community.home-assistant.io/t/how-to-send-translation-arguments-to-the-translation-custom-integration/143965/3
            - https://github.com/home-assistant/core/issues/98993
            - https://community.home-assistant.io/t/translation-issues/657691


## To Be Done

- (?) Only set PIN in _options-flow_
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
12. https://community.home-assistant.io/t/starting-a-websocket-connection-in-async-setup-entry-via-hass-async-create-task-causes-long-startup/464966/5
13. https://community.home-assistant.io/t/creating-persistent-async-tasks/180257
14. Unload
    - https://docs.python.org/3.6/library/weakref.html#weakref.finalize
    - https://docs.python.org/3.6/library/weakref.html#comparing-finalizers-with-del-methods
    - https://docs.python.org/3.6/reference/datamodel.html#object.__del__
    - https://docs.python.org/3/library/asyncio-protocol.html#udp-echo-server
    - https://docs.python.org/3/library/asyncio-stream.html
15. Name translation
    - https://developers.home-assistant.io/docs/core/entity
    - https://github.com/home-assistant/core/issues/98993
    - https://developers.home-assistant.io/docs/core/entity
    - python3 -m script.hassfest
16. https://developers.home-assistant.io/docs/integration_fetching_data/#pushing-api-endpoints
17. Services
    - https://data.home-assistant.io/docs/services
    - https://developers.home-assistant.io/docs/dev_101_services
    - https://community.home-assistant.io/t/registering-a-service/40327/8
    - https://community.home-assistant.io/t/async-register-entity-service-calling-entity-method-from-service-call/240927/2
    - https://github.com/doudz/homeassistant-myjdownloader/blob/master/custom_components/myjdownloader/services.yaml


