from dataclasses import dataclass
from typing import Dict


@dataclass
class DB:
    controllers: Dict[int, Dict]
    doors: Dict[int, Dict]
    cards: Dict[str, Dict]
    events: Dict[int, Dict]
