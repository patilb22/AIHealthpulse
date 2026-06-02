"""Generate a reproducible synthetic health tracker dataset.

Run:
    python data/generate_data.py

Outputs:
    data/health_tracker_data.csv
"""

import csv
import os
from datetime import date, timedelta

import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "health_tracker_data.csv")

RNG = np.random.default_rng(42)

PATIENTS = [
    ("Avery Morgan", "F", 29, "Seattle", "WA"),
    ("Brianna Lee", "F", 33, "Portland", "OR"),
    ("Caroline Davis", "F", 38, "San Francisco", "CA"),
    ("Danielle Nguyen", "F", 41, "Vancouver", "WA"),
    ("Elena Patel", "F", 46, "Eugene", "OR"),
    ("Fiona Brooks", "F", 51, "Boise", "ID"),
    ("Grace Thompson", "F", 54, "Bend", "OR"),
    ("Hannah Rivera", "F", 58, "Tacoma", "WA"),
    ("Isabella Chen", "F", 61, "Spokane", "WA"),
    ("Jackson Carter", "M", 26, "Seattle", "WA"),
    ("Liam Anderson", "M", 35, "Portland", "OR"),
    ("Mason Wright", "M", 44, "Salem", "OR"),
    ("Noah Harris", "M", 49, "Boise", "ID"),
    ("Owen Clark", "M", 57, "Tacoma", "WA"),
    ("Wyatt Kelly", "M", 68, "Honolulu", "HI"),
]

CONDITIONS = [
    "Hypertension",
    "Type 2 Diabetes",
    "Asthma",
    "Arthritis",
    "Migraine",
    "Anxiety",
    "Depression",
    "GERD",
    "None",
    "None",
]

SYMPTOMS = [
    "Headache",
    "Fatigue",
    "Dizziness",
    "Chest Pain",
    "Shortness of Breath",
    "Joint Pain",
    "Back Pain",
    "Nausea",
    "Insomnia",
    "Anxiety",
    "None",
]

SLEEP_QUALITY = ["Excellent", "Good", "Fair", "Poor", "Very Poor"]
ACTIVITY_LEVEL = ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"]
MOODS = ["Happy", "Calm", "Tired", "Stressed", "Neutral"]
MEDICATION_TAKEN = ["Yes", "Yes", "Yes", "No"]

FIELDNAMES = [
    "patient_id",
    "patient_name",
    "gender",
    "age",
    "city",
    "state",
    "date",
    "primary_condition",
    "systolic_bp",
    "diastolic_bp",
    "blood_glucose_mgdl",
    "heart_rate_bpm",
    "spo2_percent",
    "body_temp_celsius",
    "weight_kg",
    "bmi",
    "steps_count",
    "calories_burned",
    "water_intake_liters",
    "sleep_hours",
    "sleep_quality",
    "activity_level",
    "mood",
    "symptom",
    "symptom_severity",
    "medication_taken",
]


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def generate_patient_rows(patient_id, name, gender, age, city, state, condition):
    rows = []
    start = date(2024, 1, 1)

    for day_offset in range(365):
        current_date = start + timedelta(days=day_offset)

        if condition == "Hypertension":
            systolic = RNG.normal(145, 15)
            diastolic = RNG.normal(92, 10)
        else:
            systolic = RNG.normal(118, 10)
            diastolic = RNG.normal(76, 8)

        if condition == "Type 2 Diabetes":
            glucose = RNG.normal(145, 30)
        else:
            glucose = RNG.normal(98, 12)

        systolic = clamp(round(systolic, 1), 95, 205)
        diastolic = clamp(round(diastolic, 1), 60, 130)
        glucose = clamp(round(glucose, 1), 60, 320)

        heart_rate = clamp(round(RNG.normal(70 if age < 50 else 74, 9), 1), 50, 115)
        spo2 = clamp(round(RNG.normal(97.5, 1.0), 1), 91, 100)
        temp = clamp(round(RNG.normal(36.6, 0.3), 1), 35.5, 38.5)
        weight = clamp(round(55 + (age - 25) * 0.5 + (0 if gender == "F" else 8) + RNG.normal(0, 3), 1), 50, 115)
        height_m = 1.62 if gender == "F" else 1.75
        bmi = clamp(round(weight / (height_m**2), 1), 18.0, 40.0)
        steps = int(clamp(RNG.normal(7200, 2600), 500, 16000))
        calories = int(clamp(RNG.normal(2100, 450), 1400, 3300))
        water = round(clamp(RNG.normal(2.2, 0.5), 1.0, 4.5), 1)
        sleep_hours = round(clamp(RNG.normal(7.2, 1.1), 4.0, 10.0), 1)
        sleep_quality = str(RNG.choice(SLEEP_QUALITY))
        activity = str(RNG.choice(ACTIVITY_LEVEL))
        mood = str(RNG.choice(MOODS))
        symptom = str(RNG.choice(SYMPTOMS))
        symptom_severity = 0 if symptom == "None" else int(RNG.integers(1, 11))
        medication_taken = str(RNG.choice(MEDICATION_TAKEN))

        rows.append({
            "patient_id": f"PT{patient_id:03d}",
            "patient_name": name,
            "gender": gender,
            "age": age,
            "city": city,
            "state": state,
            "date": current_date.isoformat(),
            "primary_condition": condition,
            "systolic_bp": systolic,
            "diastolic_bp": diastolic,
            "blood_glucose_mgdl": glucose,
            "heart_rate_bpm": heart_rate,
            "spo2_percent": spo2,
            "body_temp_celsius": temp,
            "weight_kg": weight,
            "bmi": bmi,
            "steps_count": steps,
            "calories_burned": calories,
            "water_intake_liters": water,
            "sleep_hours": sleep_hours,
            "sleep_quality": sleep_quality,
            "activity_level": activity,
            "mood": mood,
            "symptom": symptom,
            "symptom_severity": symptom_severity,
            "medication_taken": medication_taken,
        })

    return rows


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    condition_map = [
        "Hypertension",
        "Type 2 Diabetes",
        "Hypertension",
        "Type 2 Diabetes",
        "Hypertension",
        "Type 2 Diabetes",
        "Asthma",
        "Arthritis",
        "Migraine",
        "Anxiety",
        "Depression",
        "GERD",
        "None",
        "None",
        "None",
    ]

    all_rows = []
    for idx, patient in enumerate(PATIENTS, start=1):
        name, gender, age, city, state = patient
        condition = condition_map[idx - 1]
        all_rows.extend(generate_patient_rows(idx, name, gender, age, city, state, condition))

    assert len(all_rows) == 15 * 365, f"Expected 5475 rows, got {len(all_rows)}"

    all_rows.sort(key=lambda row: (row["patient_id"], row["date"]))

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Generated {len(all_rows)} rows for 15 patients and saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
