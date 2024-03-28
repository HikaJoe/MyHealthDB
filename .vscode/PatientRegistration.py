import mysql.connector

# Connect to the MySQL database
connection = mysql.connector.connect(
    host='13.49.107.159',
    user='root',
    password='Admin',
    database='PatientInfoMed'
)

# Create a cursor object
cursor = connection.cursor()

# Example query
cursor.execute('SELECT * FROM Patients;')

# Fetch and print all rows of the query result
for row in cursor.fetchall():
    print(row)

# Close the connection
connection.close()

