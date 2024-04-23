from flask import Flask, request, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash
from config import db_config

app = Flask(__name__)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    dateOfBirth = data.get('dateOfBirth')
    email = data.get('email')
    phoneNumber = data.get('phoneNumber')
    medicalConditions = data.get('medicalConditions')
    password = data.get('password')

    # Hash the password for security
    password_hash = generate_password_hash(password)

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Adjust the INSERT INTO statement based on your database schema
        query = """
        INSERT INTO Patients (name, dateOfBirth, email, phoneNumber, medicalConditions, password_hash) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, dateOfBirth, email, phoneNumber, medicalConditions, password_hash))

        conn.commit()
        return jsonify({"success": True, "message": "User registered successfully."}), 201
    except mysql.connector.Error as err:
        print("Failed to insert data into MySQL table {}".format(err))
        return jsonify({"success": False, "message": "Failed to register user."}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            if conn.is_connected():
                conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)



