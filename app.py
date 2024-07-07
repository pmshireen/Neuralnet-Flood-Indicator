
import json
import requests
from flask import Flask, request, render_template, jsonify, redirect, url_for
from pymongo import MongoClient
from selenium import webdriver
import time
import base64
import numpy as np
from keras.preprocessing import image

app = Flask(__name__)

DOCKER_CONTAINER_URL = 'http://localhost:5500/upload'
current_location = None
try:
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Flood-app']  # Replace 'Flood-app' with your database name
    collection = db['Users']  # Replace 'Users' with your collection name
    print("Successfully connected to MongoDB!");
except Exception as e:
    print("Error connecting to MongoDB:", e)

@app.route("/")
def initial_page():
    return redirect(url_for("home"))

@app.route("/home")
def home():
    return render_template("home.html")
#
# @app.route("/login", methods=["POST"])
# def login():
#     username = request.form.get("username")
#     password = request.form.get("password")
#     valid = False
#     # Query the database for the provided username
#     documents = collection.find();
#     users = {}
#     for record in documents:
#         # if user == username and password
#         users = record['Users']
#     for item in users:
#         if item['username'] == username and item['password'] == password:
#             valid = True
#         # print(item)
#         # print(item['username'])
#     if valid:
#         # Redirect to the map page upon successful login
#         return redirect(url_for("map"))
#     else:
#         # Redirect back to the home page upon unsuccessful login
#         return redirect(url_for("login", error="Invalid username or password."))

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    # Check if the username and password match the predefined values
    if username == "murshi" and password == "123":
        # Redirect to the map page upon successful login
        return redirect(url_for("map"))
    else:
        # Redirect back to the login page upon unsuccessful login
        return redirect(url_for("login", error="Invalid username or password."))

@app.route("/login")
def login_page():
    error = request.args.get("error")
    return render_template("login.html", error=error)


@app.route("/signup", methods=["POST"])
def signup():
    # Get username and password from the signup form
    username = request.form.get("username")
    password = request.form.get("password")

    # Check if the username already exists in the database
    existing_user = collection.find_one({"username": username})

    if existing_user:
        # If username already exists, redirect back to signup page with an error
        return redirect(url_for("signup_page", error="Username already exists. Please choose another one."))

    else:
        # If username doesn't exist, insert the new user into the Users collection
        new_user = {"username": username, "password": password}
        collection.insert_one(new_user)
        # Redirect to login page after successful signup
        return redirect(url_for("login_page"))

@app.route("/signup")
def signup_page():
    error = request.args.get("error")
    return render_template("signup.html", error=error)

@app.route("/index")
def map():
    return render_template("index.html")

# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    global current_location  # Declare current_location as global
    location = request.form['location']
    current_location = location


    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome()

    # Open Google My Maps URL with the search query
    driver.get('https://www.google.com/maps/search/' + location)

    # Wait for the page to load
    time.sleep(10)  # Adjust the wait time as needed

    # Save a screenshot of the page
    screenshot_path = 'screenshot.png'
    driver.save_screenshot(screenshot_path)

    # Close the browser
    driver.quit()

    # Preprocess the screenshot and send it to the Docker container for prediction
    return predict(screenshot_path)
@app.route('/predict', methods=['POST'])
def predict(image_path=None):
    global current_location
    if image_path is None:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'})
        image = request.files['image']
        image_path = 'uploaded_image.png'
        image.save(image_path)

    # Preprocess the image
    img_array = preprocess_image(image_path)
    # Convert the image to base64 format
    with open(image_path, 'rb') as img_file:
        encoded_image = base64.b64encode(img_file.read()).decode('utf-8')

    # Send the image to the Docker container for processing
    files = {'image': open(image_path, 'rb')}
    response = requests.post(DOCKER_CONTAINER_URL, files=files)
    prediction = response.text

    # Parse the prediction result to extract the prediction value
    prediction_value = extract_prediction(prediction)
    rainfall_result = rainfall()
    temperature = rainfall_result['temperature']
    humidity = rainfall_result['humidity']
    wind_speed = rainfall_result['wind_speed']
    wind_degree = rainfall_result['wind_degree']
    pred_level = rainfall_result['pre_level']
    print(rainfall_result)
    if((prediction_value =="flood" or " Flood") and (rainfall_result == "flood")):
         predictions = "flood"
    else:
        predictions = "no flood"
    # Pass the screenshot data and prediction result to the result.html template
    return render_template('result.html', screenshot_data=encoded_image,location=current_location, prediction=predictions,
                           temperature=temperature,
                           humidity=humidity,
                           wind_speed=wind_speed,
                           wind_degree=wind_degree,
                           pred_level = pred_level,
                           )


def extract_prediction(prediction):
    try:
        # Parse the prediction string as a JSON object
        prediction_json = json.loads(prediction)
        # Extract the prediction value from the JSON object
        prediction_value = prediction_json['prediction']
        return prediction_value
    except (json.JSONDecodeError, KeyError):
        # Handle the case where the prediction string cannot be parsed as JSON or does not have the expected format
        return 'Prediction unavailable'

def rainfall():
    global current_location
    apiKey = "e9b4d3c0d4d088c522e59a83d2e3018b"
    baseURL ="https://api.openweathermap.org/data/2.5/weather?q="
    completeURL = baseURL + current_location + "&appid=" + apiKey
    response = requests.get(completeURL)
    data = response.json()
    temp = data["main"]["temp"]
    hum = data["main"]["humidity"]
    rainfall = data["wind"]["speed"]
    river = data["wind"]["deg"]
    if((temp <= 303 and hum >= 50) and ( 2.57 >= rainfall <= 5.57 and river >= 50)):
        result = "flood"
    else:
        result = "no flood"
    if(result == "flood" and rainfall >= 4.57):
        pre_level = "90%"
    elif(result == "flood" and rainfall <= 4.57):
        pre_level ="75%"
    else:
        pre_level ="10%"


    return { 'result': result,
        'temperature': temp,
        'humidity': hum,
        'wind_speed': rainfall,
        'wind_degree': river,
             'pre_level': pre_level}


def preprocess_image(image_path):
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = img_array / 255.0  # Normalization
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

if __name__ == '__main__':
    app.run(debug=True)