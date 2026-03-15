from dataclasses import dataclass
from datetime import time

from .TimeSlot import TimeSlot
@dataclass(frozen=True)
class Event:
    """
    מחלקה האחראית על פרטי האירוע והמשתתף.
    נשענת על TimeSlot עבור ניהול הזמן.
    """
    participant_name: str
    subject: str
    time_slot: TimeSlot

# דוגמה לשימוש:
start = time(10, 0)  # 10:00
end = time(11, 30)   # 11:30

my_slot = TimeSlot(start_time=start, end_time=end)
my_event = Event(participant_name="ישראל ישראלי", subject="סקירת פרויקט", time_slot=my_slot)

print(f"אירוע: {my_event.subject} עם {my_event.participant_name}")
print(f"זמן: {my_event.time_slot.start_time} - {my_event.time_slot.end_time}")