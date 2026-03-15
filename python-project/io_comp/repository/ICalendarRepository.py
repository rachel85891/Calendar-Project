from abc import ABC, abstractmethod
from ..models import Event
from typing import List

class ICalendarRepository(ABC):
    @abstractmethod
    def load_events(self)-> List[Event]:
        pass

    @abstractmethod
    def _map_row_to_event(self, row: dict) -> Event:
        pass