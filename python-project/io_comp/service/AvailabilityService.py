from datetime import time, timedelta
from typing import List
from ..models import Event,TimeSlot
from ..repository.CalendarRepository import CalendarRepository


class AvailabilityService:
    def __init__(self, repository: CalendarRepository):
        self.repository = repository
        self.WORK_DAY_START = time(7, 0)
        self.WORK_DAY_END = time(19, 0)

    def find_available_slots(self, person_list: List[str], duration_minutes: int) -> List[TimeSlot]:
        # 1. איסוף כל האירועים הרלוונטיים
        all_events = self.repository.load_events()
        relevant_slots = [
            e.time_slot for e in all_events
            if e.participant_name in person_list
        ]

        # 2. מיזוג חפיפות
        merged_occupied = self._merge_slots(relevant_slots)

        # 3. מציאת רווחים (Gaps)
        return self._identify_gaps(merged_occupied, duration_minutes)

    def _time_to_minutes(self, t: time) -> int:
        return t.hour * 60 + t.minute

    def _minutes_to_time(self, m: int) -> time:
        return time(hour=m // 60, minute=m % 60)

    def _merge_slots(self, slots: List[TimeSlot]) -> List[tuple]:
        if not slots:
            return []

        # מיון לפי זמן התחלה
        sorted_slots = sorted(
            [(self._time_to_minutes(s.start_time), self._time_to_minutes(s.end_time)) for s in slots]
        )

        merged = [sorted_slots[0]]
        for current_start, current_end in sorted_slots[1:]:
            last_start, last_end = merged[-1]

            if current_start <= last_end:  # יש חפיפה או רצף
                merged[-1] = (last_start, max(last_end, current_end))
            else:
                merged.append((current_start, current_end))
        return merged

    def _identify_gaps(self, occupied: List[tuple], duration: int) -> List[TimeSlot]:
        available_slots = []
        day_start_min = self._time_to_minutes(self.WORK_DAY_START)
        day_end_min = self._time_to_minutes(self.WORK_DAY_END)

        # נקודת התחלה לבדיקה
        current_marker = day_start_min

        for start, end in occupied:
            # האם יש מספיק זמן מהסמן הנוכחי ועד תחילת הבלוק התפוס?
            if start - current_marker >= duration:
                available_slots.append(TimeSlot(
                    self._minutes_to_time(max(current_marker, day_start_min)),
                    self._minutes_to_time(start)
                ))
            current_marker = max(current_marker, end)

        # בדיקת הרווח האחרון עד סוף היום
        if day_end_min - current_marker >= duration:
            available_slots.append(TimeSlot(
                self._minutes_to_time(current_marker),
                self._minutes_to_time(day_end_min)
            ))

        return available_slots