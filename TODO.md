# TODO

1. _github_ workflow
2. README
3. Install
4. Icon
   - https://developers.home-assistant.io/blog/2020/05/08/logos-custom-integrations/
   - https://smarthomescene.com/guides/how-to-add-custom-icons-in-home-assistant
   - https://www.reddit.com/r/homeassistant/comments/lqoxoy/how_can_i_use_custom_images_for_icons/
5. Shutdown while waiting for controller response
```
TimeoutError: timed out
^C2023-11-29 12:44:52.365 ERROR (MainThread) [root] Uncaught exception
...               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyboardInterrupt

```

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
            - [ ] Multiple doors
            - [ ] Make bind, broadcast, etc step optional
            - [ ] Integration icon
            - [ ] Set integration name to controller name
            - [ ] PLATFORM_SCHEMA
            - 201020304
            - 303986753
            - 405419896
            - https://developers.home-assistant.io/docs/dev_101_states/

      - [ ] Entities
            - [x] Figure out entity IDs for multiple controllers
            - [x] ID
            - [x] address
            - [x] datetime
                  - (?) Derive from TimeEntity
                  - [ ] Handle controller without valid date/time
```
Traceback (most recent call last):
  File "sensor.py", line 274, in async_update
    response = self.uhppote.get_time(controller)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "uhppote.py", line 111, in get_time
    return decode.get_time_response(reply)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "decode.py", line 107, in get_time_response
    unpack_datetime(packet, 8),
    ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "decode.py", line 1159, in unpack_datetime
    return datetime.datetime.strptime(bcd, '%Y%m%d%H%M%S')
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "_strptime.py", line 568, in _strptime_datetime
    tt, fraction, gmtoff_fraction = _strptime(data_string, format)
                                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "_strptime.py", line 349, in _strptime
    raise ValueError("time data %r does not match format %r" %
ValueError: time data '20000000000000' does not match format '%Y%m%d%H%M%S'
2023-11-29 11:37:29.754 ERROR (MainThread) [custom_components.uhppoted.sensor] error retrieving controller status
```
            - [ ] door
                  - [x] open/locked/button sensor
                  - [x] seperate open/locked/pressed sensors
                  - [ ] delay
                  - [ ] mode
                  - [ ] string translation
                  - [ ] update on event

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
