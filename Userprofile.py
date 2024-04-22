from flask import Flask, request, jsonify, session, g
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST', '13.49.107.159'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'Admin'),
    'database': os.getenv('DB_NAME', 'myhealthdb'),
}

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(**db_config)
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None and db.is_connected():
        db.close()


@app.route('/login', methods=['POST'])
def login():
    user_credentials = request.json
    session['patient_id'] = user_credentials.get('patient_id')
    return jsonify({"success": True, "message": "Logged in successfully"}), 200

@app.route('/api/user_profile', methods=['GET'])
def get_user_profile():
    if 'patient_id' not in session:
        return jsonify({"error": "User is not logged in or session has expired"}), 401
    patient_id = session['patient_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
                SELECT Name AS name, DateOfBirth AS dateOfBirth, Email AS email 
                FROM Patients 
                WHERE PatientID = %s
                """, (patient_id,))
    user = cursor.fetchone()
    if user and user['dateOfBirth']:
        user['dateOfBirth'] = user['dateOfBirth'].strftime('%Y-%m-%d')
    return jsonify(user), 200 if user else jsonify({"error": "No user found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5005)
