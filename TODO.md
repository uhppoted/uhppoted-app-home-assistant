# TODO

## In Progress

- [ ] Initial setup error:
```
Failed setup, will retry: uhppoted API error 'list' object has no attribute 'get'
```

- [ ] Use uhppoted-lib-python async implementation (cf. https://github.com/uhppoted/uhppoted-app-home-assistant/issues/20)
    - https://developers.home-assistant.io/docs/asyncio_working_with_async
    - [x] set-time
    - [x] set-door-mode
    - [x] set-door-delay
    - [x] open-door
    - [x] set-interlock
    - [x] set-antipassback
    - [x] set-listener
    - [x] record-special-events
    - [x] get-event
        - [ ] # FIXME return cached event if it exists
    - [x] put-card
    - [x] delete-card
    - [x] get-controller
    - [x] get-listener
    - [x] get-time
    - [x] get-door
        - [x] _get-doors::get-door
        - [x] _get-doors::get-controller
    - [x] get-status
    - [ ] get-cards
    - [ ] get-card
    - [ ] get-card-by-index
    - [x] get-interlock
    - [x] get-antipassback
    - [ ] Throttle requests — 50–100 ms between sends helps keep NAT tables sane (apparently)
    - [ ] event-listener `# FIXME reinstate - temporarily removed for async conversion`

- [ ] HA has been getting slower and slower (cf. https://github.com/uhppoted/uhppoted-app-home-assistant/issues/21)
    - [ ] allow 'no event listener'
    - [ ] weird thing with multiple setups after a reconfigure

    - (?) store controller + card in coordinator and collate presented state from that
    - https://developers.home-assistant.io/docs/core/entity/#excluding-state-attributes-from-recorder-history
    - https://www.home-assistant.io/integrations/logger
    - https://community.home-assistant.io/t/make-recorder-logbook-and-history-includes-avaialable-for-editing-on-the-entities-page/212515
    - https://community.home-assistant.io/t/recorder-retention-period-by-entity/267849/5
    - https://www.reddit.com/r/homeassistant/comments/8aj8xg/is_there_a_way_to_prevent_specific_entities_form
    - https://community.home-assistant.io/t/worth-disabling-unused-entities/350068
    - https://community.home-assistant.io/t/how-to-prevent-a-log-entry-when-an-automation-is-executed/255876

- [ ] Improve event handling (cf. https://github.com/uhppoted/uhppoted-app-home-assistant/issues/14)
       - [ ] opt-in/out in configuration.yaml/config-flow
       - (?) per-card swipe events
       - [ ] automation to handle card.swipe.decorated event
       - [ ] add automation to config-flow
       - [ ] Lovelace card to display events
       - [ ] add Lovelace card to config-flow

- [ ] loading on startup
    - task dequeue seems to take forever to start running
- [ ] set-interlock on startup takes forever
- (?) retry set-interlock if not available/not correct
- [ ] fix _controller 405419896 incorrect event listener address (None)_
- [ ] can't seem to disable check/set-listener
- [ ] fix:
```
2025-11-04 19:41:10.930 ERROR (MainThread) [homeassistant] Error doing job: Task exception was never retrieved (None)
home-assistant-stable  | Traceback (most recent call last):
home-assistant-stable  |   File "/config/custom_components/uhppoted/coordinators/events.py", line 58, in _listen
home-assistant-stable  |     transport, protocol = await loop.create_datagram_endpoint(lambda: listener, local_addr=(addr, port))
home-assistant-stable  |                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
home-assistant-stable  |   File "/usr/local/lib/python3.13/asyncio/base_events.py", line 1467, in create_datagram_endpoint
home-assistant-stable  |     raise exceptions[0]
home-assistant-stable  |   File "/usr/local/lib/python3.13/asyncio/base_events.py", line 1451, in create_datagram_endpoint
home-assistant-stable  |     sock.bind(local_address)
home-assistant-stable  |     ~~~~~~~~~^^^^^^^^^^^^^^^
home-assistant-stable  | OSError: [Errno 98] Address in use
```

- [ ] fix - error after reconfiguring
```
2025-11-05 19:48:04.705 ERROR (MainThread) [homeassistant.config_entries] Error unloading entry uhppoted for uhppoted
home-assistant-stable  | Traceback (most recent call last):
home-assistant-stable  |   File "/usr/src/homeassistant/homeassistant/config_entries.py", line 967, in async_unload
home-assistant-stable  |     result = await component.async_unload_entry(hass, self)
home-assistant-stable  |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
home-assistant-stable  |   File "/config/custom_components/uhppoted/__init__.py", line 214, in async_unload_entry
home-assistant-stable  |     Coordinators.unload(entry.entry_id)
home-assistant-stable  |     ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^
home-assistant-stable  |   File "/config/custom_components/uhppoted/coordinators/coordinators.py", line 33, in unload
home-assistant-stable  |     coordinators._unload()
home-assistant-stable  |     ~~~~~~~~~~~~~~~~~~~~^^
home-assistant-stable  |   File "/config/custom_components/uhppoted/coordinators/coordinators.py", line 136, in _unload
home-assistant-stable  |     self._driver.stop(hass)
home-assistant-stable  |                       ^^^^
home-assistant-stable  | NameError: name 'hass' is not defined. Did you mean: 'hash'?
```

- [ ] get-events
```
    home-assistant-stable  | 2025-11-05 19:57:43.399 ERROR (MainThread) [custom_components.uhppoted.coordinators.events] Error fetching events data: uhppoted API error 
```

## TODO

- [ ] https://www.hacs.xyz/docs/publish/action/
- [ ] (eventually) remove `controllers` from driver

- [ ] DataCoordinator
      - [ ] communalise data
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


