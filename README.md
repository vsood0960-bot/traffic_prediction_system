# 🚦 Urban Traffic Intelligence & Congestion Prediction System
### MCA Final Year Project | Python Flask + MySQL + ML + Power BI

---

## 📁 Project Structure

```
urban_traffic_system/
│
├── app.py                        ← Flask backend (main entry point)
├── database.sql                  ← MySQL database setup script
├── requirements.txt              ← Python dependencies
│
├── ml_model/
│   ├── __init__.py
│   └── traffic_model.py          ← Random Forest ML prediction model
│
├── static/
│   ├── css/
│   │   └── style.css             ← Main stylesheet
│   └── js/
│       └── main.js               ← Main JavaScript utilities
│
├── templates/
│   ├── base.html                 ← Base layout with navbar & footer
│   ├── index.html                ← Home page (hero + features)
│   ├── login.html                ← Login page
│   ├── register.html             ← Register page
│   ├── dashboard.html            ← KPI cards + 4 charts
│   ├── predict.html              ← Congestion prediction form + result
│   ├── route_suggestion.html     ← Smart route suggestion page
│   ├── alerts.html               ← High congestion alerts page
│   ├── history.html              ← Prediction history table
│   ├── powerbi.html              ← Power BI dashboard embed page
│   ├── admin.html                ← Admin panel (manage records + users)
│   └── about.html                ← About project page
│
└── exports/                      ← (auto-created) temporary export files
```

---

## ⚙️ Setup Instructions

### Step 1 — Install Python (3.9 or higher)
Download from: https://www.python.org/downloads/

### Step 2 — Install MySQL Server
Download from: https://dev.mysql.com/downloads/installer/
- Set root password during installation (remember it!)
- Default port: 3306

### Step 3 — Create Virtual Environment
```bash
cd urban_traffic_system
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### Step 4 — Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 5 — Setup MySQL Database
Open MySQL Command Line or MySQL Workbench and run:
```bash
mysql -u root -p < database.sql
```
OR open MySQL Workbench → File → Open SQL Script → select database.sql → Execute

### Step 6 — Configure Database Password
Open `app.py` and update the DB_CONFIG section (around line 22):
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_MYSQL_PASSWORD_HERE',   # ← change this
    'database': 'urban_traffic_db',
}
```

### Step 7 — Run the Application
```bash
python app.py
```

### Step 8 — Open in Browser
```
http://localhost:5000
```

---

## 🔐 Default Login Credentials

| Role  | Email                | Password  |
|-------|----------------------|-----------|
| Admin | admin@traffic.com    | admin123  |
| User  | user@traffic.com     | user123   |

> **Note:** The demo users in database.sql have hashed passwords. Use the Register page to create fresh accounts, which will work immediately. OR register new users directly from the website.

### ✅ Recommended First-Time Setup:
1. Open `http://localhost:5000/register`
2. Register an Admin account (select role: Admin)
3. Register a User account (select role: User)
4. Login and start using the system

---

## 📊 Pages & Features

| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Hero section, features, how it works |
| Login | `/login` | Role-based login (User / Admin) |
| Register | `/register` | New account creation |
| Dashboard | `/dashboard` | KPI cards + 4 interactive charts |
| Predict | `/predict` | ML congestion prediction form + result |
| Route Suggestion | `/route-suggestion` | Smart alternate route recommender |
| Alerts | `/alerts` | High congestion alert list |
| History | `/history` | Prediction history with search/filter/export |
| Power BI | `/powerbi` | Power BI embed + demo charts |
| Admin Panel | `/admin` | Manage records, users, alerts |
| About | `/about` | Project details for viva |
| Logout | `/logout` | End session |

---

## 🤖 ML Model Details

- **Algorithm:** Random Forest Classifier (scikit-learn)
- **Training Data:** 2,000 synthetic traffic records
- **Input Features:** Day, Hour, Weather, Vehicle Count, Average Speed, Road Type
- **Output Classes:** Low / Medium / High congestion
- **Model File:** `ml_model/model.pkl` (auto-generated on first run)
- **Accuracy:** ~90–95% on synthetic test data
- **Fallback:** Rule-based engine if scikit-learn is not available

### How Prediction Works:
1. User enters 8 parameters in the prediction form
2. Flask API encodes categorical data (weather, road type, day) to numbers
3. Random Forest model predicts one of: Low / Medium / High
4. System also calculates: severity, estimated delay, safety message
5. Result saved to `prediction_history` table in MySQL
6. If HIGH → alert automatically saved to `alerts` table

---

## 📤 Export Feature

- **CSV Export:** Downloads all prediction history as `.csv` file
- **PDF Export:** Downloads formatted PDF report using ReportLab
- Available on: History page, Admin panel, Dashboard quick actions

---

## 📌 Power BI Integration

To embed your actual Power BI dashboard:
1. Create a report in Power BI Desktop connected to your MySQL database
2. Publish to Power BI Service (powerbi.microsoft.com)
3. Get the embed URL from: Report → File → Embed Report → Website or portal
4. Open `templates/powerbi.html` and replace `YOUR_POWER_BI_EMBED_URL_HERE` with your link

---

## 🛠 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `mysql.connector.errors.DatabaseError` | Check MySQL is running and password is correct in `app.py` |
| `Model not found` | Delete `ml_model/model.pkl` and restart app (it will retrain) |
| Port 5000 in use | Change `app.run(port=5001)` in `app.py` |
| PDF export fails | Run `pip install reportlab` |

---

## 🎓 Viva Explanation Points

1. **Architecture:** 3-tier — Frontend (HTML/Bootstrap), Backend (Flask/Python), Database (MySQL)
2. **ML Model:** Random Forest with 100 estimators, trained on 2000 records, 6 features
3. **Prediction:** Encodes categorical → numerical → ML classifies → result displayed
4. **Alerts:** Auto-triggered when HIGH prediction made, stored in alerts table
5. **Route Suggestion:** Rule-based engine using congestion + weather as decision factors
6. **Power BI:** Connects to MySQL for real-time analytics dashboards
7. **Security:** Werkzeug password hashing (PBKDF2-SHA256), session-based auth, role-based access
8. **Export:** CSV via Python csv module, PDF via ReportLab library

---

*Built with ❤️ for MCA Final Year Project Submission*
