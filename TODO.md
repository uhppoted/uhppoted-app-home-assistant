# TODO

- [ ] get/set-antipassback: 
      - remove #FIXME when uhppoted-lib-python updated (cf. https://github.com/uhppoted/uhppoted/issues/60)
      - bump version to 0.8.11

- [x] Fix deprecation warning (cf. https://github.com/uhppoted/uhppoted-app-home-assistant/issues/15)
- [x] Decorated events door lookup error (cf. https://github.com/uhppoted/uhppoted-app-home-assistant/issues/17#event-17118124970)
- [x] anti-passback (cf. https://github.com/uhppoted/uhppoted/issues/60)
- [x] Weird timeout behaviour (cf. https://github.com/uhppoted/uhppoted-app-home-assistant/issues/18)
   - [x] background fetch queue
   - [x] cache

- [ ] Decorate card swipe event (cf. https://github.com/uhppoted/uhppoted-app-home-assistant/issues/13)
       - [x] fire card.swipe.decorated event
       - [ ] opt-in/out in configuration.yaml/config-flow

- [ ] decorated events
       - (?) per-card swipe events
       - [ ] automation to handle card.swipe.decorated event
       - [ ] add automation to config-flow
       - [ ] Lovelace card to display events
       - [ ] add Lovelace card to config-flow

- [ ] Cache
      - store controller + card in coordinator and collate presented state from that

- [ ] https://www.hacs.xyz/docs/publish/action/
- [ ] (eventually) remove `controllers` from driver

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
      - [ ] automatically skip last step if there are no cards configured (or on the controller)
            (maybe display note)

- [ ] options-flow
      - [ ] automatically skip last step if there are no cards configured (or on the controller)
            (maybe display note)

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

- (?) per-controller interlock/anti-passback opt-in
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


