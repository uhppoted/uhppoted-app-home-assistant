import threading

from typing import Dict

class DB:
    _lock: threading.Lock
    _controllers: Dict[int, Dict]
    _doors: Dict[int, Dict]
    _cards: Dict[str, Dict]
    _events: Dict[int, Dict]

    def __init__ (self):
        self._lock = threading.Lock()

        self._controllers = {}
        self._doors = {}
        self._cards = {}
        self._events = {}
