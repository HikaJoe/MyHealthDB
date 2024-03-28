from flask import Flask, request, jsonify
import mysql.connector
from werkzeug.security import check_password_hash

app = Flask(__name__)

# Database configuration - replace with your actual details
db_config = {
    'host': '13.49.107.159',
    'user': 'root',
    'password': 'Admin',
    'database': 'PatientInfoMed'
}

@app.route('/login', methods=['POST'])
def login():
    # Retrieve login data from request
    data = request.json
    user_identifier = data.get('user_identifier')  # Can be email or phone number
    password = data.get('password')

    # Connect to the database
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Query to find user by email or phone number
        query = "SELECT * FROM Patients WHERE email = %s OR phonenumber = %s"
        cursor.execute(query, (user_identifier, user_identifier))
        user = cursor.fetchone()

        # Verify user exists and check password
        if user and check_password_hash(user['password_hash'], password):
            # Login success
            return jsonify({"success": True, "message": "Login successful"}), 200
        else:
            # Login failed
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({"success": False, "message": "Database error"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5001)

