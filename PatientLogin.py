from flask import Flask, request, jsonify
import mysql.connector
from werkzeug.security import check_password_hash
from datetime import datetime
import json

app = Flask(__name__)

# Database configuration
db_config = {
    'host': '13.49.107.159',
    'user': 'root',
    'password': 'Admin',
    'database': 'PatientInfoMed',
}

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user_identifier = data.get('user_identifier')
    password = data.get('password')

    print("Attempting to log in user:", user_identifier)  # Log the attempt

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM Patients WHERE Name = %s OR PhoneNumber = %s"
        cursor.execute(query, (user_identifier, user_identifier))
        user = cursor.fetchone()

        if user:
            print("User found in database:", user['Name'])  # Log user details (careful with sensitive data)
            if check_password_hash(user['password_hash'], password):
                print("Password verification successful.")
                return jsonify({"success": True, "message": "Login successful"}), 200
            else:
                print("Password verification failed.")
                return jsonify({"success": False, "message": "Invalid credentials"}), 401
        else:
            print("User not found.")
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({"success": False, "message": "Database error"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/add_medication_with_reminders', methods=['POST'])
def add_medication_with_reminders():
    data = request.json
    print("Received data for adding medication:", json.dumps(data, indent=2))

    patient_id = data.get('PatientID')
    medication_name = data.get('MedicationName')
    dosage = data.get('Dosage')
    frequency = data.get('Frequency')
    start_date = data.get('StartDate')
    end_date = data.get('EndDate')
    
    # Expecting a list of times, convert them into 24-hour format
    reminder_times = [datetime.strptime(rt, '%I:%M %p').strftime('%H:%M') if 'AM' in rt or 'PM' in rt else rt for rt in data.get('ReminderTimes', [])]

    if not all([patient_id, medication_name, dosage, frequency, start_date, end_date, reminder_times]):
        return jsonify({"success": False, "message": "Missing required medication or reminder data"}), 400

    try:
        start_date = datetime.fromisoformat(start_date).date()
        end_date = datetime.fromisoformat(end_date).date()
    except ValueError as e:
        return jsonify({"success": False, "message": f"Date formatting error: {e}"}), 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        medication_query = """
        INSERT INTO Medications (PatientID, MedicationName, Dosage, Frequency, StartDate, EndDate)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(medication_query, (patient_id, medication_name, dosage, frequency, start_date, end_date))
        medication_id = cursor.lastrowid

        reminder_query = """
        INSERT INTO Reminders (PatientID, MedicationID, ReminderTime, ReminderFrequency, ActiveStatus)
        VALUES (%s, %s, %s, %s, TRUE)
        """
        for reminder_time in reminder_times:
            cursor.execute(reminder_query, (patient_id, medication_id, reminder_time, frequency))
        
        conn.commit()
        return jsonify({"success": True, "message": "Medication and reminders added successfully"}), 200
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        conn.rollback()  # Rollback in case of any error
        return jsonify({"success": False, "message": f"Database error: {err}"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/api/vitalsigns', methods=['POST'])
def add_vital_signs():
    if request.is_json:
        data = request.get_json()
        print("Received the following vital sign data:")
        print(json.dumps(data, indent=4))

        try:
            timestamp = datetime.fromisoformat(data['timestamp'])
            patient_id = data['patientID']
            type_of_vital_sign = data['typeOfVitalSign']
            measurement_value = data['measurementValue']
            notes = data.get('notes', '')  # Default to empty string if notes are not provided

            # Establish a database connection
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # SQL to insert data
            insert_sql = """
            INSERT INTO VitalSigns (PatientID, Timestamp, TypeOfVitalSign, MeasurementValue, Notes)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (patient_id, timestamp, type_of_vital_sign, measurement_value, notes))
            conn.commit()  # Commit the transaction

            return jsonify({"message": "Vital sign recorded successfully", "status": "success"}), 200
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return jsonify({"error": str(err), "status": "error"}), 500
        except KeyError as ke:
            print(f"Missing data: {ke}")
            return jsonify({"error": f"Missing data: {ke}", "status": "error"}), 400
        except ValueError as ve:
            print(f"Data format error: {ve}")
            return jsonify({"error": f"Data format error: {ve}", "status": "error"}), 400
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    else:
        return jsonify({"error": "Request must be JSON", "status": "error"}), 400
    

@app.route('/api/vital_signs', methods=['GET'])
def get_vital_signs():
    patient_id = request.args.get('patientID', '1')  # Default patientID set to '1'
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
            print("Database connection closed.")  # Debug: Confirm closure

@app.route('/api/medications', methods=['GET'])
def get_medications():
    patient_id = request.args.get('patientID', '1')
    print(f"Using patientID: {patient_id}")

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        print("Database connection established.")

        query = "SELECT * FROM Medications WHERE PatientID = %s;"
        print(f"Executing query: {query} with patientID: {patient_id}")
        cursor.execute(query, (patient_id,))
        results = cursor.fetchall()
        print(f"Query executed. Number of results: {len(results)}")

        results = [dict(row) for row in results]
        for result in results:
            if 'StartDate' in result and isinstance(result['StartDate'], datetime):
                result['StartDate'] = result['StartDate'].isoformat()
            if 'EndDate' in result and isinstance(result['EndDate'], datetime):
                result['EndDate'] = result['EndDate'].isoformat()

        query = "SELECT * FROM Reminders WHERE PatientID = %s;"
        print(f"Executing query: {query} with patientID: {patient_id}")
        cursor.execute(query, (patient_id,))
        reminders = cursor.fetchall()
        print(f"Query executed. Number of results: {len(reminders)}")

        print(f"Results: {results}")
        return jsonify({"data": results, "status": "success"}), 200
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({"error": str(err), "status": "error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("Database connection closed.")
            

if __name__ == '__main__':
    app.run(debug=True, port=5001)