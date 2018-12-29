import os, json, sqlite3


from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_mail import Mail, Message
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from helpers import error, login_required


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

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure database
connection = sqlite3.connect("findharvard.db", check_same_thread=False)
db = connection.cursor()

# Configure Flask-Mail and serializer, from https://pythonprogramming.net/flask-email-tutorial/
# and documentation: https://pythonhosted.org/Flask-Mail/
# and https://www.youtube.com/watch?v=vF9n248M1yk
app.config.update(dict(
    MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_DEFAULT_SENDER = 'harvardmeets@gmail.com',
	MAIL_USERNAME = 'harvardmeets@gmail.com',
	MAIL_PASSWORD = 'bIdhev-qadqe6-viqrok'
	))
mail = Mail(app)
serializer = URLSafeTimedSerializer('iyjlxirogs')


@app.route("/")
@login_required
def index():
    return render_template("map.html", events=json.dumps(db.execute("SELECT title, location, description, start, end, latlng FROM events")))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure form submitted correctly
        if not request.form.get("email"):
            return error("must provide email", 403)
        if not request.form.get("password"):
            return error("must provide password", 403)

        cmd = "SELECT hash, id, confirmed FROM users WHERE email = (?)"
        db.execute(cmd, (request.form.get("email"),))
        rows = db.fetchall()
        print(len(rows))
        
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][0], request.form.get("password")):
            return error("invalid username or password", 403)
        if rows[0][2] != 1:
            return error('Please confirm your email. If you just registered, check your email for a confimation link.')

        # Remember which user has logged in
        session["user_id"] = rows[0][1]

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "GET":
        return render_template("register.html")

    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email")
    password = request.form.get("password")

    # Check valid/correct inputs
    if email.find("@") == -1 or not email[email.find("@"):] == "@college.harvard.edu":
        return error("Please use your Harvard email account")
    if len(firstname) < 1:
        return error("You must provide a first name")
    if len(lastname) < 1:
        return error("You must provide a last name")
    if len(password) < 1 or (password != request.form.get("confirmpass")):
        return error("Invalid password")

    cmd = "INSERT INTO users (firstname, lastname, email, hash) VALUES (?,?,?,?)"
    db.execute(cmd, (firstname, lastname, email, generate_password_hash(password)))
    connection.commit()

    # From https://www.youtube.com/watch?v=vF9n248M1yk
    token = serializer.dumps(email, salt='confirm')
    link = url_for('confirm_email', token=token, _external=True)
    msg = Message("HMeets email confirmation")
    msg.add_recipient(email)
    msg.body = render_template("confirmation_email.txt", link=link)
    msg.html = render_template("confirmation_email.html", link=link)
    mail.send(msg)

    return render_template("login.html")

@app.route("/createevent", methods = ["GET", "POST"])
@login_required
def create_event():
    """Log an event in the database"""

    if request.method == "GET":
        return render_template("create_event.html", lat=request.args.get("lat"), lng=request.args.get("lng"))

    if request.method == "POST":

        title = request.form.get("title")
        location = request.form.get("location")
        desc = request.form.get('desc')
        start = request.form.get('start')
        end = request.form.get('end')
        latlng = request.form.get('latlng')
        cmd = "INSERT INTO events (user_id, start, end, title, description, location, latlng) VALUES (?,?,?,?,?,?,?)"
        db.execute(cmd, (session["user_id"], start, end, title, desc, location, latlng))
        connection.commit()

    return "DONE"

@app.route("/confirm_email/<token>")
def confirm_email(token):
    """Confirm a user's email adderss in the database"""

    try:
        email = serializer.loads(token, salt='confirm', max_age=3600)
    except SignatureExpired:
        return error('Your token expired.')
    except BadTimeSignature:
        return error('Bad time signature.')

    # Update table so user is confirmed
    db.execute('UPDATE users SET confirmed=1 WHERE email=?', (email))
    connection.commit()

    return redirect('/')
