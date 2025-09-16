
# --- Imports and App Initialization ---
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import mysql.connector
import os
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)
# Secret key for session management
app.secret_key = 'your_secret_key_here'  # Change this to a secure random value

# MySQL configuration
db_config = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': 'swetA098Poi',  # Replace with your MySQL password
    'database': 'lostfound_db'
}

def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

@app.route('/')
def home():
    user_name = session.get('user_name')
    success_message = session.pop('success_message', None)
    return render_template('index.html', user_name=user_name, success_message=success_message)

@app.route('/login', methods=['POST'])
def login():
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500
    try:
        data = request.form
        email = data['email']
        password = data['password']

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['success_message'] = 'Login successful!'
            return redirect(url_for('home'))
        else:
            return render_template('user.html', error='Invalid email or password')
    except Exception as e:
        return render_template('user.html', error=str(e))

@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    conn = get_db_connection()
    if not conn:
        # For a full HTML app, you might render an error template here
        return "Database connection failed", 500

    try:
        data = request.form
        user_id = data.get('user_id')
        name = data['name']
        email = data['email']
        password = data['password']

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        cursor = conn.cursor()
        if user_id:
            sql = "INSERT INTO users (user_id, name, email, password) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (user_id, name, email, hashed_password))
        else:
            sql = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, email, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()

        session['user_name'] = name
        session['user_email'] = email
        session['success_message'] = 'User added successfully!'
        return redirect(url_for('home'))

    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        return redirect(url_for('error_page', message=str(err)))
    except Exception as e:
        return redirect(url_for('error_page', message=str(e)))

#success page loading
@app.route('/success_page')
def success_page():
    # Renders an HTML template for a successful operation
    return render_template('success.html')

@app.route('/error_page')
def error_page():
    # Renders a simple HTML template for displaying an error
    message = request.args.get('message', 'An unknown error occurred.')
    return render_template('error.html', error_message=message)

# route to fetch users
@app.route('/users')
def get_users():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('users.html', users=users)
    else:
        return render_template('error.html', error_message='Database connection failed'), 500

# --- Report Lost Route ---
@app.route('/report_lost', methods=['POST'])
def report_lost():
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500

    try:
        data = request.form
        user_id = data['user_id']
        item_name = data['item_name']
        description = data['description']
        location_reported = data['location_reported']
        status = data.get('status', 'Pending')

        cursor = conn.cursor()
        sql = """
            INSERT INTO LostReports (user_id, item_name, description, location_reported, status)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (user_id, item_name, description, location_reported, status))
        conn.commit()

        # Get the auto-generated report_id and time_reported
        report_id = cursor.lastrowid
        cursor.execute("SELECT time_reported FROM LostReports WHERE report_id = %s", (report_id,))
        time_reported = cursor.fetchone()[0]
        cursor.close()

        # Redirect to the success page, passing report_id and time_reported
        return redirect(url_for('success_page', report_id=report_id, time_reported=time_reported))

    except mysql.connector.Error as err:
        conn.rollback()
        return redirect(url_for('error_page', message=str(err)))

    except Exception as e:
        return redirect(url_for('error_page', message=str(e)))

    finally:
        if conn:
            conn.close()

    # --- Get Reports Route (HTML) ---
@app.route('/reports')
def get_reports():
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM LostReports")
        reports = cursor.fetchall()
        
        # Render an HTML template and pass the data to it
        return render_template('reports.html', reports=reports)
    
    except mysql.connector.Error as err:
        return redirect(url_for('error_page', message=str(err)))
    
    finally:
        if conn:
            conn.close()

# --- Add Detected Item Route ---
@app.route('/add_detected', methods=['POST'])
def add_detected():
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500
    try:
        data = request.form # Correctly get data from an HTML form
        item_type = data['item_type']
        location_detected = data['location_detected']
        status = data.get('status', 'Unclaimed')

        cursor = conn.cursor()
        sql = "INSERT INTO DetectedItems (item_type, location_detected, status) VALUES (%s, %s, %s)"
        cursor.execute(sql, (item_type, location_detected, status))
        conn.commit()

        # Get the auto-generated detected_id and time_detected
        detected_id = cursor.lastrowid
        cursor.execute("SELECT time_detected FROM DetectedItems WHERE detected_id = %s", (detected_id,))
        time_detected = cursor.fetchone()[0]
        cursor.close()

        # Redirect to the success page, passing detected_id and time_detected
        return redirect(url_for('success_page', detected_id=detected_id, time_detected=time_detected))

    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        return redirect(url_for('error_page', message=str(err)))
    except Exception as e:
        return redirect(url_for('error_page', message=str(e)))
    finally:
        if conn:
            conn.close()

# --- Get Detected Items Route (HTML) ---
@app.route('/detected')
def get_detected_items():
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM DetectedItems")
        detected_items = cursor.fetchall()

        # Render an HTML template and pass the data to it
        return render_template('detected_items.html', detected_items=detected_items)
    
    except mysql.connector.Error as err:
        return redirect(url_for('error_page', message=str(err)))
    
    finally:
        if conn:
            conn.close()

# --- Matching System Route ---
@app.route('/match_items')
def match_items():
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500

    try:
        cursor = conn.cursor(dictionary=True)

        # Step 1: Fetch all lost reports and detected items
        cursor.execute("SELECT * FROM LostReports WHERE status = 'Pending'")
        lost_reports = cursor.fetchall()

        cursor.execute("SELECT * FROM DetectedItems WHERE status = 'Unclaimed'")
        detected_items = cursor.fetchall()

        new_matches_count = 0
        matches_to_insert = []

        # Step 2: Implement the matching logic
        if lost_reports and detected_items:
            for report in lost_reports:
                for item in detected_items:
                    confidence = 0.0

                    # Basic matching logic based on item names
                    if report['item_name'].lower() == item['item_type'].lower():
                        confidence += 0.5
                    
                    # TODO: Add more sophisticated matching (e.g., location, time, etc.)
                    # Example: if report['location_reported'] == item['location_detected']:
                    #              confidence += 0.3
                    
                    if confidence >= 0.5: # Example threshold
                        matches_to_insert.append((report['report_id'], item['item_id'], confidence))

        # Step 3: Insert new matches into the Matches table
        if matches_to_insert:
            sql = "INSERT INTO Matches (report_id, item_id, confidence_score) VALUES (%s, %s, %s)"
            cursor.executemany(sql, matches_to_insert)
            conn.commit()
            new_matches_count = cursor.rowcount

        return f"Matching logic executed. Found and inserted {new_matches_count} new matches."

    except mysql.connector.Error as err:
        conn.rollback()
        return redirect(url_for('error_page', message=str(err)))

    finally:
        if conn:
            cursor.close()
            conn.close()
# User profile route
@app.route('/profile')
def profile():
    user_name = session.get('user_name')
    user_email = session.get('user_email')
    reports = []
    detected_items = []
    if user_email:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT user_id FROM users WHERE email = %s", (user_email,))
            user_row = cursor.fetchone()
            user_id = user_row['user_id'] if user_row else None
            if user_id:
                cursor.execute("SELECT * FROM LostReports WHERE user_id = %s", (user_id,))
                reports = cursor.fetchall()
                cursor.execute("SELECT * FROM DetectedItems WHERE user_id = %s", (user_id,))
                detected_items = cursor.fetchall()
            cursor.close()
            conn.close()
    return render_template('profile.html', user_name=user_name, user_email=user_email, reports=reports, detected_items=detected_items)

# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('home'))
# Route to display the login page
@app.route('/login')
def login_page():
    return render_template('login.html')

# Route to display the sign-up page
@app.route('/signup')
def signup_page():
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)