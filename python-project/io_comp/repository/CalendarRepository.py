import csv
import os
from datetime import time
from typing import List
from ..models import Event,TimeSlot

class CalendarRepository:
    def __init__(self, file_path: str = "calendar.csv"):
        self.file_path = file_path

    def load_events(self):
        events = []
        if not os.path.exists(self.file_path):
            print(f"שגיאה: הקובץ {self.file_path} לא נמצא.")
            return []

        # הגדרת שמות העמודות באופן ידני מכיוון שהם חסרים בקובץ
        column_names = ['participant_name', 'subject', 'start_time', 'end_time']

        try:
            with open(self.file_path, mode='r', encoding='utf-8') as file:
                # אנו מעבירים את column_names ל-fieldnames
                reader = csv.DictReader(file, fieldnames=column_names)

                for row_number, row in enumerate(reader, start=1):
                    try:
                        # המרת מחרוזת לטיפוס time
                        start_t = time.fromisoformat(row['start_time'].strip())
                        end_t = time.fromisoformat(row['end_time'].strip())

                        slot = TimeSlot(start_time=start_t, end_time=end_t)
                        event = Event(
                            participant_name=row['participant_name'].strip(),
                            subject=row['subject'].strip(),
                            time_slot=slot
                        )
                        events.append(event)
                    except (ValueError, TypeError) as e:
                        print(f"אזהרה: שגיאת נתונים בשורה {row_number}: {e}. השורה דולגה.")
        except Exception as e:
            print(f"שגיאה כללית בקריאת הקובץ: {e}")

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