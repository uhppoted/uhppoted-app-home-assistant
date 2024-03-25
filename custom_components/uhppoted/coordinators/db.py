import threading

from typing import Dict


class DB:
    _lock: threading.Lock
    _controllers: Dict[int, Dict]
    _doors: Dict[str, Dict]
    _cards: Dict[int, Dict]
    _events: Dict[int, Dict]

    def __init__(self):
        self._lock = threading.Lock()

        self._controllers = {}
        self._doors = {}
        self._cards = {}
        self._events = {}

    @property
    def controllers(self):
        return self._controllers

    @controllers.setter
    def controllers(self, controllers):
        with self._lock:
            self._controllers = controllers

    @property
    def doors(self):
        return self._doors

    @doors.setter
    def doors(self, doors):
        with self._lock:
            self._doors = doors

    @property
    def cards(self):
        return self._cards

    @cards.setter
    def cards(self, cards):
        with self._lock:
            self._cards = cards

    @property
    def events(self):
        return self._events

    @events.setter
    def events(self, events):
        with self._lock:
            self._events = events
