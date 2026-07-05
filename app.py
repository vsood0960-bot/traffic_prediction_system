"""
Urban Traffic Intelligence and Congestion Prediction System
Flask Backend Application
"""

from flask import Flask, request, jsonify, session, render_template, redirect, url_for, send_file
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import csv
import io
import os
import sys
import json

# Add ml_model to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ml_model'))
from traffic_model import predict_congestion, get_route_suggestion

app = Flask(__name__)
app.secret_key = 'urban_traffic_secret_key_2024'
CORS(app, supports_credentials=True)

# ─── Database Configuration ────────────────────────────────────────────────────
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vsood@1209',          
    'database': 'urban_traffic_db',
    'charset': 'utf8mb4',
    'autocommit': True
}

def get_db():
    """Get database connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        return None

def db_query(query, params=None, fetch=True, many=False):
    """Execute a database query."""
    conn = get_db()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall() if many else cursor.fetchone()
        else:
            conn.commit()
            result = cursor.lastrowid
        cursor.close()
        conn.close()
        return result
    except mysql.connector.Error as e:
        print(f"Query error: {e}")
        return None

# ─── Page Routes ───────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('dashboard.html', user=session)

@app.route('/predict')
def predict_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('predict.html', user=session)

@app.route('/route-suggestion')
def route_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('route_suggestion.html', user=session)

@app.route('/history')
def history_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('history.html', user=session)

@app.route('/alerts')
def alerts_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('alerts.html', user=session)

@app.route('/powerbi')
def powerbi_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('powerbi.html', user=session)

@app.route('/admin')
def admin_page():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login_page'))
    return render_template('admin.html', user=session)

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ─── API: Auth ─────────────────────────────────────────────────────────────────
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role = data.get('role', 'user')

    if not all([name, email, password]):
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400

    existing = db_query("SELECT id FROM users WHERE email=%s", (email,))
    if existing:
        return jsonify({'success': False, 'message': 'Email already registered.'}), 409

    hashed = generate_password_hash(password)
    db_query("INSERT INTO users (name, email, password, role) VALUES (%s,%s,%s,%s)",
             (name, email, hashed, role), fetch=False)

    return jsonify({'success': True, 'message': 'Registration successful!'})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    user = db_query("SELECT * FROM users WHERE email=%s", (email,))
    if not user:
        return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401

    if not check_password_hash(user['password'], password):
        return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401

    session['user_id'] = user['id']
    session['name'] = user['name']
    session['email'] = user['email']
    session['role'] = user['role']

    redirect_url = '/admin' if user['role'] == 'admin' else '/dashboard'
    return jsonify({'success': True, 'message': 'Login successful!',
                    'role': user['role'], 'redirect': redirect_url})

# ─── API: Dashboard ────────────────────────────────────────────────────────────
@app.route('/api/dashboard', methods=['GET'])
def api_dashboard():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    total_vehicles = db_query("SELECT COALESCE(SUM(vehicle_count),0) AS total FROM traffic_records")
    avg_speed = db_query("SELECT COALESCE(ROUND(AVG(average_speed),1),0) AS avg FROM traffic_records")
    high_areas = db_query("SELECT COUNT(DISTINCT area) AS cnt FROM traffic_records WHERE congestion_level='High'")
    total_preds = db_query("SELECT COUNT(*) AS cnt FROM prediction_history")
    total_alerts = db_query("SELECT COUNT(*) AS cnt FROM alerts")

    # Peak hour
    peak = db_query("""SELECT time, COUNT(*) AS cnt FROM traffic_records
                       GROUP BY time ORDER BY cnt DESC LIMIT 1""")

    # Charts
    congestion_dist = db_query("""SELECT congestion_level, COUNT(*) AS count
                                  FROM traffic_records GROUP BY congestion_level""", many=True)
    vehicle_by_area = db_query("""SELECT area, SUM(vehicle_count) AS total
                                  FROM traffic_records GROUP BY area ORDER BY total DESC LIMIT 8""", many=True)
    speed_trend = db_query("""SELECT DATE_FORMAT(created_at,'%d %b') AS date,
                               ROUND(AVG(average_speed),1) AS avg_speed
                               FROM traffic_records GROUP BY DATE(created_at) ORDER BY created_at LIMIT 7""", many=True)
    peak_hour = db_query("""SELECT time, COUNT(*) AS count FROM traffic_records
                            GROUP BY time ORDER BY count DESC LIMIT 8""", many=True)

    return jsonify({
        'success': True,
        'kpis': {
            'total_vehicles': int(total_vehicles['total']) if total_vehicles else 0,
            'avg_speed': float(avg_speed['avg']) if avg_speed else 0,
            'high_areas': int(high_areas['cnt']) if high_areas else 0,
            'peak_hour': peak['time'] if peak else 'N/A',
            'total_predictions': int(total_preds['cnt']) if total_preds else 0,
            'total_alerts': int(total_alerts['cnt']) if total_alerts else 0,
        },
        'charts': {
            'congestion_dist': congestion_dist or [],
            'vehicle_by_area': vehicle_by_area or [],
            'speed_trend': speed_trend or [],
            'peak_hour': peak_hour or [],
        }
    })

# ─── API: Predict ──────────────────────────────────────────────────────────────
@app.route('/api/predict', methods=['POST'])
def api_predict():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    try:
        data = request.get_json()

        required = ['area','road_name','day','time','weather','vehicle_count','average_speed','road_type']
        for field in required:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Field {field} is required.'}), 400

        result = predict_congestion(
            data['area'], data['road_name'], data['day'], data['time'],
            data['weather'], data['vehicle_count'], data['average_speed'], data['road_type']
        )

        # Save prediction history
        db_query("""
            INSERT INTO prediction_history
            (user_id, area, road_name, day, time, weather, vehicle_count, average_speed,
             road_type, predicted_congestion, estimated_delay)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            session['user_id'],
            data['area'],
            data['road_name'],
            data['day'],
            data['time'],
            data['weather'],
            int(data['vehicle_count']),
            float(data['average_speed']),
            data['road_type'],
            result['congestion_level'],
            result['estimated_delay']
        ), fetch=False)

        # Save to traffic_records
        db_query("""
            INSERT INTO traffic_records
            (area, road_name, day, time, weather, vehicle_count, average_speed, road_type, congestion_level)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            data['area'],
            data['road_name'],
            data['day'],
            data['time'],
            data['weather'],
            int(data['vehicle_count']),
            float(data['average_speed']),
            data['road_type'],
            result['congestion_level']
        ), fetch=False)

        # Save alert if High / Severe / Heavy
        if result['congestion_level'] in ['High', 'Severe Congestion', 'Heavy Traffic']:
            alert_msg = (
                f"⚠️ HIGH TRAFFIC ALERT: {data['area']} - {data['road_name']}. "
                f"Estimated delay: {result['estimated_delay']}. Avoid this route."
            )

            db_query("""
                INSERT INTO alerts
                (area, road_name, alert_message, congestion_level, estimated_delay, created_at)
                VALUES (%s,%s,%s,%s,%s,NOW())
            """, (
                data['area'],
                data['road_name'],
                alert_msg,
                result['congestion_level'],
                result['estimated_delay']
            ), fetch=False)

            print("High alert saved successfully")

        print("Prediction saved successfully in MySQL")

        return jsonify({
            'success': True,
            'result': {
                'congestion_level': result['congestion_level'],
                'confidence': result.get('confidence', 95),
                'severity': result.get('severity', result['congestion_level']),
                'estimated_delay': result.get('estimated_delay', '10-20 minutes'),
                'area': data['area'],
                'road_name': data['road_name'],
                'safety_message': result.get(
                    'safety_message',
                    'Drive safely and follow traffic rules.'
                )
            }
        })

    except Exception as e:
        print("Prediction save error:", e)
        return jsonify({'success': False, 'message': str(e)}), 500

# ─── API: Route Suggestion ────────────────────────────────────────────────────
@app.route('/api/route-suggestion', methods=['POST'])
def api_route():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    data = request.get_json()
    suggestion = get_route_suggestion(
        data.get('congestion_level', 'Low'),
        data.get('area', ''),
        data.get('road_name', ''),
        data.get('weather', 'Clear')
    )
    return jsonify({'success': True, 'suggestion': suggestion})

# ─── API: Alerts ──────────────────────────────────────────────────────────────
@app.route('/api/high-alerts', methods=['GET'])
def api_alerts():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    alerts = db_query("""SELECT * FROM alerts ORDER BY created_at DESC LIMIT 50""", many=True)
    return jsonify({'success': True, 'alerts': alerts or []})

# ─── API: Prediction History ──────────────────────────────────────────────────
@app.route('/api/prediction-history', methods=['GET'])
def api_history():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    search = request.args.get('search', '')
    filter_cong = request.args.get('congestion', '')
    role = session.get('role')
    uid = session['user_id']

    query = """SELECT ph.*, u.name AS user_name FROM prediction_history ph
               LEFT JOIN users u ON ph.user_id=u.id WHERE 1=1"""
    params = []

    if role != 'admin':
        query += " AND ph.user_id=%s"
        params.append(uid)
    if search:
        query += " AND (ph.area LIKE %s OR ph.road_name LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])
    if filter_cong:
        query += " AND ph.predicted_congestion=%s"
        params.append(filter_cong)

    query += " ORDER BY ph.created_at DESC LIMIT 100"
    records = db_query(query, tuple(params), many=True)

    # Convert datetime to string
    if records:
        for r in records:
            if r.get('created_at'):
                r['created_at'] = r['created_at'].strftime('%Y-%m-%d %H:%M:%S')

    return jsonify({'success': True, 'records': records or []})

# ─── API: Delete Record ───────────────────────────────────────────────────────
@app.route('/api/delete-record/<int:rid>', methods=['DELETE'])
def api_delete(rid):
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Admin only'}), 403
    db_query("DELETE FROM prediction_history WHERE id=%s", (rid,), fetch=False)
    return jsonify({'success': True, 'message': 'Record deleted.'})

# ─── API: Admin Users ─────────────────────────────────────────────────────────
@app.route('/api/admin/users', methods=['GET'])
def api_admin_users():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Admin only'}), 403
    users = db_query("""SELECT id, name, email, role,
                        DATE_FORMAT(created_at, '%d %b %Y') AS joined
                        FROM users ORDER BY created_at DESC""", many=True)
    return jsonify({'success': True, 'users': users or []})

# ─── API: Export CSV ──────────────────────────────────────────────────────────
@app.route('/api/export-csv', methods=['GET'])
def api_export_csv():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    uid = session['user_id']
    role = session.get('role')

    if role == 'admin':
        records = db_query("""SELECT ph.area, ph.road_name, ph.day, ph.time, ph.weather,
                              ph.vehicle_count, ph.average_speed, ph.road_type,
                              ph.predicted_congestion, ph.estimated_delay,
                              DATE_FORMAT(ph.created_at,'%Y-%m-%d %H:%M') AS date,
                              u.name AS user
                              FROM prediction_history ph LEFT JOIN users u ON ph.user_id=u.id
                              ORDER BY ph.created_at DESC""", many=True)
    else:
        records = db_query("""SELECT area, road_name, day, time, weather,
                              vehicle_count, average_speed, road_type,
                              predicted_congestion, estimated_delay,
                              DATE_FORMAT(created_at,'%Y-%m-%d %H:%M') AS date
                              FROM prediction_history WHERE user_id=%s
                              ORDER BY created_at DESC""", (uid,), many=True)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=(records[0].keys() if records else
                ['area','road_name','day','time','weather','vehicle_count',
                 'average_speed','road_type','predicted_congestion','estimated_delay','date']))
    writer.writeheader()
    writer.writerows(records or [])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'traffic_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

# ─── API: Export PDF ──────────────────────────────────────────────────────────
@app.route('/api/export-pdf', methods=['GET'])
def api_export_pdf():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    uid = session['user_id']
    role = session.get('role')

    if role == 'admin':
        records = db_query("""SELECT ph.area, ph.road_name, ph.day, ph.time, ph.weather,
                              ph.vehicle_count, ph.average_speed, ph.road_type,
                              ph.predicted_congestion, ph.estimated_delay,
                              DATE_FORMAT(ph.created_at,'%Y-%m-%d %H:%M') AS date
                              FROM prediction_history ph ORDER BY ph.created_at DESC LIMIT 100""", many=True)
    else:
        records = db_query("""SELECT area, road_name, day, time, weather,
                              vehicle_count, average_speed, road_type,
                              predicted_congestion, estimated_delay,
                              DATE_FORMAT(created_at,'%Y-%m-%d %H:%M') AS date
                              FROM prediction_history WHERE user_id=%s
                              ORDER BY created_at DESC LIMIT 100""", (uid,), many=True)

    records = records or []

    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.units import inch

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=landscape(A4), rightMargin=30, leftMargin=30,
                                topMargin=30, bottomMargin=30)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("Urban Traffic Intelligence – Prediction Report",
                                  styles['Title']))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}",
                                  styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))

        headers = ['Area','Road','Day','Time','Weather','Vehicles','Avg Speed',
                   'Road Type','Congestion','Delay','Date']
        data = [headers]
        for r in records:
            data.append([
                r.get('area',''), r.get('road_name',''), r.get('day',''), r.get('time',''),
                r.get('weather',''), str(r.get('vehicle_count','')), str(r.get('average_speed','')),
                r.get('road_type',''), r.get('predicted_congestion',''),
                r.get('estimated_delay',''), r.get('date','')
            ])

        t = Table(data, repeatRows=1)
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0d1b4b')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 7),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f0f4ff')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ])
        for i, row in enumerate(data[1:], 1):
            cong = row[8]
            if cong == 'High':
                style.add('TEXTCOLOR', (8, i), (8, i), colors.red)
            elif cong == 'Medium':
                style.add('TEXTCOLOR', (8, i), (8, i), colors.orange)
            else:
                style.add('TEXTCOLOR', (8, i), (8, i), colors.green)
        t.setStyle(style)
        elements.append(t)

        doc.build(elements)
        buf.seek(0)
        return send_file(buf, mimetype='application/pdf', as_attachment=True,
                         download_name=f'traffic_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
    except ImportError:
        return jsonify({'success': False,
                        'message': 'PDF export requires reportlab. Run: pip install reportlab'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
