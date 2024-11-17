from flask import Flask, render_template, request
import csv
from datetime import datetime
import mysql.connector

app = Flask(__name__)

# Database configuration
db_config = {
    'user': 'root',            # Your MySQL username
    'password': 'Nhla@1234',   # Your MySQL password
    'host': '127.0.0.1',       # Typically localhost
    'database': 'studentlist', # Your database name
    'auth_plugin': 'mysql_native_password'  # Specify the plugin here
}

# Path to CSV where attendance will be recorded
attendance_file = 'cmpg121_attendance.csv'

# Validate student number by checking if it exists in the database
def is_student_valid(student_number):
    conn = None
    try:
        # Establish database connection
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM students WHERE student_number = %s"
        cursor.execute(query, (student_number,))
        result = cursor.fetchone()
        return result[0] > 0  # Return True if the student exists
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()

# Check if the student number already exists in the CSV file
def is_attendance_recorded(student_number):
    try:
        with open(attendance_file, mode='r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == student_number:  # Check if student number already exists
                    return True
    except FileNotFoundError:
        return False  # If the file doesn't exist, attendance hasn't been recorded yet
    return False

# Route to display the attendance form
@app.route('/')
def index():
    return render_template('attandance.html')  # Show attendance form

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit_attendance():
    student_number = request.form.get('student_number')

    # Validate student number
    if student_number and is_student_valid(student_number):
        # Check if the attendance has already been recorded
        if is_attendance_recorded(student_number):
            return "You have already submitted your attendance.", 400

        # Record attendance
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Write to CSV (student number and timestamp)
        try:
            with open(attendance_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([student_number, timestamp])
            return "Thank you! Your attendance has been recorded.", 200
        except IOError as e:
            print(f"Error writing to CSV: {e}")
            return "Error recording attendance. Please try again later.", 500
    else:
        return "Invalid student number. Please try again.", 400

# Vercel automatically calls the Flask app
if __name__ == '__main__':
    # Initialize CSV file if it doesn't exist
    try:
        with open(attendance_file, mode='r'):
            pass
    except FileNotFoundError:
        with open(attendance_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Student Number', 'Time Submitted'])  # Column headers

    # Vercel manages the Flask app startup
