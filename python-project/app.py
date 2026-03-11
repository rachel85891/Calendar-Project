"""
This is the App entry point
"""
"""
from io_comp import AvailabilityService, CalendarRepository

def main():
    # 1. יצירת ה-Repository וטעינת הנתונים מהנתיב המבוקש
    repo = CalendarRepository(file_path="resources/calendar.csv")

    # 2. יצירת השרות (Service) המשתמש ב-Repository
    service = AvailabilityService(repository=repo)

    # הגדרת פרמטרים לדוגמה להרצה
    participants = ["Alice", "Jack"]
    meeting_duration = 60  # דקות

    print(f"מחפש חלונות זמן פנויים עבור: {', '.join(participants)}")
    print(f"משך פגישה מבוקש: {meeting_duration} דקות\n")

    # 3. קריאה ללוגיקת מציאת הזמן הפנוי
    available_slots = service.find_available_slots(participants, meeting_duration)

    # 4. הדפסת התוצאות בפורמט הנדרש
    if not available_slots:
        print("לא נמצאו חלונות זמן פנויים העונים על הדרישות.")
    else:
        print("Starting Time of available slots:")
        for slot in available_slots:
            # פורמט HH:MM - HH:MM
            start_str = slot.start_time.strftime("%H:%M")
            end_str = slot.end_time.strftime("%H:%M")
            print(f"{start_str} - {end_str}")


# 5. נקודת כניסה להרצה מהטרמינל
if __name__ == "__main__":
    main()
"""
from flask import Flask, render_template, request, jsonify
from io_comp import CalendarRepository, AvailabilityService

app = Flask(__name__)

# הגדרת ה-Backend
repo = CalendarRepository(file_path="resources/calendar.csv")
service = AvailabilityService(repository=repo)


# נתיב ראשי המציג את דף הנחיתה
@app.route('/')
def home():
    return render_template('index.html')


# נתיב ה-API שמקבל בקשות מהדף ומחזיר זמנים פנויים
@app.route('/api/availability', methods=['POST'])
def get_slots():
    data = request.json
    participants = data.get('participants', [])
    duration = int(data.get('duration', 60))

    available_slots = service.find_available_slots(participants, duration)

    # המרת אובייקטי TimeSlot למילון פשוט עבור ה-JSON
    results = [
        {"start": slot.start_time.strftime("%H:%M"), "end": slot.end_time.strftime("%H:%M")}
        for slot in available_slots
    ]
    return jsonify(results)


# פונקציית ה-Main שביקשת (להרצה מהטרמינל)
def run_cli_demo():
    print("--- Running CLI Demo ---")
    participants = ["Alice", "Jack"]
    duration = 60
    print(f"Starting Time of available slots for {participants}:")
    slots = service.find_available_slots(participants, duration)
    for slot in slots:
        print(f"{slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')}")
    print("------------------------\n")


if __name__ == "__main__":
    # הרצת הדוגמה לטרמינל (סעיף 2 ו-4 בבקשה שלך)
    run_cli_demo()

    # הרצת שרת האינטרנט (סעיף 5)
    print("Starting Web Server at http://127.0.0.1:5000")
    app.run(debug=True)