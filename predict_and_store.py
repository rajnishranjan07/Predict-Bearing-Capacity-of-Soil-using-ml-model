import sqlite3
import joblib
import pandas as pd

# --------------------------------------
# Load Model & Encoders
# --------------------------------------
model = joblib.load("bearing_capacity_model.pkl")
le_soil = joblib.load("soil_encoder.pkl")
le_footing = joblib.load("footing_encoder.pkl")

# --------------------------------------
# User Input (Example)
# --------------------------------------
soil_type = "Alluvial"
footing_type = "Combined"
c = 20.1
phi = 20
gamma = 17.86
Df = 0.97
B=1.12
FOS = 3

# --------------------------------------
# Encode Inputs
# --------------------------------------
soil_encoded = le_soil.transform([soil_type])[0]
footing_encoded = le_footing.transform([footing_type])[0]

X_input = pd.DataFrame([[
    soil_encoded,
    footing_encoded,
    c,
    phi,
    gamma,
    Df,
    B,
    FOS
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

# --------------------------------------
# Prediction
# --------------------------------------
ultimate, safe = model.predict(X_input)[0]

print("Ultimate Bearing Capacity:", round(ultimate, 2))
print("Safe Bearing Capacity:", round(safe, 2))

# --------------------------------------
# Store in SQLite
# --------------------------------------
conn = sqlite3.connect("bearing_capacity.db")
cursor = conn.cursor()

cursor.execute("""
INSERT INTO predictions (
    soil_type, footing_type, cohesion, phi, gamma, depth, width, fos,
    ultimate_capacity, safe_capacity
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    soil_type, footing_type, c, phi, gamma, Df, B, FOS,
    round(ultimate, 2), round(safe, 2)
))

conn.commit()
conn.close()

print("Prediction stored in database!")