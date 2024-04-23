
import os
from flask import Flask, request, jsonify
import mysql.connector
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
import json
from flask import session
from flask import jsonify, make_response
from config import db_config


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(days=1)



@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user_identifier = data.get('user_identifier')
    password = data.get('password')

    print("Attempting to log in user:", user_identifier)

    try:
        with mysql.connector.connect(**db_config) as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = "SELECT * FROM Patients WHERE Name = %s OR PhoneNumber = %s"
                cursor.execute(query, (user_identifier, user_identifier))
                user = cursor.fetchone()

                if user:
                    if check_password_hash(user['password_hash'], password):
                        session['patient_id'] = user['PatientID']
                        session.permanent = True  # Makes the session permanent until it is explicitly cleared
                        print("Login successful for:", user['Name'])
                        return jsonify({"success": True, "message": "Login successful"}), 200
                    else:
                        return jsonify({"success": False, "message": "Invalid credentials"}), 401
                else:
                    return jsonify({"success": False, "message": "User not found"}), 401
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({"success": False, "message": "Database error"}), 500






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
        notes = data['ImportantInformation']

        # Handling reminder times flexibly, assuming 24-hour format directly from input
        reminder_times = [datetime.strptime(rt, '%H:%M').strftime('%H:%M') for rt in data.get('ReminderTimes', [])]

        with mysql.connector.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Medications (PatientID, MedicationName, Dosage, Frequency, StartDate, EndDate,Notes)
                    VALUES (%s, %s, %s, %s, %s, %s,%s)
                """, (patient_id, medication_name, dosage, frequency, start_date, end_date,notes))
                
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





@app.route('/api/vitalsigns', methods=['POST'])
def add_vital_signs():
    if 'patient_id' not in session:
        return jsonify({"error": "User not logged in or session expired", "status": "error"}), 403

    if request.is_json:
        data = request.get_json()
        print("Received the following vital sign data:")
        print(json.dumps(data, indent=4))

        conn = None

        try:
            timestamp = datetime.fromisoformat(data['timestamp'])
            patient_id = session['patient_id']
            type_of_vital_sign = data['typeOfVitalSign']
            measurement_value = data['measurementValue']
            notes = data.get('notes', '')

            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            insert_sql = """
            INSERT INTO VitalSigns (PatientID, Timestamp, TypeOfVitalSign, MeasurementValue, Notes)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (patient_id, timestamp, type_of_vital_sign, measurement_value, notes))
            conn.commit()

            return jsonify({"message": "Vital sign recorded successfully", "status": "success"}), 200
        except mysql.connector.Error as err:
            if conn and conn.is_connected():
                conn.rollback()
            print(f"Database error: {err}")
            return jsonify({"error": str(err), "status": "error"}), 500
        except KeyError as ke:
            print(f"Missing data: {ke}")
            return jsonify({"error": f"Missing data: {ke}", "status": "error"}), 400
        except ValueError as ve:
            print(f"Data format error: {ve}")
            return jsonify({"error": f"Data format error: {ve}", "status": "error"}), 400
        finally:
            if conn:
                cursor.close()
                conn.close()
                print("Database connection closed.")
    else:
        return jsonify({"error": "Request must be JSON", "status": "error"}), 400






@app.route('/api/vital_signs', methods=['GET'])
def get_vital_signs():
    # Check if the patient is logged in and get the patient_id from session
    if 'patient_id' not in session:
        return jsonify({"error": "User is not logged in or session has expired", "status": "error"}), 401
    
    patient_id = session['patient_id']
    print(f"Using patientID: {patient_id}")  # Debug: Check what patientID is being used

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        print("Database connection established.")  # Debug: Confirm connection

        query = "SELECT * FROM VitalSigns WHERE PatientID = %s;"
        print(f"Executing query: {query} with patientID: {patient_id}")  # Debug: Show query
        cursor.execute(query, (patient_id,))  # Ensure the parameter is a tuple
        results = cursor.fetchall()
        print(f"Query executed. Number of results: {len(results)}")  # Debug: Output results count

        results = [dict(row) for row in results]
        for result in results:
            if 'Timestamp' in result and isinstance(result['Timestamp'], datetime):
                result['Timestamp'] = result['Timestamp'].isoformat()

        print(f"Results: {results}")  # Debug: Output results
        return jsonify({"data": results, "status": "success"}), 200
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({"error": str(err), "status": "error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("Database connection closed.") 





# Convert timedelta objects to ISO 8601 format
def serialize_timedelta(obj):
    if isinstance(obj, timedelta):
        return obj.total_seconds()
    raise TypeError("Object of type timedelta is not JSON serializable")

@app.route('/api/medications', methods=['GET'])
def get_medications():
    if 'patient_id' not in session:
        return jsonify({"error": "User is not logged in or session has expired", "status": "error"}), 401

    patient_id = session['patient_id']
    try:
        conn = mysql.connector.connect(**db_config)
        with conn.cursor(dictionary=True) as cursor:
            print("Database connection established.")
            query = """
            SELECT m.*, r.ReminderID, TIME_FORMAT(r.ReminderTime, '%H:%i') AS ReminderTime, r.ReminderFrequency, r.ActiveStatus,m.Notes
            FROM Medications m 
            LEFT JOIN Reminders r ON m.MedicationID = r.MedicationID 
            WHERE m.PatientID = %s;
            """
            cursor.execute(query, (patient_id,))
            medications = {}
            for row in cursor:
                medication_id = row['MedicationID']
                if medication_id not in medications:
                    medications[medication_id] = {
                        'MedicationID': medication_id,
                        'MedicationName': row['MedicationName'],
                        'Dosage': row['Dosage'],
                        'Frequency': row['Frequency'],
                        'StartDate': row['StartDate'].isoformat(),
                        'EndDate': row['EndDate'].isoformat() if row['EndDate'] else None,
                        'Notes': row['Notes'],
                        'PatientID': row['PatientID'],
                        'Reminders': []
                    }
                if row.get('ReminderID'):
                    medications[medication_id]['Reminders'].append({
                        'ReminderID': row['ReminderID'],
                        'ReminderTime': row['ReminderTime'],  # Return as formatted string
                        'ReminderFrequency': row['ReminderFrequency'],
                        'ActiveStatus': bool(row['ActiveStatus']),
                        'PatientID': row['PatientID'],
                        'MedicationID': medication_id
                    })

            print(f"Medications: {medications}")
            return jsonify({"medications": list(medications.values()), "status": "success"}), 200
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({"error": str(err), "status": "error"}), 500
    finally:
        if conn.is_connected():
            conn.close()
            print("Database connection closed.")




@app.route('/api/user_profile', methods=['GET'])
def get_user_profile():
    if 'patient_id' not in session:
        return jsonify({"error": "User is not logged in or session has expired"}), 401

    patient_id = session['patient_id']
    try:
        with mysql.connector.connect(**db_config) as conn:
            with conn.cursor(dictionary=True) as cursor:
                # Fetch user data based on patient_id stored in session
                cursor.execute("""
                SELECT Name AS name, DateOfBirth AS dateOfBirth, Email AS email 
                FROM Patients 
                WHERE PatientID = %s
                """, (patient_id,))
                user = cursor.fetchone()

                if user and user['dateOfBirth']:
                    # Format date of birth to string if necessary
                    user['dateOfBirth'] = user['dateOfBirth'].isoformat()

                    print(f"User data: {user}")
                
            return jsonify(user) if user else make_response(jsonify({"error": "No user found"}), 404)
    except mysql.connector.Error as err:
        return make_response(jsonify({"error": "Database error: " + str(err)}), 500)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)

