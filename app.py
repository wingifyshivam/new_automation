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

    # Define inputs for your scripts
    inputs = []
    if script_id == "lab_removal":
        inputs = ["db_username", "db_password", "db_name", "modified_by_function", "excel_file"]

    if request.method == "POST":
        # Here you would handle the script execution
        result = f"Script '{script_id}' executed successfully!"
        return render_template("result.html", result=result)

    return render_template("script_form.html", script_id=script_id, inputs=inputs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
