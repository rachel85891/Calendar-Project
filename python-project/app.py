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

@app.route('/api/availability', methods=['POST'])
def get_slots():
    data = request.json
    participants = data.get('participants', [])
    duration = int(data.get('duration', 60))

    # עכשיו מקבלים רשימת מילונים עם 'slot' ו-'score'
    scored_slots = service.find_available_slots(participants, duration)

    results = [
        {
            "start": item["slot"].start_time.strftime("%H:%M"),
            "end": item["slot"].end_time.strftime("%H:%M"),
            "score": item["score"]
        }
        for item in scored_slots
    ]
    return jsonify(results)

def run_cli_demo():
    print("--- Running CLI Demo ---")
    participants = ["Alice", "Jack"]
    duration = 60
    scored_slots = service.find_available_slots(participants, duration)

    print(f"Recommended slots for {participants}:")
    for item in scored_slots:
        s = item["slot"]
        print(f"{s.start_time.strftime('%H:%M')} - {s.end_time.strftime('%H:%M')} (Score: {item['score']})")


if __name__ == "__main__":
    # הרצת הדוגמה לטרמינל (סעיף 2 ו-4 בבקשה שלך)
    run_cli_demo()

    # הרצת שרת האינטרנט (סעיף 5)
    print("Starting Web Server at http://127.0.0.1:5000")
    app.run(debug=True)