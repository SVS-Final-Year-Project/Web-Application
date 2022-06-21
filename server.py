import base64
from urllib import request, response

from flask import Flask, Response, request, render_template, make_response, session, redirect, url_for
import pymongo
import json
from bson.objectid import ObjectId

# For loading and calling the models
import threading
import tensorflow as tf
from tensorflow import keras
import numpy as np
from keras.models import load_model

# For image processing and storing
from PIL import Image
from skimage import transform
import pdfkit
import storage

import random
import string

from datetime import datetime

# Encrypting the password
import math
import bcrypt

# email
from email.message import EmailMessage
import smtplib

import dotenv
import os

dotenv.load_dotenv('.env')

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

msg = EmailMessage()

modelResults = {
    "resnet": {},
    "inception": {},
    "xception": {}
}


try:
    mongo = pymongo.MongoClient(
        host="localhost", port=27017, serverSelectionTimeoutMS=1000)
    db = mongo.svs
    mongo.server_info()
    print("DB connected")
except Exception as ex:
    print(ex)
    print("Error - Cannot connect DB")

# Admin ----------------------------------------------------------------

# Register Admin


@app.route('/register/admin', methods=['GET', 'POST'])
def registerAdmin():
    message = ''
    if "email" in session:
        return redirect(url_for("dashboard"))

    print("Here")
    if request.method == 'POST':
        user = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        email_found = db.admin.find_one({"email": email})
        if email_found:
            message = 'This email already exists in database'
            return render_template('register.html', message=message)
        else:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            admin_input = {'name': user, 'email': email, 'password': hashed}
            db.admin.insert_one(admin_input)
            admin_data = db.admin.find_one({"email": email})
            del admin_data["password"]
            session["name"] = admin_data["name"]
            session["email"] = admin_data["email"]
            return redirect(url_for('dashboard'))
    return render_template('register.html', message=message)


# Login Admin

@app.route('/login/admin', methods=["GET", "POST"])
def loginAdmin():
    message = ''
    if "email" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        print(email)
        email_found = db.admin.find_one({"email": email})
        if email_found:
            print("Here 1")
            email_val = email_found['email']
            passwordcheck = email_found['password']

            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                print("Here 2")
                session["email"] = email_val
                session["name"] = email_found["name"]
                return redirect(url_for('dashboard'))
            else:
                print("Here 3")
                if "email" in session:
                    print("Here 4")
                    return redirect(url_for("dashboard"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            print("Here 5")
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

# Logout Admin


@app.route('/logout', methods=["POST"])
def logout():
    print("Here logout")
    session.pop("email", None)
    session.pop("name", None)
    return redirect(url_for("dashboard"))


# Models --------------------------------------------------------

# Xception Model function

def xceptionModel(np_image):
    load_model = keras.models.load_model("xceptionModelFile")
    prediction = load_model.predict(np_image)
    result = {"prediction": [i[0] for i in prediction][0]}
    # return {"prediction": [i[0] for i in prediction][0]}
    # return "Xception Model complete"
    modelResults["xception"] = result
    print("Xception")


# Inception Model function

def inceptionModel(np_image):
    load_model = keras.models.load_model("inceptionModelFile")
    prediction = load_model.predict(np_image)
    result = {"prediction": [i[0] for i in prediction][0]}
    # return "inception Model complete"
    modelResults["inception"] = result
    print("Inception")


# Resnet Model function

def resnetModel(np_image):
    load_model = keras.models.load_model("resnetModelFile")
    prediction = load_model.predict(np_image)
    className = np.where([i[1] for i in prediction][0]
                         > 0.5, "Normal", "Cyst").tolist()
    print(className)
    result = {"prediction": [i[1] for i in prediction][0], "class": className}
    # return "resnet Model complete"
    modelResults["resnet"] = result


# Reports --------------------------------------

# Get particular user report of a user

@app.route("/report/<userid>/<id>")
def getReport(userid, id):
    if "email" not in session:
        redirect(url_for("dashboard"))
    try:
        report = db.reports.find_one(
            {"user_id": ObjectId(oid=userid), "_id": ObjectId(id)})
        user = db.users.find_one({"_id": ObjectId(userid)})
        print(report)
        return render_template("report.html", report=report, user=user, today=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    except Exception as ex:
        print(ex)
        return redirect(url_for("dashboard"))


# Get all reports of a particular user

@app.route("/report/<id>")
def getUserReports(id):
    if "email" not in session:
        redirect(url_for("dashboard"))
    try:
        print(id)
        reports = list(db.reports.find({'user_id': ObjectId(oid=id)}))
        print(reports)
        admin = False
        if "email" in session:
            admin = {"email": session["email"], "name": session["name"]}
        return render_template("allReports.html", reports=reports, reportsLength=len(reports), admin=admin)
    except Exception as ex:
        print(ex)
        return redirect(url_for("dashboard"))


# Download Report

def image_file_path_to_base64_string(filepath: str) -> str:
    '''
    Takes a filepath and converts the image saved there to its base64 encoding,
    then decodes that into a string.
    '''
    with open(filepath, 'rb') as f:
        return base64.b64encode(f.read()).decode()


@app.route("/report/<userid>/<id>/download")
def downloadReport(userid, id):
    if "email" not in session:
        redirect(url_for("dashboard"))
    try:
        print("Inside download")
        report = db.reports.find_one(
            {"user_id": ObjectId(oid=userid), "_id": ObjectId(id)})
        user = db.users.find_one({"_id": ObjectId(userid)})
        print(report)

        html = render_template(
            "reportTemplate.html", report=report, user=user, today=datetime.now().strftime("%d/%m/%Y %H:%M:%S"), img_string=image_file_path_to_base64_string('static/images/logo.png'))
        css = ['static/css/bootstrap.min.css', 'static/css/icons.min.css',
               'static/css/app.min.css', 'static/css/report.css']
        pdf = pdfkit.from_string(html, False, css=css)
        response = make_response(pdf)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = "attachment; filename=" + \
            report["report_id"]+"report.pdf"

        print("Here")
        return response
    except Exception as ex:
        print(ex)
        return render_template("report.html", report=report, user=user, today=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))


# Email Report

@app.route("/report/<userid>/<id>/email")
def emailReport(userid, id):
    if "email" not in session:
        redirect(url_for("dashboard"))
    try:
        print("Inside Email")
        report = db.reports.find_one(
            {"user_id": ObjectId(oid=userid), "_id": ObjectId(id)})
        user = db.users.find_one({"_id": ObjectId(userid)})
        print(report)
        html = render_template(
            "reportTemplate.html", report=report, user=user, today=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        css = ['static/css/bootstrap.min.css', 'static/css/icons.min.css',
               'static/css/app.min.css', 'static/css/report.css']
        pdf = pdfkit.from_string(html, False, css=css)
        ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        msg.add_attachment(pdf, maintype=maintype,
                           subtype=subtype, filename=report["report_id"]+'.pdf')
        msg['Subject'] = 'SVS Medical Care Report'
        msg['From'] = "srivatsan.ln.2018.cse@rajalakshmi.edu.in"
        msg['To'] = user["email"]

        s = smtplib.SMTP('smtp.gmail.com', 587)

        s.starttls()

        s.login("srivatsan.ln.2018.cse@rajalakshmi.edu.in", 'srivatsan')
        s.send_message(msg)
        s.quit()
        del msg['To']
        return render_template("report.html", report=report, user=user, today=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    except Exception as ex:
        print(ex)
        return render_template("report.html", report=report, user=user, today=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))


# Dashboard --------------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def dashboard():
    print("Dashboard")
    users = []
    try:
        data = list(db.users.find())
        for user in data:
            user["_id"] = str(user["_id"])
            user["reportCount"] = len(user["reports"])
            users = data
        modelCount = db.modelcount.find_one({"name": "model_count"})
    except Exception as ex:
        response = json.dumps(
            {"message": ex})
        print(response)
    counts = {
        "normalCount": modelCount["normal_count"],
        "normalPercentage": math.floor((modelCount["normal_count"]/modelCount["total_prediction_count"])*100),
        "cystCount": modelCount["cyst_count"],
        "cystPercentage": math.floor((modelCount["cyst_count"]/modelCount["total_prediction_count"])*100)
    }
    admin = False
    if "email" in session:
        admin = {"email": session["email"], "name": session["name"]}
    return render_template("index.html", users=users, usersLength=len(users), counts=counts, admin=admin)


# Prediction -------------------------------------------------------


# Creating the user function

def createUser(form):
    try:
        user = {"name": form["name"], "age": form["age"],
                "phone": form["number"], "email": form["email"], "reports": []}
        dbResponse = db.users.insert_one(user)
        print(dbResponse)
        return dbResponse.inserted_id
    except Exception as ex:
        print(ex)


# Prediction page GET

@app.route("/prediction", methods=["GET"])
def prediction():
    admin = False
    if "email" in session:
        admin = {"email": session["email"], "name": session["name"]}
    return render_template("predict.html", admin=admin)


# Prediction function POST

@app.route("/prediction", methods=["POST"])
def predict():
    form = request.form
    email = form["email"]
    file = request.files["file"]

    if email == None or file == None:
        return render_template("predict.html", msg="Please fill the required details!")

    userId = db.users.find_one({"email": email})
    print(userId)
    if(userId == None):
        userId = createUser(form)
    else:
        userId = userId["_id"]
    print(userId)

    # Uploading the scan image to firebase
    reportId = ''.join(random.choices(
        string.ascii_uppercase + string.ascii_lowercase + string.digits, k=17))
    path = "CTScans/"+reportId+"kc"
    print(path)
    storage.storage.child(path).put(file)
    url = storage.storage.child(path).get_url(None)
    print(url)

    # Image preprocessing
    np_image = Image.open(file)
    np_image = np.array(np_image).astype('float32')/255
    np_image = transform.rescale(image=np_image, scale=1/255)
    np_image = transform.rotate(image=np_image, angle=50)
    np_image = transform.resize(np_image, (75, 75, 3))
    resnet_np_image = transform.resize(np_image, (200, 200, 3))
    np_image = np.expand_dims(np_image, axis=0)

    # Calling the model functions

    threading.Thread(target=resnetModel(
        np_image=np.expand_dims(resnet_np_image, axis=0))).start()
    threading.Thread(target=xceptionModel(np_image)).start()
    threading.Thread(target=inceptionModel(np_image)).start()

    # Printing the model Results
    print(modelResults)

    report = {
        "report_id": reportId,
        "user_id": userId,
        "datetime": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "scan_image": url,
        "prediction": str(str(modelResults["resnet"]["prediction"])),
        "class": modelResults["resnet"]["class"]
    }
    db.reports.insert_one(report)

    db.users.update_one({"_id": userId}, {"$push": {"reports": reportId}})

    db.modelcount.update_one({"name": "model_count"}, {"$push": {
                             "resnet": str(modelResults["resnet"]["prediction"]), "inception": str(modelResults["inception"]["prediction"]), "xception": str(modelResults["xception"]["prediction"])}, "$inc": {"cyst_count": 1, "total_prediction_count": 1} if modelResults["resnet"]["class"] == "Cyst" else {"normal_count": 1, "total_prediction_count": 1}}, upsert=False)
    admin = False
    if "email" in session:
        admin = {"email": session["email"], "name": session["name"]}
    return render_template("predict.html", report=report, admin=admin)


@app.errorhandler(404)
def error(e):
    return redirect(url_for("dashboard"))


# app
if __name__ == "__main__":
    app.run(port=80, debug=True)
