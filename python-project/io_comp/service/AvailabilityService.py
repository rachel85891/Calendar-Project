from datetime import time, timedelta
from typing import List,Tuple,Dict,Any
from ..models import Event,TimeSlot
import logging
from ..repository.ICalendarRepository import ICalendarRepository

logger = logging.getLogger(__name__)

class AvailabilityService:
    def __init__(self, repository: ICalendarRepository):
        self.repository = repository
        self.WORK_DAY_START = time(7, 0)
        self.WORK_DAY_END = time(19, 0)
        logger.info("AvailabilityService initialized.")

    def find_available_slots(self, person_list:List[str], duration_minutes:int):
        logger.info(f"Starting availability search for {len(person_list)} persons, duration: {duration_minutes} min.")

        all_events = self.repository.load_events()
        relevant_events = [e for e in all_events if e.participant_name in person_list]

        logger.debug(f"Found {len(relevant_events)} relevant events for the requested participants.")

        relevant_slots: List[TimeSlot] = [e.time_slot for e in relevant_events]

        merged_occupied: List[Tuple[int, int]] = self._merge_slots(relevant_slots)
        gaps: List[TimeSlot]= self._identify_gaps(merged_occupied, duration_minutes)

        logger.info(f"Identified {len(gaps)} potential gaps.")

        scored_results: List[Dict[str, Any]] = []
        for gap in gaps:
            score = self._calculate_score(gap, relevant_slots)

            logger.debug(f"Gap found: {gap.start_time}-{gap.end_time} | Calculated Score: {score}")
            # יוצרים מילון במקום לשנות את האובייקט הקפוא
            scored_results.append({
                "slot": gap,
                "score": score
            })

        # מיון לפי הציון מהגבוה לנמוך
        scored_results.sort(key=lambda x: x["score"], reverse=True)

        # לוג מסכם לפני ההחזרה
        if scored_results:
            best_slot = scored_results[0]["slot"]
            logger.info(
                f"Search completed. Found {len(scored_results)} slots. "
                f"Best slot: {best_slot.start_time}-{best_slot.end_time} with score {scored_results[0]['score']}"
            )
        else:
            logger.warning(f"No available slots found for duration {duration_minutes} minutes.")

        return scored_results

    def _calculate_score(self, gap: TimeSlot, occupied_slots: List[TimeSlot]) -> int:
        score = 100  # ציון בסיס

        logger.debug(f"Calculating score for gap: {gap.start_time}-{gap.end_time}")

        # בונוס בוקר: לפני 12:00
        if gap.start_time < time(12, 0):
            score += 30

        # בונוס רצף: האם חלון הזמן מתחיל בדיוק כשמישהו מסיים פגישה?
        for occ in occupied_slots:
            if occ.end_time == gap.start_time:
                score += 50
                logger.debug("Sequence bonus applied (+50).")
                break  # מספיק שצמוד לפגישה אחת

        return score

    def _time_to_minutes(self, t: time) -> int:
        return t.hour * 60 + t.minute

    def _minutes_to_time(self, m: int) -> time:
        return time(hour=m // 60, minute=m % 60)

    def _merge_slots(self, slots: List[TimeSlot]) -> List[Tuple[int, int]]:
        if not slots:
            return []

        # מיון לפי זמן התחלה
        sorted_slots: List[Tuple[int, int]] = sorted(
            [(self._time_to_minutes(s.start_time), self._time_to_minutes(s.end_time)) for s in slots]
        )

        merged: List[Tuple[int, int]] = [sorted_slots[0]]
        for current_start, current_end in sorted_slots[1:]:
            last_start, last_end = merged[-1]

            if current_start <= last_end:  # יש חפיפה או רצף
                merged[-1] = (last_start, max(last_end, current_end))
            else:
                merged.append((current_start, current_end))
        return merged

    def _identify_gaps(self, occupied: List[Tuple[int, int]], duration: int) -> List[TimeSlot]:
        available_slots: List[TimeSlot] = []
        day_start_min: int = self._time_to_minutes(self.WORK_DAY_START)
        day_end_min: int = self._time_to_minutes(self.WORK_DAY_END)

        # נקודת התחלה לבדיקה
        current_marker: int = day_start_min

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

