from flask import Flask, render_template, request
from scripts.lab_removal import run_lab_removal
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def run_lab_removal_route():
    if request.method == "POST":
        # Get inputs from the form
        db_username = request.form["db_username"]
        db_password = request.form["db_password"]
        #db_host = request.form["db_host"]
        #db_port = request.form["db_port"]
        db_name = request.form["db_name"]
        modified_by_function = request.form["modified_by_function"]

        # Save uploaded file
        file = request.files["excel_file"]
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Run the script
        result = run_lab_removal(file_path, modified_by_function, db_username, db_password, db_name)

        return render_template("result.html", result=result)

    return render_template("lab_removal_form.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
