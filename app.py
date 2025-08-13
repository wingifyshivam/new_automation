from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os

# Initialize app
app = Flask(__name__)
app.secret_key = "your_secret_key"

# In-memory user storage (replace with DB for production)
users = {}

# Dummy scripts list
scripts = [
    {"id": "lab_removal", "name": "Lab Removal Script"}
]

# Root route redirects
@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

# Register route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users:
            flash("Username already exists!", "danger")
        else:
            users[username] = password
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
    return render_template("register.html")

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and users[username] == password:
            session["username"] = username
            session["password"] = password
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials!", "danger")
    return render_template("login.html")

# Logout route
@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))

# Dashboard route
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", scripts=scripts)

# Script form route
@app.route("/script/<script_id>", methods=["GET", "POST"])
def script_form(script_id):
    if "username" not in session:
        return redirect(url_for("login"))

    # Define inputs for scripts
    inputs = []
    template_name = "script_form.html"

    if script_id == "lab_removal":
        # For lab removal, we only ask for the file path since DB creds come from login
        inputs = ["file_path"]
        template_name = "lab_removal_form.html"

    if request.method == "POST":
        db_username = session["username"]   # use login username
        db_password = session["password"]   # use login password
        db_name = request.form.get("db_name")
        modified_by_function = request.form.get("modified_by_function")
        excel_file_path = request.form["excel_file_path"]

        try:
            # Call your script function
            result = run_lab_removal(
                db_username=db_username,
                db_password=db_password,
                db_name=db_name,
                modified_by_function=modified_by_function,
                excel_file_path=filepath
            )
        except Exception as e:
            result = f"Error executing script: {str(e)}"

        return render_template("result.html", result=result)

    # GET request
    return render_template("lab_removal_form.html")
#def script_form(script_id):
#    if "username" not in session:
#        return redirect(url_for("login"))
#
#   # Define inputs for your scripts
#    inputs = []
#    if script_id == "lab_removal":
#        inputs = ["db_username", "db_password", "db_name", "modified_by_function", "excel_file"]
#
#    if request.method == "POST":
#        # Here you would handle the script execution
#        result = f"Script '{script_id}' executed successfully!"
#        return render_template("result.html", result=result)

#    return render_template("script_form.html", script_id=script_id, inputs=inputs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
