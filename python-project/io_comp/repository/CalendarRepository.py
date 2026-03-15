import csv
import os
from datetime import time
from typing import List
from ..models import Event,TimeSlot
from .ICalendarRepository import ICalendarRepository
import logging

logger = logging.getLogger(__name__)

class CalendarRepository(ICalendarRepository):
    """
    מימוש של ICalendarRepository הקורא נתונים מקובץ CSV.
    
    המחלקה מטפלת בפתיחת הקובץ, מיפוי העמודות והמרת הנתונים לאובייקטים מסוג Event.
    """
    def __init__(self, file_path: str = "calendar.csv")-> None:
        self.file_path = file_path

    def load_events(self)-> List[Event]:
        """
        קורא את קובץ ה-CSV וממיר כל שורה תקינה לאובייקט Event.
        
        במקרה של שגיאות בנתונים או קובץ חסר, המערכת מבצעת רישום ללוג וממשיכה הלאה.
        """
        events: List[Event] = []
        if not os.path.exists(self.file_path):
            logger.error(f"שגיאה: הקובץ {self.file_path} לא נמצא.")
            return []

        # הגדרת שמות העמודות באופן ידני מכיוון שהם חסרים בקובץ
        column_names: List[str] = ['participant_name', 'subject', 'start_time', 'end_time']

        try:
            with open(self.file_path, mode='r', encoding='utf-8') as file:
                # אנו מעבירים את column_names ל-fieldnames
                reader = csv.DictReader(file, fieldnames=column_names)

                for row_number, row in enumerate(reader, start=1):
                    try:
                        event : Event = self._map_row_to_event(row)
                        events.append(event)
                    except (ValueError, TypeError) as e:
                        logger.warning(f"אזהרה: שגיאת נתונים בשורה {row_number}: {e}. השורה דולגה.")
        except Exception as e:
            logger.exception(f"שגיאה כללית בקריאת הקובץ: {e}")

        return events

    def _map_row_to_event(self, row: dict) -> Event:
        """
        פונקציית עזר להמרת שורה מה-CSV לאובייקט Event.
        """
        # המרת מחרוזת לטיפוס time (מצפה לפורמט HH:MM)
        start_t = time.fromisoformat(row['start_time'])
        end_t = time.fromisoformat(row['end_time'])

        slot = TimeSlot(start_time=start_t, end_time=end_t)

        return Event(
            participant_name=row['participant_name'],
            subject=row['subject'],
            time_slot=slot
        )