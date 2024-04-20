

import requests

# URL for the login endpoint
login_url = 'http://localhost:5001/login'
login_data = {'patient_id': 6}
login_response = requests.post(login_url, json=login_data)

# Check if login was successful
if login_response.ok:
    url = 'http://localhost:5001/add_medication_with_reminders'
    data = {
        "MedicationName": "Aspirin",
        "Dosage": "100mg",
        "Frequency": "Daily",
        "StartDate": "2022-02-01",
        "EndDate": "2022-02-28",
        "ReminderTimes": ["10:00 AM", "2:00 PM"]
    }

    # Use cookies to maintain the session
    response = requests.post(url, json=data, cookies=login_response.cookies)
    print(response.text)
else:
    print("Login failed")
