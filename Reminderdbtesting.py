

import mysql.connector
from flask import Flask, request, jsonify, session
from datetime import datetime
import json




app = Flask(__name__)
app.secret_key = 'secret_key'

# Database configuration
db_config = {
    'host': '13.49.107.159',
    'user': 'root',
    'password': 'Admin',
    'database': 'myhealthdb',
}


@app.route('/login', methods=['POST'])
def login():
    # Here you would typically validate the user's credentials
    user_credentials = request.json
    # Assuming validation passes, set the session:
    session['patient_id'] = user_credentials.get('patient_id', None)
    return jsonify({"success": True, "message": "Logged in successfully"}), 200



@app.route('/add_medication_with_reminders', methods=['POST'])
def add_medication_with_reminders():


    if 'patient_id' not in session:
        return jsonify({"success": False, "message": "User is not logged in"}), 403

    data = request.json
    print("Received data for adding medication:", json.dumps(data, indent=2))

    try:
        patient_id = session['patient_id']
        medication_name = data['MedicationName']
        dosage = data['Dosage']
        frequency = data['Frequency']
        start_date = datetime.fromisoformat(data['StartDate']).date()
        end_date = datetime.fromisoformat(data['EndDate']).date()
        reminder_times = [datetime.strptime(rt, '%I:%M %p').strftime('%H:%M') for rt in data.get('ReminderTimes', []) if 'AM' in rt or 'PM' in rt]
        
        with mysql.connector.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Medications (PatientID, MedicationName, Dosage, Frequency, StartDate, EndDate)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (patient_id, medication_name, dosage, frequency, start_date, end_date))
                
                medication_id = cursor.lastrowid
                for reminder_time in reminder_times:
                    print(f"Inserting reminder for time: {reminder_time}")
                    cursor.execute("""
                        INSERT INTO Reminders (PatientID, MedicationID, ReminderTime, ReminderFrequency, ActiveStatus)
                        VALUES (%s, %s, %s, %s, TRUE)
                    """, (patient_id, medication_id, reminder_time, frequency))
                    print(f"Inserted reminder for time: {reminder_time}")
                
                conn.commit()
                return jsonify({"success": True, "message": "Medication and reminders added successfully"}), 200

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        if conn.is_connected():
            conn.rollback()
        return jsonify({"success": False, "message": f"Database error: {err}"}), 500

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"success": False, "message": f"Unexpected error: {e}"}), 500
    


if __name__ == '__main__':
    app.run(debug=True, port=5001)
