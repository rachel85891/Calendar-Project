
from dataclasses import dataclass
from datetime import time

@dataclass(frozen=True)
class TimeSlot:
    """
    מחלקה האחראית אך ורק על ייצוג טווח זמן.
    השימוש ב-frozen=True הופך את האובייקט לבלתי ניתן לשינוי (Immutable).
    """
    start_time: time
    end_time: time

    def __post_init__(self):
        # בדיקה לוגית בסיסית שזמן הסיום הוא אחרי זמן ההתחלה
        if self.end_time <= self.start_time:
            raise ValueError("זמן הסיום חייב להיות אחרי זמן ההתחלה.")