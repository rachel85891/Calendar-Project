"""
Unit tests for Comp calendar scheduler
"""
import pytest

import pytest
from unittest.mock import MagicMock
from datetime import time
from io_comp import AvailabilityService, Event, TimeSlot
#from ..io_comp import AvailabilityService, Event, TimeSlot

@pytest.fixture
def mock_service():
    """פיקסטורה ליצירת ה-Service עם Repository מזויף (Mock)"""
    mock_repo = MagicMock()
    service = AvailabilityService(repository=mock_repo)
    return service, mock_repo


# --- טסט 1: המקרה מה-README (Alice & Jack) ---
def test_find_available_slots_readme_case(mock_service):
    service, mock_repo = mock_service

    # הגדרת נתונים המדמים את ה-CSV עבור Alice ו-Jack
    mock_repo.load_events.return_value = [
        # Alice
        Event("Alice", "M1", TimeSlot(time(8, 0), time(9, 30))),
        Event("Alice", "M2", TimeSlot(time(13, 0), time(14, 0))),
        Event("Alice", "M3", TimeSlot(time(16, 0), time(17, 0))),
        # Jack
        Event("Jack", "M1", TimeSlot(time(8, 0), time(8, 50))),
        Event("Jack", "M2", TimeSlot(time(9, 0), time(9, 40))),
        Event("Jack", "M3", TimeSlot(time(13, 0), time(14, 0))),
        Event("Jack", "M4", TimeSlot(time(16, 0), time(17, 0)))
    ]

    results = service.find_available_slots(["Alice", "Jack"], 60)

    # שליפת שעות ההתחלה בלבד לצורך השוואה קלה
    start_times = [slot.start_time for slot in results]
    expected_starts = [time(7, 0), time(9, 40), time(14, 0), time(17, 0)]

    assert start_times == expected_starts


# --- טסט 2: אין חלון זמן פנוי (מישהו תפוס כל היום) ---
def test_no_available_slots_full_day(mock_service):
    service, mock_repo = mock_service

    mock_repo.load_events.return_value = [
        Event("Alice", "Busy", TimeSlot(time(7, 0), time(19, 0)))
    ]

    results = service.find_available_slots(["Alice"], 30)
    assert results == []


# --- טסט 3: פגישה ארוכה מדי (13 שעות) ---
def test_meeting_longer_than_workday(mock_service):
    service, mock_repo = mock_service

    # גם אם כולם פנויים
    mock_repo.load_events.return_value = []

    duration_13_hours = 13 * 60
    results = service.find_available_slots(["Alice"], duration_13_hours)

    assert results == []


# --- טסט 4: משתתף ללא אירועים (פנוי לגמרי) ---
def test_participant_with_no_events(mock_service):
    service, mock_repo = mock_service

    # ב-Repository יש רק אירועים של Bob, לא של Alice
    mock_repo.load_events.return_value = [
        Event("Bob", "Meeting", TimeSlot(time(10, 0), time(11, 0)))
    ]

    # נחפש זמן עבור Alice (שלא קיימת ב-CSV) ו-Bob
    results = service.find_available_slots(["Alice", "Bob"], 60)

    # Alice פנויה תמיד, אז האילוץ היחיד הוא Bob
    # צריכים להיות רווחים לפני (7-10) ואחרי (11-19)
    assert any(slot.start_time == time(7, 0) and slot.end_time == time(10, 0) for slot in results)
    assert any(slot.start_time == time(11, 0) and slot.end_time == time(19, 0) for slot in results)

# --- טסט 5: לוח ריק לחלוטין (כולם פנויים כל היום) ---
def test_all_participants_empty_calendars(mock_service):
    service, mock_repo = mock_service

    # אין אירועים בכלל ב-Repository
    mock_repo.load_events.return_value = []

    # מחפשים פגישה של שעה עבור Alice ו-Bob
    results = service.find_available_slots(["Alice", "Bob"], 60)

    # התוצאה צריכה להיות חלון אחד יחיד שמתחיל בתחילת היום ומסתיים בסופו
    assert len(results) == 1
    assert results[0].start_time == time(7, 0)
    assert results[0].end_time == time(19, 0)
