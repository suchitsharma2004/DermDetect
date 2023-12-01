from os import name
from keras.models import load_model
from flask import Flask, redirect, render_template, request, session
from keras.preprocessing import image
import numpy as np
from PIL import Image
import pyrebase

config = {
    "apiKey": "AIzaSyAN0gSFId7s88DipRUQZRlitLCk34GtIBU",
    "authDomain": "derm-detect.firebaseapp.com",
    "projectId": "derm-detect",
    "storageBucket": "derm-detect.appspot.com",
    "messagingSenderId": "450277166658",
    "appId": "1:450277166658:web:1aa928fd4fb0ced364a7db",
    "measurementId": "G-DMPB1BTBDK",
    "databaseURL": "https://derm-detect-default-rtdb.firebaseio.com/",
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

# Creating the app
app = Flask(__name__, static_url_path="/static")
app.secret_key = "super secret key"

# Loading the model
model = load_model("final_skin_disease_model.h5")


# Define the route for the home page
@app.route("/")
def home():
    # Add logic here to render the home page HTML template
    return render_template("index.html", session=session)


@app.route("/predict", methods=["POST"])
def predict():
    # Get the image from the request
    file = request.files["file"]

    # Open the image using PIL
    test_image = None
    try:
        test_image = Image.open(file)
    except Exception as e:
        return render_template("index.html", error="Please choose an image file first")

    # Load and preprocess the image
    test_image = test_image.resize((224, 224))
    test_image = image.img_to_array(test_image)
    test_image /= 255.0
    test_image = np.expand_dims(test_image, axis=0)
    test_image = test_image[:, :, :, :3]

    # Make predictions using the loaded model
    predictions = model.predict(test_image)
    predicted_class_index = np.argmax(predictions)

    class_labels = ["Enfeksiyonel", "Ekzama", "Acne", "Pigment", "Benign", "Malign"]
    predicted_class_label = class_labels[predicted_class_index]

    # Set probability threshold
    threshold = 0.6

    # Check if probability is above threshold
    if predictions[0, predicted_class_index] < threshold:
        return render_template(
            "error.html",
            error="Inconclusive result. Please consult a healthcare professional for an accurate diagnosis",
        )

    # Render the results page with the prediction
    return render_template("results.html", prediction=predicted_class_label)


def allowed_file(filename):
    # Add logic to check if the filename has an allowed extension (e.g., .jpg, .jpeg, .png)
    allowed_extensions = {"jpg", "jpeg", "png"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user") != None:
        return render_template("index.html")

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session.update({"user": user})
            return redirect("/")
        except Exception as e:
            return render_template("login.html", error=e.args[1].split(":")[3])

    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("user", None)
    return redirect("/")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        try:
            auth.create_user_with_email_and_password(email, password)
            user = auth.sign_in_with_email_and_password(email, password)
            session.update({"user": user})
            auth.update_profile(id_token=user["idToken"], display_name=name)
            return redirect("/")
        except Exception as e:
            return render_template("signup.html", error=e.args[1].split(":")[3])

    return render_template("signup.html")


@app.route("/appointment", methods=["GET", "POST"])
def appointment():
    doctors = [
        {
            "name": "Dr. John Doe",
            "speciality": "Dermatologist",
            "clinic": "Dermatology Clinic",
            "location": "New York",
            "calendly_link": "https://calendly.com/johndoe",
            "image": "doctor-m-1.jpg",
        },
        {
            "name": "Dr. Sarah Smith",
            "speciality": "Cardiologist",
            "clinic": "Heart Care Center",
            "location": "Los Angeles",
            "calendly_link": "https://calendly.com/sarahsmith",
            "image": "doctor-w-1.jpg",
        },
        {
            "name": "Dr. Michael Johnson",
            "speciality": "Orthopedic Surgeon",
            "clinic": "Ortho Wellness Center",
            "location": "Chicago",
            "calendly_link": "https://calendly.com/michaeljohnson",
            "image": "doctor-m-2.jpg",
        },
        {
            "name": "Dr. Emily Brown",
            "speciality": "Pediatrician",
            "clinic": "Kids Care Clinic",
            "location": "San Francisco",
            "calendly_link": "https://calendly.com/emilybrown",
            "image": "doctor-w-2.jpg",
        },
        {
            "name": "Dr. Robert Taylor",
            "speciality": "Oncologist",
            "clinic": "Cancer Care Center",
            "location": "Houston",
            "calendly_link": "https://calendly.com/roberttaylor",
            "image": "doctor-m-3.jpg",
        },
        {
            "name": "Dr. Jessica Rodriguez",
            "speciality": "Neurologist",
            "clinic": "Brain Health Center",
            "location": "Miami",
            "calendly_link": "https://calendly.com/jessicarodriguez",
            "image": "doctor-w-3.jpg",
        },
    ]

    return render_template("appointment.html", session=session, doctors=doctors)


# Run the application
if __name__ == "__main__":
    app.run(debug=True)
