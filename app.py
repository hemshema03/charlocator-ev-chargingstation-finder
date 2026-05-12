import os
import re
import random
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from flask import Flask, render_template, url_for, request, redirect, session, jsonify, flash
from DBConnection import Db

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-this")



#//////////////////////////////////////////////////////////////COMMON/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/find_your_charger')
def find_your_charger():
    return render_template('find_your_charger.html')

@app.route('/about')
def about():
    return render_template('about.html')




@app.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        feedback = request.form['message']
        db = Db()
        sql = db.insert("INSERT INTO contact_us (Name, Email, feedback_date, feedback) VALUES (%s, %s, NOW(), %s)", (name, email, feedback))
        return render_template('contact_us.html', message='Thank you for your feedback!')
    else:
        return render_template('contact_us.html')





@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == "POST":
        # Validate email input
        email = request.form.get('email', '').strip()
        if not email:
            return "Email is required", 400
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return "Invalid email format", 400

        # Check if email exists in database
        db = Db()
        user = db.selectOne("SELECT * FROM login WHERE email=%s", (email,))
        if not user:
            return "Sorry, we couldn't find an account associated with that email address.", 400

         # Send email with passw    ord reset instructions or link
        password = user['password']
        sender_email = os.environ.get("MAIL_USERNAME", "")
        sender_password = os.environ.get("MAIL_PASSWORD", "")
        recipient_email = email
        subject = "Password Reset for EV STATION BOOKING WEBSITE"
        content = "Your password for EV STATION BOOKING WEBSITE has been reset. Please login with your new password."
        host = "smtp.gmail.com"
        port = 465
        message = MIMEMultipart()
        message['From'] = Header(sender_email)
        message['To'] = Header(recipient_email)
        message['Subject'] = Header(subject)
        message.attach(MIMEText(content, 'plain', 'utf-8'))
        try:
            with smtplib.SMTP_SSL(host, port) as server:            
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, message.as_string())

                return "An email has been sent to your email address with instructions on how to reset your password."
        except smtplib.SMTPAuthenticationError:
            return "Failed to authenticate with the email server. Please check your email credentials.", 500
        except smtplib.SMTPException as e:
            return f"An error occurred while sending the email: {str(e)}", 500

    return render_template("forgot_password.html")








@app.route('/login',methods=['GET', 'POST'])
def login():
    if  'user_type' in session and session['user_type'] == "admin":
        return redirect('/admin-home')

    if request.method == "POST":
        print('form ', request.form)
        username = request.form['username']
        password = request.form['password']
        db = Db()
        ss = db.selectOne("select * from login where username=%s and password=%s", (username, password))
        if ss is not None:
            session['head'] = ""
            session['username'] = username # set the username key in the session
            if ss['usertype'] == 'admin':
                session['user_type'] = 'admin'
                return redirect('/admin-home')

            elif ss['usertype'] == 'user':
                session['user_type'] = 'user'
                session['uid'] = ss['login_id']
                return redirect('/user-dashboard')
            else:
                return '''<script>alert('user not found');window.location="/login"</script>'''
        else:
            return '''<script>alert('user not found');window.location="/login"</script>'''
    return render_template("login.html")


@app.route('/logout')
def logout():
    session.pop('username',None)
    session.pop('user_type',None)
    session.pop('log',None)
    session.pop('usertype',None)

    return redirect('/login')



    # =========================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['signupUsername']
        email = request.form['email']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']

        # Perform form validation
        if username.strip() == '':
            return redirect(url_for('register', error='Please enter a username', form_id='createAccount'))

        if email.strip() == '':
            return redirect(url_for('register', error='Please enter an email address', form_id='createAccount'))

        if password.strip() == '':
            return redirect(url_for('register', error='Please enter a password', form_id='createAccount'))

        if confirmPassword.strip() == '':
            return redirect(url_for('register', error='Please confirm the password', form_id='createAccount'))

        if password != confirmPassword:
            return redirect(url_for('register', error='Passwords do not match', form_id='createAccount'))

        db = Db()
        login_id = db.insert("INSERT INTO login (username, password, usertype) VALUES (%s, %s, 'user')", (username, password))
        db.insert("INSERT INTO user_dashboard (login_id, credit_points, reward_claimed, discount_percentage) VALUES (%s, 0, 0, 0)", (login_id,))

        return '<script>alert("User registered"); window.location.href="/login";</script>'
    else:
        error = request.args.get('error')  # Get the error message from the URL parameters
        return render_template("login.html", error=error , form_id='createAccount')






#////////////////////////////////////////////////////////////ADMIN///////////////////////////////////////////////////////////////////////////////////////////////////////////////////



@app.route('/admin-home')
def admin_home():
    print('session ', session)
    if session.get('user_type') == 'admin':
        username = session['username'] # get the username from the session
        return render_template('admin/admin-login-dashboard.html', username=username)
    else:
        return redirect('/')



# ✅ Route 1: Display the Station Table (Using `Db()` Class)
@app.route('/Manage_station')
def Manage_station():
    if 'user_type' in session and session['user_type'] == 'admin':
        db = Db()
        qry = db.select("SELECT station_id, station_name, address, city, charger_type, available_ports FROM admin_charging_station_list")
        return render_template("admin/Manage_station.html", data=qry)
    else:
        return redirect('/')

# ✅ Route 2: Add a New Charging Station (Using `Db()` Class)
@app.route('/add_station', methods=['POST'])
def add_station():
    if 'user_type' in session and session['user_type'] == 'admin':
        station_name = request.form['station_name']
        address = request.form['address']
        city = request.form['city']
        charger_type = request.form['charger_type']
        available_ports = request.form['available_ports']

        db = Db()
        db.insert(
            "INSERT INTO admin_charging_station_list (station_name, address, city, charger_type, available_ports) VALUES (%s, %s, %s, %s, %s)",
            (station_name, address, city, charger_type, available_ports)
        )

        return redirect('/Manage_station')
    else:
        return redirect('/')

@app.route('/adm_delete_station/<int:station_id>')
def adm_delete_station(station_id):
    if 'user_type' in session and session['user_type'] == 'admin':
        db = Db()
        db.delete("DELETE FROM admin_charging_station_list WHERE station_id=%s", (station_id,))
        return '''<script>alert("Station deleted successfully!"); window.location="/Manage_station";</script>'''
    else:
        return redirect('/')



# =============================contact_us
@app.route('/view_feedback')
def view_feedback():
    print('session ', session)
    if session.get('user_type') == 'admin':
        db=Db()
        ss=db.select("select * from contact_us")
        return render_template("admin/view_feedback.html",data=ss)
    else:
        return redirect('/')

# 




# =======================================





@app.route("/adm_delete_feedback/<int:feedback>")
def adm_delete_feedback(feedback):
    if 'user_type' in session and session['user_type'] == 'admin':
        db = Db()
        qry = db.delete("DELETE FROM contact_us WHERE Sl_no = %s", (feedback,))
        return '''<script>alert('Feedback deleted');window.location="/view_feedback"</script>'''
    else:
        return redirect('/')




@app.route('/user-list')
def user_list():
    print('session ', session)
    if session.get('user_type') == 'admin':
        db=Db()
        qry = db.select("SELECT * FROM user")
        return render_template("admin/user-list.html",data=qry)
    else:
        return redirect('/')


# ==================delete user===========
@app.route("/adm_delete_user/<user_id>")
def adm_delete_user(user_id):
    print('session ', session)
    if session.get('user_type') == 'admin':
        db = Db()
        qry = db.delete("DELETE FROM user WHERE user_id=%s", (user_id,))
        return '''<script>alert('user deleted');window.location="/user-list"</script>'''
    else:
        return redirect('/')
# ==============view booking=========================

@app.route('/view_booking')
def view_booking():
    print('session:', session)
    
    if session.get('user_type') == 'admin':  # Use get() to avoid KeyError
        db = Db()
        
        query = """SELECT booking.Booking_id, booking.Booking_date, booking.Time_from, 
                          booking.Time_to, booking.City, booking.Station_name, 
                          booking.Available_ports, login.username, 
                          booking.original_price, booking.total_price, booking.discount_applied 
                   FROM booking  
                   JOIN login ON booking.login_id = login.login_id  
                   ORDER BY booking.Booking_id DESC;"""  # Newest bookings first

        bookings = db.select(query)

        # Convert Decimal to float for price calculations
        for booking in bookings:
            booking['original_price'] = float(booking['original_price'])
            booking['total_price'] = float(booking['total_price'])

        return render_template('admin/view_booking.html', bookings=bookings)
    else:
        return redirect('/')


# ===========delete booking

@app.route("/adm_delete_booking/<Booking_id>")
def adm_delete_booking(Booking_id):
    print('session ', session)
    if session.get('user_type') == 'admin':
        db = Db()
        qry = db.delete("DELETE FROM booking WHERE Booking_id=%s", (Booking_id,))
        return '''<script>alert('booking deleted');window.location="/view_booking"</script>'''
    else:
        return redirect('/')



#//////////////////////////////////////////////////////////////USER//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# -----------

from decimal import Decimal

@app.route('/user-dashboard')
def user_dashboard():
    if 'user_type' in session and session['user_type'] == "user":
        username = session['username']
        login_id = session['uid']
        db = Db()

        # Fetch user bookings with original price (before discount)
        bookings = db.select("""
            SELECT Booking_id, Booking_date, Time_from, Time_to, City, Station_name, Available_ports, 
                   total_price, discount_applied, 
                   (total_price / 0.9) AS original_price  -- Reverse calculation to get original price
            FROM booking 
            WHERE login_id = %s 
            ORDER BY Booking_id DESC
        """, (login_id,))

        # Convert Decimal values to float
        for booking in bookings:
            booking['total_price'] = float(booking['total_price'])
            booking['original_price'] = float(booking['original_price']) if booking['discount_applied'] else booking['total_price']

        # Fetch user's credit points
        user = db.selectOne("SELECT credit_points FROM user_dashboard WHERE login_id = %s", (login_id,))
        credit_points = user['credit_points'] if user else 0

        return render_template("user/user-login-dashboard.html", bookings=bookings, username=username, credit_points=credit_points)
    else:
        return redirect('/')

@app.route('/usr_delete_booking/<int:booking_id>')
def usr_delete_booking(booking_id):
    if 'user_type' in session and session['user_type'] == "user":
        db = Db()
        
        # Delete the booking for the specific user and booking_id
        db.delete("DELETE FROM booking WHERE booking_id = %s AND login_id = %s", (booking_id, session['uid']))
        
        return '''<script>alert('Booking deleted');window.location="/user-dashboard"</script>'''
    else:
        return redirect('/user-dashboard')



# TODO: Fix the DB (FK, table etc) and frontend field and backend Field

# @app.route('/user-profile', methods=['GET', 'POST'])
# def user_profile():
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         password = request.form['password']
#         confirm_password = request.form['confirm-password']
        
#         if password != confirm_password:
#             return redirect(url_for('user_profile', error='Passwords do not match'))
        
#         db = Db()
#         qry = db.update("UPDATE login SET name = %s, email = %s, password = %s WHERE username = %s", (name, email, password, session['username']))  # Assuming you have stored the logged-in user's username in the session
#         return '<script>alert("Account details updated"); window.location.href="/user-profile";</script>'

#     error = request.args.get('error')
#     return render_template('user/user-profile.html', error=error)




@app.route('/user_find_your_charger', methods=['GET', 'POST'])
def user_find_your_charger():
    if 'user_type' in session and session['user_type'] == 'user':
        if request.method == 'POST':
            city = request.form.get('City')
            charger_type = request.form.get('Charger_type')
            db = Db()
            qry = db.select("select Station_name, Address, Charger_type, Available_ports from admin_charging_station_list where City = %s and Charger_type = %s", (city, charger_type))
            return render_template('user/station_search.html', data=qry)       
        else:
            return render_template('user/user_find_your_charger.html')
    else:
        return redirect('/')




@app.route('/search_stations', methods=['POST'])
def search_stations():
    # Get the form data
    City = request.form.get('City')
    Charger_type = request.form.get('Charger_type')

    # Redirect to the station_list page with the city and charger_type as URL parameters
    return redirect(url_for('station_search', City=City, Charger_type=Charger_type))


@app.route('/station_search', methods=['GET'])
def station_search():
    if 'user_type' in session and session['user_type'] == 'user':
        City = request.args.get('City')
        Charger_type = request.args.get('Charger_type')
        # Query your MySQL database using the city and charge_type variables
        db = Db()
        sql = "select * from admin_charging_station_list where City = %s and Charger_type = %s"
        ss = db.select(sql, (City, Charger_type))

        # Return the results to the user in a new template
        return render_template('user/station_search.html', data=ss, City=City, Charger_type=Charger_type)
    else:
        return redirect('/')

# ==============from station_search to booking page====================
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        Station_name = request.form['Station_name']
        City = request.form['City']
        Available_ports = request.form['Available_ports']
        return redirect(url_for('booking_form',  Station_name=Station_name, City=City, Available_ports=Available_ports))
    else:
        # handle GET request to display the form
        Station_name = request.args.get('Station_name')
        City = request.args.get('City')
        Available_ports = request.args.get('Available_ports')
        return redirect(url_for('booking_form', Station_name=Station_name, City=City, Available_ports=Available_ports))

@app.route('/booking-form', methods=['GET'])
def booking_form():
    if 'user_type' in session and session['user_type'] == "user":
        city = request.args.get('City')
        available_ports = request.args.get('Available_ports')
        station_name = request.args.get('Station_name')
        
        db = Db()
        
        # Fetch station data
        station_data = db.select("SELECT * FROM admin_charging_station_list WHERE Station_name = %s", (station_name,))
        session['station_data'] = station_data[0] if station_data else None

        # Fetch reward_claimed status for the user
        login_id = session['uid']
        user = db.selectOne("SELECT reward_claimed FROM user_dashboard WHERE login_id = %s", (login_id,))
        reward_claimed = user['reward_claimed'] if user else 0  # Default to 0 if not found

        if 'station_data' in session and session['station_data']:
            return render_template('/user/booking_form.html', city=city, available_ports=available_ports, station_name=station_name, reward_claimed=reward_claimed)
        else:
            return redirect(url_for('station_search'))
    else:
        return redirect('/')







@app.route('/book', methods=['POST'])
def book():
    if 'user_type' in session and session['user_type'] == 'user':
        station_name = request.form['Station_name']
        city = request.form['City']
        available_ports = request.form['Available_ports']
        booking_date = request.form['Booking_date']
        time_from = request.form['Time_from']
        time_to = request.form['Time_to']
        login_id = session['uid']
        price_per_hour = Decimal(100)  # Set default price
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Calculate duration and original price
        time_format = "%H:%M"
        duration = (datetime.strptime(time_to, time_format) - datetime.strptime(time_from, time_format)).seconds / 3600
        original_price = round(Decimal(duration) * price_per_hour, 2)  # Ensure Decimal for precision

        db = Db()
        discount_applied = 0
        discount_percentage = Decimal(0)
        total_price = original_price  # Default total price

        # Check if user has a discount (Fixed 10% Discount)
        user = db.selectOne("SELECT reward_claimed FROM user_dashboard WHERE login_id = %s", (login_id,))
        if user and user['reward_claimed'] == 1:
            discount_percentage = Decimal(10)  # Fixed 10% discount
            total_price = round(original_price * Decimal(0.9), 2)  # Apply fixed 10% discount
            discount_applied = 1

            # Reset reward after applying discount
            db.update("UPDATE user_dashboard SET reward_claimed = 0 WHERE login_id = %s", (login_id,))

        # Insert booking with the correct prices and discount status
        sql = """INSERT INTO booking 
                 (Station_name, City, Available_ports, Booking_date, Time_from, Time_to, Created_id, login_id, 
                 original_price, total_price, discount_applied, discount_percentage) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        db.insert(sql, (station_name, city, available_ports, booking_date, time_from, time_to, created_at, login_id, 
                        original_price, total_price, discount_applied, discount_percentage))

        # Update user credit points (add 5 points)
        user = db.selectOne("SELECT credit_points FROM user_dashboard WHERE login_id = %s", (login_id,))
        new_credit_points = (user['credit_points'] + 5) if user else 5
        db.update("UPDATE user_dashboard SET credit_points = %s WHERE login_id = %s", (new_credit_points, login_id))

        return redirect('/user-dashboard')

    return redirect('/booking-form')



@app.route('/claim_reward', methods=['POST'])
def claim_reward():
    if 'user_type' in session and session['user_type'] == "user":
        login_id = session['uid']
        db = Db()

        # Check if user has enough points
        user = db.selectOne("SELECT credit_points FROM user_dashboard WHERE login_id = %s", (login_id,))
        if user and user['credit_points'] >= 20:
            # Generate a random discount between 10% and 25%
            discount_percentage = random.randint(10, 25)

            # Update user_dashboard to store the discount and reset points
            db.update("UPDATE user_dashboard SET reward_claimed = 1, discount_percentage = %s, credit_points = 0 WHERE login_id = %s",
                      (discount_percentage, login_id))

            return jsonify({
                "message": f"Successfully claimed! 🎉 You will get {discount_percentage}% discount on your next booking.",
                "discount": discount_percentage
            })

    return jsonify({"message": "Not enough credit points to claim reward"}), 400






if __name__ == '__main__':        
    app.run(host='127.0.0.1', port=5000, debug=True)
