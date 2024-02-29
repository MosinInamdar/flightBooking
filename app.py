import sqlite3
import os
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import userlogin_required,adminlogin_required

from dotenv import load_dotenv

load_dotenv()

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
# app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def get_db_connection():
    conn = sqlite3.connect('flightBooking.db')
    # conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/userhome")
@userlogin_required
def userhome():
    return render_template("userhome.html")

@app.route("/adminhome")
@adminlogin_required
def adminhome():
    return render_template("adminhome.html")

@app.route("/userlogin", methods=["GET", "POST"])
def userlogin():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username=request.form.get("username")
        password = request.form.get("password")
        # Ensure username was submitted
        if not username:
            message = "Please enter your username"
            return render_template("userLogin.html", messages=message)

        # Ensure password was submitted
        elif not password:
            message = "Please enter your password"
            return render_template("userLogin.html", messages=message)
        else:
            conn = get_db_connection()
            # Query database for username
            row = conn.execute("SELECT * FROM Users WHERE username = ?", (username,)).fetchone()

            # Ensure username exists and password is correct
            if row is None or not check_password_hash(row[2], password):
                message = "INVALID USERNAME OR PASSWORD"
                return render_template("userLogin.html",messages=message)

            # Remember which user has logged in
            session["user_id"] = row[0]
            conn.commit()
            conn.close()
            # Redirect user to home page
            return redirect("/userhome")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("userLogin.html")
    
@app.route("/adminlogin", methods=["GET", "POST"])
def adminlogin():
    """Log admin in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username=request.form.get("username")
        password = request.form.get("password")
        # Ensure username was submitted
        if not username:
            message = "Please enter your username"
            return render_template("adminLogin.html", messages=message)

        # Ensure password was submitted
        elif not password:
            message = "Please enter your passsword"
            return render_template("adminLogin.html", messages=message)
        else:
            adminUser = os.getenv("ADMIN_USER")
            adminPassword = os.getenv("ADMIN_PASSWORD")
            
            if adminUser != username or password != adminPassword:
                message="INVALID USERNAME OR PASSWORD"
                return render_template("adminLogin.html",messages=message)

            # Remember which user has logged in
            session["admin_id"] = 1
            # Redirect user to home page
            return redirect("/adminhome")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("adminLogin.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        conn = get_db_connection()
        # Ensure username was submitted
        if not request.form.get("username"):
            message = "must provide username"
            return render_template("register.html",messages=message)

        # Ensure password was submitted
        elif not request.form.get("password"):
            message = "must provide password"
            return render_template("register.html",messages=message)
        
        elif not request.form.get("email"):
            message = "must provide email"
            return render_template("register.html",messages=message)

        # Ensure password was confirmed
        elif request.form.get("password") != request.form.get("confirmation"):
            message= "password don't match"
            return render_template("register.html",messages=message)

        # store the hash of the password and not the actual password that was typed in
        Userpassword = request.form.get("password")
        password = generate_password_hash(Userpassword, method='pbkdf2:sha256', salt_length=8)
        username = request.form.get("username")
        email = request.form.get("email")
        existing_user = conn.execute("SELECT username FROM Users WHERE username = ?", (username,)).fetchone()

        if existing_user == username:
            message = "User already exists"
            return render_template("register.html",messages = message)
        else:
            # Assuming 'password' is already defined somewhere in your code
            insert = conn.execute("INSERT INTO Users (username, password, email) VALUES (?, ?, ?)", 
                        (username, password, email))
            # Check if the insertion was successful
            if not insert:
                message = "Failed to register user"
                return render_template("register.html",messages = message)

        conn.commit()
        conn.close()
        # Redirect user to home page
        return redirect("/userlogin")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")



# def errorhandler(e):
#     """Handle error"""
#     if not isinstance(e, HTTPException):
#         e = InternalServerError()
#     return flash('Something went wrong')


# # Listen for errors
# for code in default_exceptions:
#     app.errorhandler(code)(errorhandler)


# Route for searching flights based on date and time of arrival
@app.route('/searchflights', methods=['GET','POST'])
@userlogin_required
def searchflights():
    if request.method == "GET":
        # Retrieve date and time of arrival from the request parameters
        flight_date = request.args.get('arrival_date')
        arrival_time = request.args.get('arrival_time')

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to retrieve flight details based on date and time of arrival
        cursor.execute("SELECT * FROM FlightDetails WHERE flight_date >= ? AND arrival_time >= ?", (flight_date, arrival_time,))
        flights = cursor.fetchall()

        # Close the database connection
        conn.close()
        
        # Convert the result into a dictionary for JSON response
        flight_list = []
        for flight in flights:
            flight_dict = {
                'flight_id': flight[0],
                'flight_number': flight[1],
                'departure_location': flight[2],
                'arrival_location': flight[3],
                'departure_time': flight[4],
                'arrival_time': flight[5],
                'capacity': flight[6],
                'available_seats': flight[7],
                'flight_date': flight[8],
                'flight_name': flight[9]
            }
            flight_list.append(flight_dict)
        if not flight_date:
            return render_template('searchflights.html')
        elif not arrival_time:
            return render_template('searchflights.html')
        else:
            return render_template('searchflights.html',flights = flight_list, arrival_date=flight_date, arrival_time=arrival_time)
    if request.method == "POST":
            user_id = session['user_id']
            # Get the flight_id from the form data
            flight_id = request.form.get('flight_id')
                
            # Assuming num_tickets is also provided in the form data
            num_tickets = request.form.get('num_tickets')

            # Connect to the database and insert booking details
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                # Begin transaction
                cursor.execute("BEGIN TRANSACTION")
                    
                # Insert booking details into BookingDetails table
                cursor.execute("INSERT INTO BookingDetails (user_id, flight_id, num_tickets) VALUES (?, ?, ?)", (user_id, flight_id, num_tickets))
                # Query to retrieve flight details based on date and time of arrival
                cursor.execute("SELECT * FROM BookingDetails WHERE user_id = ?",(user_id,))
                bookings = cursor.fetchall()
                # Convert the result into a dictionary for JSON response
                booking_list = []
                for booking in bookings:
                    booking_dict = {
                        'booking_id':booking[0],
                        'user_id' : booking[1],
                        'flight_id': booking[2],
                        'booking_time': booking[3],
                        'num_tickets': booking[4]
                    }
                    booking_list.append(booking_dict)
                    # Get the current available seats and capacity for the flight
                cursor.execute("SELECT available_seats FROM FlightDetails WHERE flight_id = ?", (flight_id,))
                result = cursor.fetchone()
                available_seats = result[0]      
                    # Calculate remaining available seats after booking
                remaining_seats = int(available_seats) - int(num_tickets)
                    
                    # Check if remaining seats are not negative
                if remaining_seats >= 0:
                        # Update available seats in FlightDetails table
                    cursor.execute("UPDATE FlightDetails SET available_seats = ? WHERE flight_id = ?", (remaining_seats, flight_id))
                        # Commit transaction
                    conn.commit()
                    message = "Booking successful!"
                else:
                        # Rollback transaction if booking fails due to insufficient seats
                    conn.rollback()
                    message = "Booking failed. Not enough seats available."
            except Exception as e:
                    # Rollback transaction if any error occurs
                conn.rollback()
                message = "Booking failed. Please try again."
            finally:
                    # Close connection
                    conn.close()

            return render_template('mybookings.html',message=message,bookings=booking_list)


@app.route('/addflights', methods=['POST','GET'])
@adminlogin_required
def addflights():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Check if all form fields are filled
        required_fields = ['flight_number', 'departure_location', 'arrival_location', 
                           'departure_time', 'arrival_time', 'capacity', 
                           'available_seats', 'flight_date', 'flight_name']
        for field in required_fields:
            if not request.form.get(field):
                flash(f"Please provide {field.replace('_', ' ').title()}")  # Flash message for missing field
                return redirect('/addflights')  # Redirect back to the form
                    
        flight_number = request.form['flight_number']
        departure_location = request.form['departure_location']
        arrival_location = request.form['arrival_location']
        departure_time = request.form['departure_time']
        arrival_time = request.form['arrival_time']
        capacity = request.form['capacity']
        available_seats = request.form['available_seats']
        flight_date = request.form['flight_date']
        flight_name = request.form['flight_name']
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('INSERT INTO FlightDetails (flight_number, departure_location, arrival_location, departure_time, arrival_time, capacity, available_seats, flight_date, flight_name) VALUES (?,?,?,?,?,?,?,?,?)',(flight_number, departure_location, arrival_location, departure_time, arrival_time, capacity, available_seats, flight_date, flight_name))
            conn.commit()
            flash("Flight added successfully!")
        except Exception as e:
            conn.rollback()
            flash("An error occurred while adding the flight.")
        finally:
            conn.close()
        # Redirect user to home page
        return redirect("/flightdetails")
    if request.method == 'GET':
        
        # User reached route via GET (as by clicking a link or via redirect)
        return render_template("addflights.html")

@app.route('/flightdetails', methods=['POST','GET'])
@adminlogin_required
def flightdetails():
    if request.method == "GET":
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to retrieve flight details based on date and time of arrival
        cursor.execute("SELECT * FROM FlightDetails")
        flights = cursor.fetchall()

        # Close the database connection
        conn.close()
        
        # Convert the result into a dictionary for JSON response
        flight_list = []
        for flight in flights:
            flight_dict = {
                'flight_id':flight[0],
                'flight_number': flight[1],
                'departure_location': flight[2],
                'arrival_location': flight[3],
                'departure_time': flight[4],
                'arrival_time': flight[5],
                'capacity': flight[6],
                'available_seats': flight[7],
                'flight_date': flight[8],
                'flight_name': flight[9]
            }
            flight_list.append(flight_dict)
        
        if not flights:
            return render_template('flightdetails.html', flights=None)
        else:
            return render_template('flightdetails.html', flights=flight_list)
        
    if request.method == "POST":
        flight_id = request.form.get('flight_id')
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        if not flight_id:
            return render_template('flightdetails.html')
        try:
            
            # Query to retrieve flight details based on date and time of arrival
            cursor.execute("DELETE FROM FlightDetails WHERE flight_id = ?",(flight_id,))
            conn.commit()
            flash("Flight deleted successfully!")
        except Exception as e:
            conn.rollback()
            flash("An error occurred while deleting the flight.")
        finally:
            conn.close()
        # Redirect user to home page
        return redirect("/flightdetails")
            # Close the database connection
    return render_template('flightdetails.html')
    
@app.route("/updateflight/<int:flight_id>", methods=["POST","GET"])
@adminlogin_required
def updateflight(flight_id):
    if request.method == "POST":
        flight_id = flight_id
        if not flight_id:
            return redirect("/flightdetails")
        # Check if all form fields are filled
        required_fields = ['departure_time', 'arrival_time','flight_date', 'flight_name']
        for field in required_fields:
            if not request.form.get(field):
                flash(f"Please provide {field.replace('_', ' ').title()}")  # Flash message for missing field
                return redirect(f'/updateflight/{flight_id}')  # Redirect back to the form
            
        departure_time = request.form['departure_time']
        arrival_time = request.form['arrival_time']
        flight_date = request.form['flight_date']
        flight_name = request.form['flight_name']
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE FlightDetails SET departure_time = ?, arrival_time = ? , flight_date = ?, flight_name = ? WHERE flight_id = ? ',(departure_time, arrival_time,flight_date, flight_name, flight_id))
            conn.commit()
            flash("Flight Updated successfully!")
        except Exception as e:
            conn.rollback()
            flash("An error occurred while updating the flight.")
        finally:
            conn.close()
        # Redirect user to home page
        return redirect("/flightdetails")
    return render_template("updateflight.html", flight_id=flight_id)

@app.route('/mybookings',methods=['GET', 'POST'])
@userlogin_required
def mybookings():
    if request.method == 'GET':
        user_id = session.get('user_id')
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to retrieve flight details based on date and time of arrival
        cursor.execute("SELECT * FROM BookingDetails WHERE user_id = ?",(user_id,))
        bookings = cursor.fetchall()

        # Close the database connection
        conn.close()
        
        # Convert the result into a dictionary for JSON response
        booking_list = []
        for booking in bookings:
            booking_dict = {
                'booking_id':booking[0],
                'user_id' : booking[1],
                'flight_id': booking[2],
                'booking_time': booking[3],
                'num_tickets': booking[4]
            }
            booking_list.append(booking_dict)
        
        if not bookings:
            return render_template('mybookings.html', bookings=None)
        else:
            return render_template('mybookings.html', bookings=booking_list)
        
@app.route('/flightbookings', methods=['GET', 'POST'])
@adminlogin_required
def flightbookings():
    if request.method == 'POST':
        # Get flight number and time from the form
        flight_number = request.form['flight_number']
        arrival_time = request.form['arrival_time']

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to retrieve booking details based on flight number and time
        cursor.execute("SELECT * FROM BookingDetails bd INNER JOIN FlightDetails fd ON bd.flight_id = fd.flight_id WHERE fd.flight_number = ? AND fd.arrival_time = ?", (flight_number, arrival_time))
        bookings = cursor.fetchall()

        # Close the database connection
        conn.close()

        # Convert the result into a dictionary for JSON response
        booking_list = []
        for booking in bookings:
            booking_dict = {
                'booking_id': booking[0],
                'user_id': booking[1],
                'flight_id': booking[2],
                'booking_time': booking[3],
                'num_tickets': booking[4],
                'flight_number': booking[5],  # assuming flight number is available in FlightDetails table
                'departure_time': booking[6]  # assuming departure time is available in FlightDetails table
            }
            booking_list.append(booking_dict)

        if not bookings:
            return render_template('flightbookings.html', bookings=None, message="No Bookings were found")
        else:
            return render_template('flightbookings.html', bookings=booking_list,message = None)
    else:
        # Handle GET request (show form to input flight details)
        return render_template('flightbookings.html')
