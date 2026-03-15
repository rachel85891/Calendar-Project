from abc import ABC, abstractmethod
from ..models import Event
from typing import List

class ICalendarRepository(ABC):
    """
    ממשק מופשט (Interface) לניהול גישה לנתוני לוח שנה.
    
    מגדיר את החוזה עבור מחלקות שיממשו טעינת נתונים ממקורות שונים.
    """
    @abstractmethod
    def load_events(self)-> List[Event]:
        pass

    @abstractmethod
    def _map_row_to_event(self, row: dict) -> Event:
        pass