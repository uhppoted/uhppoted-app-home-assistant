# TODO

```
Exception ignored in: <function Coordinators.__del__ at 0x11dfc4540>
Traceback (most recent call last):
  File "/Users/tonyseebregts/Development/uhppote/hass/config/custom_components/uhppoted/coordinators/coordinators.py", line 91, in __del__
    self.unload()
  File "/Users/tonyseebregts/Development/uhppote/hass/config/custom_components/uhppoted/coordinators/coordinators.py", line 29, in unload
    coordinators._unload()
  File "/Users/tonyseebregts/Development/uhppote/hass/config/custom_components/uhppoted/coordinators/coordinators.py", line 97, in _unload
    self._events.unload()
  File "/Users/tonyseebregts/Development/uhppote/hass/config/custom_components/uhppoted/coordinators/events.py", line 152, in unload
    self._listener.close()
  File "/Users/tonyseebregts/Development/uhppote/hass/config/custom_components/uhppoted/coordinators/events.py", line 112, in close
    self._transport.close()
  File "/Users/tonyseebregts/opt/miniconda3/envs/hass/lib/python3.11/asyncio/selector_events.py", line 860, in close
    self._loop.call_soon(self._call_connection_lost, None)
  File "/Users/tonyseebregts/opt/miniconda3/envs/hass/lib/python3.11/asyncio/base_events.py", line 761, in call_soon
    self._check_closed()
  File "/Users/tonyseebregts/opt/miniconda3/envs/hass/lib/python3.11/asyncio/base_events.py", line 519, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
```

- [x] Shutdown while waiting for controller response

- [ ] DataCoordinator
      - [ ] Handle timeout on startup
      - [x] parallelize requests
      - [x] communalize coordinators
      - [ ] communalize data
            - [ ] optimization: update global controller status from event
      - [x] getters
      - [x] setters
      - [x] intervals from _configuration.yaml_
      - [x] events
            - [ ] Reconnect on connection lost 
                  - Unless being unloaded!

- [ ] _config-flow_
      - [ ] Use _self.options_ struct and _self.configured_ list
      - [ ] (somehow) commonalise config-flow and options-flow
      - [ ] Integration icon

- [ ] Controller
      - [ ] Set default timezone in configuration.yaml
      - [ ] Rework as Device
      - [ ] device_info
      - [ ] entity_category
      - [ ] Name translation

- [ ] Doors
      - [ ] unlock service call
            - (?) register as 'unlock-gryffindor'
            - [ ] services.yaml
`2024-02-28 12:01:43.027 WARNING (SyncWorker_2) [homeassistant.helpers.service] Unable to find services.yaml for the uhppoted integration`
            - [ ] icon (async_register_entity_service)
            - [ ] Remove (https://github.com/doudz/homeassistant-myjdownloader/blob/master/custom_components/myjdownloader/__init__.py)
```
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    # remove services
    hass.services.async_remove(DOMAIN, SERVICE_RESTART_AND_UPDATE)
```
            
            - https://data.home-assistant.io/docs/services
            - https://developers.home-assistant.io/docs/dev_101_services
            - https://community.home-assistant.io/t/registering-a-service/40327/8
            - https://community.home-assistant.io/t/async-register-entity-service-calling-entity-method-from-service-call/240927/2
            - https://github.com/doudz/homeassistant-myjdownloader/blob/master/custom_components/myjdownloader/services.yaml

```
service: uhppoted.unlock_le_door
data: {}
target:
  entity_id: button.uhppoted_door_slytherin_unlock
```

      - [ ] Name translation

- [ ] Cards
      - [x] set max cards in _configuration.yaml_
      - [x] set preferred cards in _configuration.yaml_
      - [x] Enable PIN in configuration.yaml
      - [ ] Name translation

- [ ] Service

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
