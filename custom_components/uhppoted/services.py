from __future__ import annotations
from collections import deque

import logging

_LOGGER = logging.getLogger(__name__)

from .const import ATTR_DOOR


def unlock_door(call):
    _LOGGER.info('service call:unlock-door', call.data)

    print('>>>>>>>>>>>>>>>>>>>>', type(call))
    # print(vars(call))

    if ATTR_DOOR in call.data:
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> WOOOT ", call.data.get(ATTR_DOOR, None))

    # name = call.data.get(ATTR_NAME, DEFAULT_NAME)
    #
    # hass.states.set("hello_service.hello", name)
