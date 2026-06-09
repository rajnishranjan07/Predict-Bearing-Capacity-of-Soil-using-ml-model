from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import pandas as pd
import joblib
import os

# ---------------------------------
# Flask App Configuration
# ---------------------------------
app = Flask(__name__)
app.secret_key = "soil_bearing_capacity_secret_key"

DB_NAME = "bearing_capacity.db"

# ---------------------------------
# Load ML Model & Encoders
# ---------------------------------
model = joblib.load("bearing_capacity_model.pkl")
soil_encoder = joblib.load("soil_encoder.pkl")
footing_encoder = joblib.load("footing_encoder.pkl")

# ---------------------------------
# Database Connection
# ---------------------------------
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------------------
# Initialize Database
# ---------------------------------
def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # Predictions table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        soil TEXT,
        footing TEXT,
        cohesion REAL,
        phi REAL,
        gamma REAL,
        depth REAL,
        width REAL,
        fos REAL,
        ultimate REAL,
        safe REAL
    )
    """)

    conn.commit()
    conn.close()
    

# ---------------------------------
# Home
# ---------------------------------
@app.route("/")
def home():
    return redirect(url_for("login"))
   
# ---------------------------------
# Register
# ---------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists"

        conn.close()
        return redirect(url_for("login"))

    return render_template("register.html")

# ---------------------------------
# Login
# ---------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect(url_for("predict"))
        else:
            return "Invalid username or password"

    return render_template("login.html")

# ---------------------------------
# Prediction Page
# ---------------------------------
@app.route("/predict", methods=["GET", "POST"])
def predict():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        soil = request.form["soil"]
        footing = request.form["footing"]
        c = float(request.form["c"])
        phi = float(request.form["phi"])
        gamma = float(request.form["gamma"])
        depth = float(request.form["depth"])
        width = float(request.form["width"])
        fos = float(request.form["fos"])

        # Encode categorical values
        soil_enc = soil_encoder.transform([soil])[0]
        footing_enc = footing_encoder.transform([footing])[0]

        # Prepare input
        X = pd.DataFrame([[
            soil_enc,
            footing_enc,
            c,
            phi,
            gamma,
            depth,
            width,
            fos
        ]], columns=[
            "Soil_Type",
            "Footing_Type",
            "Cohesion_c",
            "Angle_of_Friction_phi",
            "Unit_Weight_gamma",
            "Depth_of_Foundation_Df",
            "Width_B",
            "Factor_of_Safety"
        ])

        # Prediction
        ultimate, safe = model.predict(X)[0]
        ultimate = round(ultimate, 2)
        safe = round(safe, 2)

        # Save to database
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO predictions (
            username, soil, footing, cohesion, phi,
            gamma, depth, width, fos, ultimate, safe
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user"], soil, footing, c, phi,
            gamma, depth, width, fos, ultimate, safe
        ))
        conn.commit()
        conn.close()

        return render_template(
            "result.html",
            ultimate=ultimate,
            safe=safe
        )

    return render_template("predict.html")



# ---------------------------------
# Logout
# ---------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
    

# ---------------------------------
# Run App
# ---------------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)