"""
Generate fake medical health tracker dataset for demo purposes.
Run: python generate_data.py
"""
import csv
import random
import datetime

random.seed(42)

PATIENTS = [
    ("Alice Chen", "F", 34, "Seattle, WA"),
    ("Bob Martinez", "M", 52, "Portland, OR"),
    ("Carol White", "F", 28, "San Francisco, CA"),
    ("David Kim", "M", 45, "Los Angeles, CA"),
    ("Eva Rodriguez", "F", 61, "Phoenix, AZ"),
    ("Frank Liu", "M", 39, "Denver, CO"),
    ("Grace Thompson", "F", 47, "Chicago, IL"),
    ("Henry Patel", "M", 55, "New York, NY"),
    ("Iris Johnson", "F", 31, "Boston, MA"),
    ("James Wilson", "M", 68, "Miami, FL"),
    ("Karen Davis", "F", 43, "Atlanta, GA"),
    ("Liam Brown", "M", 26, "Austin, TX"),
    ("Maria Garcia", "F", 57, "Houston, TX"),
    ("Noah Anderson", "M", 49, "Dallas, TX"),
    ("Olivia Taylor", "F", 35, "Minneapolis, MN"),
]

CONDITIONS = [
    "Hypertension", "Type 2 Diabetes", "Asthma", "Arthritis",
    "Migraine", "Anxiety", "Depression", "GERD", "None", "None",
]

SYMPTOMS = [
    "Headache", "Fatigue", "Dizziness", "Chest Pain", "Shortness of Breath",
    "Joint Pain", "Back Pain", "Nausea", "Insomnia", "Anxiety",
    "Muscle Weakness", "Blurred Vision", "Heart Palpitations", "None",
]

MEDICATIONS = [
    "Lisinopril", "Metformin", "Albuterol", "Ibuprofen", "Sumatriptan",
    "Sertraline", "Omeprazole", "None", "Aspirin", "Atorvastatin",
]

MOOD = ["Excellent", "Good", "Fair", "Poor", "Very Poor"]
SLEEP_QUALITY = ["Excellent", "Good", "Fair", "Poor", "Very Poor"]
ACTIVITY = ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"]

def generate_patient_data(patient_id, name, gender, age, location):
    rows = []
    start_date = datetime.date(2024, 1, 1)
    condition = random.choice(CONDITIONS)

    for day_offset in range(365):
        date = start_date + datetime.timedelta(days=day_offset)

        # Health metrics with realistic ranges
        if condition == "Hypertension":
            systolic = random.gauss(145, 15)
            diastolic = random.gauss(92, 10)
        else:
            systolic = random.gauss(118, 12)
            diastolic = random.gauss(76, 8)

        systolic = max(90, min(200, systolic))
        diastolic = max(60, min(120, diastolic))

        if condition == "Type 2 Diabetes":
            glucose = random.gauss(145, 30)
        else:
            glucose = random.gauss(95, 12)
        glucose = max(60, min(300, glucose))

        if age > 50:
            heart_rate = random.gauss(72, 12)
        else:
            heart_rate = random.gauss(68, 10)
        heart_rate = max(50, min(120, heart_rate))

        weight_base = 60 + (age - 25) * 0.3 + (0 if gender == "F" else 10)
        weight = weight_base + random.gauss(0, 1.5)

        spo2 = random.gauss(97.5, 1.2)
        spo2 = max(90, min(100, spo2))

        temp = random.gauss(36.6, 0.3)
        temp = max(35.5, min(40.0, temp))

        steps = max(0, int(random.gauss(7500, 3000)))
        calories = max(1200, int(random.gauss(2000, 400)))
        water_intake = round(max(0.5, random.gauss(2.2, 0.6)), 1)
        sleep_hours = round(max(3, min(12, random.gauss(7.0, 1.2))), 1)

        symptom = random.choice(SYMPTOMS)
        symptom_severity = random.randint(1, 10) if symptom != "None" else 0
        mood = random.choice(MOOD)
        sleep_quality = random.choice(SLEEP_QUALITY)
        activity_level = random.choice(ACTIVITY)
        medication = random.choice(MEDICATIONS)
        medication_taken = random.choice(["Yes", "Yes", "Yes", "No"])

        bmi = weight / ((random.uniform(1.55, 1.85)) ** 2)

        rows.append({
            "patient_id": f"PT{patient_id:03d}",
            "name": name,
            "gender": gender,
            "age": age,
            "location": location,
            "date": date.isoformat(),
            "primary_condition": condition,
            "systolic_bp": round(systolic, 1),
            "diastolic_bp": round(diastolic, 1),
            "heart_rate_bpm": round(heart_rate, 1),
            "blood_glucose_mgdl": round(glucose, 1),
            "spo2_percent": round(spo2, 1),
            "body_temp_celsius": round(temp, 1),
            "weight_kg": round(weight, 1),
            "bmi": round(bmi, 1),
            "steps_count": steps,
            "calories_burned": calories,
            "water_intake_liters": water_intake,
            "sleep_hours": sleep_hours,
            "sleep_quality": sleep_quality,
            "activity_level": activity_level,
            "mood": mood,
            "symptom": symptom,
            "symptom_severity": symptom_severity,
            "medication": medication,
            "medication_taken": medication_taken,
        })
    return rows


def main():
    all_rows = []
    for i, (name, gender, age, location) in enumerate(PATIENTS, 1):
        all_rows.extend(generate_patient_data(i, name, gender, age, location))

    # Sort by date
    all_rows.sort(key=lambda r: (r["date"], r["patient_id"]))

    fieldnames = list(all_rows[0].keys())
    with open("health_tracker_data.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Generated {len(all_rows)} records for {len(PATIENTS)} patients across 365 days.")
    print("File saved: health_tracker_data.csv")


if __name__ == "__main__":
    main()
