import os

import json
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for, send_from_directory, abort
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import uuid

from helpers import apology, login_required, lookup, pretty_date, date

alert = False

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Configure application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# allows the custom functions from helpers.py to be used in the jinja template
app.jinja_env.filters["pretty_date"] = pretty_date
app.jinja_env.filters["date"] = date

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
# db = SQL("sqlite:///traveler.db")
db = SQL(os.getenv("DATABASE_URL"))

# creates the index page that shows all the countries
@app.route("/")
@login_required
def index():
    countries = ["Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan",
                 "The Bahamas", "Bahrain", "Bangladesh", "Barbadoes", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi",
                 "Cambodia", "Cameroon", "Canada", "Cape Verde", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Democratic Republic of the Congo", "Republic of the Congo", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic",
                 "Denmark", "Djibouti", "Dominica", "Dominican Republic",
                 "East Timor", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia",
                 "Fiji", "Finland", "France",
                 "Gabon", "The Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana",
                 "Haiti", "Honduras", "Hungary",
                 "Iceland", "India", "Indonesia", "Iran", "Iraq", "Republic of Ireland", "Israel", "Italy", "Ivory Coast",
                 "Jamaica", "Japan", "Jordan",
                 "Kazakhstan", "Kenya", "Kiribati", "Kuwait", "Kyrgyzstan",
                 "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg",
                 "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Federated States of Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar",
                 "Namibia", "Nauru", "Nepal", "Kingdom of the Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia", "Norway",
                 "Oman",
                 "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal",
                 "Qatar",
                 "Romania", "Russia", "Rwanda",
                 "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria",
                 "Tajikistan", "Tanzania", "Thailand", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu",
                 "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan",
                 "Vanuatu", "Venezuela", "Vietnam",
                 "Yemen",
                 "Zambia", "Zimbabwe"]

    return render_template("index.html", countries = countries)


# redirects to a page that explains what the aim of the website is
@app.route("/about", methods=["GET", "POST"])
def about():

    if request.method == "POST":
        return render_template("about.html")

    else:
        return render_template("about.html")

# renders all the current user's posts
@app.route("/posts")
@login_required
def posts():
    images = db.execute("SELECT * FROM filecontent WHERE user_id=:user_id", user_id=session["user_id"])
    if not images:
        return render_template("nopost.html")
    comments = db.execute("SELECT * FROM Comments")
    current_user = session['user_id']
    return render_template("posts.html", images=images, comments=comments, current_user=current_user)

# login page
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username!")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password!")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password!")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

# logs the user out
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# allows the user to register and then takes them directly into the site
@app.route("/register", methods=["GET", "POST"])
def register():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username!")
            return render_template("register.html")

        elif db.execute("SELECT username FROM users WHERE username = :username", username=request.form.get("username")):
            flash("Username already taken!")
            return render_template("register.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password!")
            return render_template("register.html")

        elif len(request.form.get("password")) < 4:
            flash("Password must be at least 4 characters!")
            return render_template("register.html")

        elif not request.form.get("confirmation"):
            flash("Must confirm password!")
            return render_template("register.html")

        elif request.form.get("password") != request.form.get("confirmation"):
            flash("passwords do not match!")
            return render_template("register.html")

        username = request.form.get("username")
        hash = generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=hash)

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=username)
        session["user_id"] = rows[0]["id"]
        flash("Thanks for registering! Welcome to Traveler!", "success")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

# when the user uses the search bar, this function determines what page the website will load
@app.route("/search", methods=["GET", "POST"])
@login_required
def search():

    if request.method == "POST":
        if not request.form.get("names"):
            flash("Must provide input to search!", 'error')
            return redirect("/")

        countries = ["Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan",
             "The Bahamas", "Bahrain", "Bangladesh", "Barbadoes", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi",
             "Cambodia", "Cameroon", "Canada", "Cape Verde", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Democratic Republic of the Congo", "Republic of the Congo", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic",
             "Denmark", "Djibouti", "Dominica", "Dominican Republic",
             "East Timor", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia",
             "Fiji", "Finland", "France",
             "Gabon", "The Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana",
             "Haiti", "Honduras", "Hungary",
             "Iceland", "India", "Indonesia", "Iran", "Iraq", "Republic of Ireland", "Israel", "Italy", "Ivory Coast",
             "Jamaica", "Japan", "Jordan",
             "Kazakhstan", "Kenya", "Kiribati", "Kuwait", "Kyrgyzstan",
             "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg",
             "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Federated States of Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar",
             "Namibia", "Nauru", "Nepal", "Kingdom of the Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia", "Norway",
             "Oman",
             "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal",
             "Qatar",
             "Romania", "Russia", "Rwanda",
             "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria",
             "Tajikistan", "Tanzania", "Thailand", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu",
             "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan",
             "Vanuatu", "Venezuela", "Vietnam",
             "Yemen",
             "Zambia", "Zimbabwe"]

        for country in countries:
            if country.lower() == request.form.get("names").lower():
                return redirect(url_for('post', country_name=country))

        flash("Country not found!", "error")
        return redirect("/")

    else:
        return redirect("/")

# followed this tutorial for file uploading -> https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# allows the user to upload files
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('Must provide file!')
            return render_template("upload.html")
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return render_template("upload.html")

        if not request.form.get("location"):
            flash("Must provide specific location!")
            return render_template("upload.html")

        if not request.form.get("country"):
            flash("Must provide country!")
            return render_template("upload.html")

        countries = ["Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan",
             "The Bahamas", "Bahrain", "Bangladesh", "Barbadoes", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi",
             "Cambodia", "Cameroon", "Canada", "Cape Verde", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Democratic Republic of the Congo", "Republic of the Congo", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic",
             "Denmark", "Djibouti", "Dominica", "Dominican Republic",
             "East Timor", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia",
             "Fiji", "Finland", "France",
             "Gabon", "The Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana",
             "Haiti", "Honduras", "Hungary",
             "Iceland", "India", "Indonesia", "Iran", "Iraq", "Republic of Ireland", "Israel", "Italy", "Ivory Coast",
             "Jamaica", "Japan", "Jordan",
             "Kazakhstan", "Kenya", "Kiribati", "Kuwait", "Kyrgyzstan",
             "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg",
             "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Federated States of Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar",
             "Namibia", "Nauru", "Nepal", "Kingdom of the Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia", "Norway",
             "Oman",
             "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal",
             "Qatar",
             "Romania", "Russia", "Rwanda",
             "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria",
             "Tajikistan", "Tanzania", "Thailand", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu",
             "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan",
             "Vanuatu", "Venezuela", "Vietnam",
             "Yemen",
             "Zambia", "Zimbabwe"]

        if not request.form.get("country") in countries:
            flash("Invalid country!")
            return render_template("upload.html")

        if file and allowed_file(file.filename):
            location = request.form.get("location")
            country = request.form.get("country")
            filename = uuid.uuid4().hex + file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            username = db.execute("SELECT username FROM users WHERE id=:id", id=session["user_id"])
            db.execute("INSERT INTO filecontent (name, user_id, location, country, username) VALUES (:name, :user_id, :location, :country, :username)", name=filename, user_id=session["user_id"], location=location, country=country, username=username[0]['username'])
            flash("Image Uploaded!", 'success')
            return redirect("/posts")

    return render_template("upload.html")

# accessed using ajax and jquery which regulates the like button
@app.route('/like', methods=['POST'])
@login_required
def like():
    id = request.form['post_id']
    action = request.form['action']
    if id and action:
        if action == 'LIKE':
            db.execute("UPDATE filecontent SET likes=likes+1 WHERE id=:id", id=id)
            db.execute("INSERT INTO likes (user_id, post_id) VALUES (:user_id, :post_id)", user_id=session["user_id"], post_id=id)
        elif action == 'UNLIKE':
            db.execute("UPDATE filecontent SET likes=likes-1 WHERE id=:id", id=id)
            db.execute("DELETE FROM likes WHERE user_id=:user_id AND post_id=:post_id", user_id=session["user_id"], post_id=id)
        likez = db.execute("SELECT likes FROM filecontent WHERE id=:id", id=id)
        likes = likez[0]['likes']
        return jsonify({'likes' : likes})
    else:
        flash("error!")
        return redirect("/")

# renders all the images in a specific country
@app.route("/country/<country_name>")
def post(country_name):
        country = country_name
        country = db.execute("SELECT * FROM filecontent WHERE country=:country", country=country)
        if not country:
            flash("Country does not yet have images!", "error")
            return redirect("/")
        likes = db.execute("SELECT * FROM likes")
        comments = db.execute("SELECT * FROM Comments")
        current_user = session['user_id']
        return render_template('country.html', country=country, comments=comments, likes=likes, current_user=current_user)

# deletes a specific post
# recieved much help from this youtube tutorial https://www.youtube.com/watch?v=u0oDDZrDz9U&list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH&index=8
@app.route("/post/<int:post_id>/delete")
def delete_post(post_id):
        id = post_id
        image = db.execute("SELECT id, user_id, name, location, country, likes FROM filecontent WHERE id=:id", id=id)
        if not image:
            flash("Post not found!")
            return redirect("/")
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image[0]['name']))
        db.execute("DELETE FROM filecontent WHERE id=:id", id=id)
        db.execute("DELETE FROM Comments WHERE post_id=:post_id", post_id=id)
        db.execute("DELETE FROM likes WHERE post_id=:post_id", post_id=id)
        return redirect('/posts')

# allows users to comment on other posts
@app.route("/comment/<int:post_id>", methods=["POST"])
def comment(post_id):
    if request.method == 'POST':
        id = post_id
        image = db.execute("SELECT id, name, location, country, likes FROM filecontent WHERE id=:id", id=id)
        user = db.execute("SELECT username FROM users WHERE id=:id", id=session['user_id'])
        if not image:
            flash("Image not found!", 'error')
            return redirect("/")
        link = '/country/' + image[0]['country']

        if not request.form.get("comment" + str(id)):
            flash("Must provide comment!", 'error')
            return redirect(request.referrer)

        db.execute("INSERT INTO Comments (post_id, name, user_id, comment) VALUES (:post_id, :name, :user_id, :comment)", post_id=id, name=user[0]['username'], user_id=session["user_id"], comment=request.form.get("comment" + str(id)))
        return redirect(request.referrer)
    else:
        return redirect("/")

# allows users to delete comments
@app.route("/comment/<int:comment_id>/delete")
def delete_comment(comment_id):
        id = comment_id
        comment = db.execute("SELECT * FROM Comments WHERE id=:id", id=id)
        if not comment:
            flash("Comment not found!", "error")
            return redirect("/")
        db.execute("DELETE FROM Comments WHERE id=:id", id=id)
        return redirect(request.referrer)

# renders a page with just the posts of a specific user
@app.route("/user/<username>")
def user(username):
        id = username
        posts = db.execute("SELECT * FROM filecontent WHERE username=:username", username=id)
        if not posts:
            flash("No such user exists!", "error")
            return redirect("/")
        likes = db.execute("SELECT * FROM likes")
        comments = db.execute("SELECT * FROM Comments")
        current_user = session['user_id']
        return render_template('user.html', posts=posts, comments=comments, likes=likes, current_user=current_user)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)