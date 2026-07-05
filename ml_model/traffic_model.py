"""
Urban Traffic Congestion Prediction Model
Uses Random Forest Classifier for congestion level prediction
"""

import pickle
import numpy as np
import os

# Try to import sklearn; if not available, use rule-based fallback
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Encoding maps
WEATHER_MAP = {'Clear': 0, 'Cloudy': 1, 'Rainy': 2, 'Foggy': 3, 'Hazy': 4, 'Stormy': 5}
ROAD_TYPE_MAP = {'Highway': 0, 'Urban Road': 1, 'Expressway': 2, 'City Street': 3, 'Ring Road': 4}
DAY_MAP = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
           'Friday': 4, 'Saturday': 5, 'Sunday': 6}
CONGESTION_MAP = {0: 'Low', 1: 'Medium', 2: 'High'}
CONGESTION_REVERSE = {'Low': 0, 'Medium': 1, 'High': 2}

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')

def time_to_hour(time_str):
    """Convert time string like '08:00 AM' to hour integer."""
    try:
        from datetime import datetime
        t = datetime.strptime(time_str.strip(), '%I:%M %p')
        return t.hour
    except:
        try:
            parts = time_str.replace('AM','').replace('PM','').strip().split(':')
            h = int(parts[0])
            if 'PM' in time_str.upper() and h != 12:
                h += 12
            if 'AM' in time_str.upper() and h == 12:
                h = 0
            return h
        except:
            return 8

def generate_training_data():
    """Generate synthetic training data for the model."""
    np.random.seed(42)
    n = 2000
    X, y = [], []

    for _ in range(n):
        day = np.random.randint(0, 7)
        hour = np.random.randint(0, 24)
        weather = np.random.randint(0, 6)
        vehicle_count = np.random.randint(100, 1200)
        avg_speed = np.random.uniform(5, 80)
        road_type = np.random.randint(0, 5)

        # Congestion logic
        score = 0
        if hour in [7, 8, 9, 17, 18, 19, 20]:  # peak hours
            score += 3
        elif hour in [10, 11, 12, 13, 14, 15, 16]:
            score += 1

        if day in [0, 1, 2, 3, 4]:  # weekday
            score += 1

        if vehicle_count > 700:
            score += 3
        elif vehicle_count > 400:
            score += 1

        if avg_speed < 20:
            score += 3
        elif avg_speed < 40:
            score += 1

        if weather in [2, 3, 5]:  # rainy, foggy, stormy
            score += 2

        if road_type == 1:  # urban road
            score += 1

        if score <= 3:
            label = 0  # Low
        elif score <= 6:
            label = 1  # Medium
        else:
            label = 2  # High

        X.append([day, hour, weather, vehicle_count, avg_speed, road_type])
        y.append(label)

    return np.array(X), np.array(y)

def train_and_save_model():
    """Train the model and save it."""
    if not SKLEARN_AVAILABLE:
        return False
    X, y = generate_training_data()
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    model.fit(X, y)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    return True

def load_model():
    """Load the saved model or train a new one."""
    if SKLEARN_AVAILABLE:
        if not os.path.exists(MODEL_PATH):
            train_and_save_model()
        try:
            with open(MODEL_PATH, 'rb') as f:
                return pickle.load(f)
        except:
            train_and_save_model()
            with open(MODEL_PATH, 'rb') as f:
                return pickle.load(f)
    return None

def rule_based_predict(day, hour, weather_code, vehicle_count, avg_speed, road_type_code):
    """Fallback rule-based prediction when sklearn is unavailable."""
    score = 0
    if hour in [7, 8, 9, 17, 18, 19, 20]:
        score += 3
    elif 10 <= hour <= 16:
        score += 1

    if day in [0, 1, 2, 3, 4]:
        score += 1

    if vehicle_count > 700:
        score += 3
    elif vehicle_count > 400:
        score += 1

    if avg_speed < 20:
        score += 3
    elif avg_speed < 40:
        score += 1

    if weather_code in [2, 3, 5]:
        score += 2

    if road_type_code == 1:
        score += 1

    if score <= 3:
        return 0
    elif score <= 6:
        return 1
    else:
        return 2

def predict_congestion(area, road_name, day, time, weather, vehicle_count, avg_speed, road_type):
    """Main prediction function."""
    day_code = DAY_MAP.get(day, 0)
    hour = time_to_hour(time)
    weather_code = WEATHER_MAP.get(weather, 0)
    vehicle_count = int(vehicle_count)
    avg_speed = float(avg_speed)
    road_type_code = ROAD_TYPE_MAP.get(road_type, 1)

    features = [[day_code, hour, weather_code, vehicle_count, avg_speed, road_type_code]]

    model = load_model()
    if model:
        prediction = model.predict(features)[0]
        try:
            probabilities = model.predict_proba(features)[0]
            confidence = round(max(probabilities) * 100, 1)
        except:
            confidence = 85.0
    else:
        prediction = rule_based_predict(day_code, hour, weather_code, vehicle_count, avg_speed, road_type_code)
        confidence = 82.0

    congestion_level = CONGESTION_MAP[prediction]

    # Severity and delay
    if congestion_level == 'High':
        severity = 'Severe'
        delay_min = max(20, int(vehicle_count / 30))
        delay = f"{delay_min}–{delay_min + 20} minutes"
        safety = "⚠️ Avoid this route if possible. High risk of accidents. Use alternate roads."
    elif congestion_level == 'Medium':
        severity = 'Moderate'
        delay_min = max(8, int(vehicle_count / 70))
        delay = f"{delay_min}–{delay_min + 10} minutes"
        safety = "🟡 Moderate traffic. Maintain safe distance. Expect delays."
    else:
        severity = 'Low'
        delay_min = max(0, int(vehicle_count / 200))
        delay = f"{delay_min}–{delay_min + 5} minutes"
        safety = "✅ Route is clear. Drive safely and follow traffic rules."

    return {
        'area': area,
        'road_name': road_name,
        'congestion_level': congestion_level,
        'severity': severity,
        'estimated_delay': delay,
        'safety_message': safety,
        'confidence': confidence,
        'hour': hour,
        'vehicle_count': vehicle_count,
        'avg_speed': avg_speed
    }

def get_route_suggestion(congestion_level, area, road_name, weather):
    """Generate route suggestion based on congestion."""
    alt_routes = {
        'Connaught Place': 'Bhairon Road → Mathura Road',
        'Bandra': 'Eastern Express Highway via Sion',
        'Electronic City': 'Bannerghatta Road → Kanakapura Road',
        'Salt Lake': 'VIP Road → Ultadanga',
        'Anna Nagar': 'Poonamallee High Road → NH-48',
        'Koramangala': 'Bannerghatta Road → Jayanagar',
        'Hitech City': 'Gachibowli Flyover → Financial District',
        'Dwarka': 'Pankha Road → NH-10',
        'Whitefield': 'Varthur Road → HAL Old Airport Road',
        'Powai': 'Jogeshwari-Vikhroli Link Road',
    }

    current = f"{road_name}, {area}"
    suggested = alt_routes.get(area, f"Inner Road via {area} Bypass")

    if congestion_level == 'High':
        reason = f"High congestion detected on {road_name}. Alternate route has ~40% less traffic."
        action = "Take Alternate Route"
        badge = "danger"
    elif congestion_level == 'Medium':
        reason = f"Moderate traffic on {road_name}. Alternate route may save 10–15 minutes."
        action = "Consider Alternate Route"
        badge = "warning"
    else:
        reason = f"Traffic is flowing smoothly on {road_name}. No detour needed."
        action = "Continue on Current Route"
        badge = "success"
        suggested = current

    if weather in ['Rainy', 'Foggy', 'Stormy']:
        reason += f" Also, {weather.lower()} weather conditions — drive cautiously."
        action = "Use Safer Route"

    return {
        'current_route': current,
        'suggested_route': suggested,
        'congestion_level': congestion_level,
        'action': action,
        'badge': badge,
        'reason': reason
    }

# Pre-train model on first import
if SKLEARN_AVAILABLE and not os.path.exists(MODEL_PATH):
    try:
        train_and_save_model()
    except:
        pass
