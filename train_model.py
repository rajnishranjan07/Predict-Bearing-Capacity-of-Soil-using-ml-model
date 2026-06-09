import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score
import joblib

# --------------------------------------
# Load Dataset
# --------------------------------------
df = pd.read_csv("dataset/soil_bearing_capacity_dataset.csv")

# --------------------------------------
# Encode Categorical Columns
# --------------------------------------
le_soil = LabelEncoder()
le_footing = LabelEncoder()

df["Soil_Type"] = le_soil.fit_transform(df["Soil_Type"])
df["Footing_Type"] = le_footing.fit_transform(df["Footing_Type"])

# --------------------------------------
# Input & Output
# --------------------------------------
X = df[
    [
        "Soil_Type",
        "Footing_Type",
        "Cohesion_c",
        "Angle_of_Friction_phi",
        "Unit_Weight_gamma",
        "Depth_of_Foundation_Df",
        "Width_B",
        "Factor_of_Safety"
    ]
]

y = df[
    [
        "Ultimate_Bearing_Capacity_qu",
        "Safe_Bearing_Capacity_qs"
    ]
]

# --------------------------------------
# Train Test Split
# --------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# --------------------------------------
# Model Training
# --------------------------------------
model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

# --------------------------------------
# Accuracy
# --------------------------------------
y_pred = model.predict(X_test)
accuracy = r2_score(y_test, y_pred)

print("Model Accuracy (R² Score):", accuracy)

# --------------------------------------
# Save Model & Encoders
# --------------------------------------
joblib.dump(model, "bearing_capacity_model.pkl")
joblib.dump(le_soil, "soil_encoder.pkl")
joblib.dump(le_footing, "footing_encoder.pkl")

print("Model and encoders saved successfully!")