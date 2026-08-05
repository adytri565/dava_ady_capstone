# src/admin/controllers.py
from flask import render_template, session, redirect
from src import mysql
from src.admin import admin_bp  # 🌟 Ambil blueprint dari __init__.py lokal folder admin
import MySQLdb.cursors

# ==========================================
# 1. OVERVIEW DASHBOARD
# ==========================================
@admin_bp.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/api/auth/login-page')
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute("SELECT COUNT(*) as total FROM drivers")
    total_vehicles = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM alert_logs WHERE severity = 'Critical'")
    drowsiness_alerts_today = cursor.fetchone()['total']
    
    cursor.execute("""
        SELECT 
            d.driver_id as id, d.name, d.avatar, 
            IFNULL(al.event_type, 'FOCUSED') as status, 
            IFNULL(al.speed, 0) as speed, 
            IFNULL(al.destination, 'Standby') as destination 
        FROM drivers d
        LEFT JOIN alert_logs al ON al.id = (
            SELECT MAX(id) FROM alert_logs WHERE driver_id = d.driver_id
        )
    """)
    drivers = cursor.fetchall()
    
    cursor.execute("""
        SELECT 
            TIME(created_at) as time, 
            (SELECT name FROM drivers WHERE driver_id = alert_logs.driver_id) as driver, 
            event_type as type, severity 
        FROM alert_logs 
        ORDER BY id DESC LIMIT 5
    """)
    alerts = cursor.fetchall()
    cursor.close()
    
    real_data = {
        "stats": {
            "total_vehicles": total_vehicles,
            "active_deliveries": total_vehicles, 
            "drowsiness_alerts_today": drowsiness_alerts_today,
            "on_time_rate": "96%"
        },
        "drivers": drivers,
        "alerts": alerts
    }
    return render_template('dashboard.html', data=real_data)

# ==========================================
# 2. LIVE FLEET MAP
# ==========================================
@admin_bp.route('/map', methods=['GET'])
def fleet_map():
    if 'user_id' not in session:
        return redirect('/api/auth/login-page')
    return render_template('map.html')

# ==========================================
# 3. DRIVER MONITOR
# ==========================================
@admin_bp.route('/drivers', methods=['GET'])
def drivers_monitor():
    if 'user_id' not in session:
        return redirect('/api/auth/login-page')
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT d.driver_id as id, d.name, d.vehicle_name as vehicle, d.phone, IFNULL(al.event_type, 'Focused') as status,
               IFNULL(al.ear_value, 0.28) as ear, IFNULL(al.blink_rate, 12) as blink_rate, IFNULL(al.speed, 0) as speed
        FROM drivers d
        LEFT JOIN alert_logs al ON al.id = (
            SELECT MAX(id) FROM alert_logs WHERE driver_id = d.driver_id
        )
    """)
    drivers_data = cursor.fetchall()
    cursor.close()
    
    return render_template('drivers.html', data={"drivers": drivers_data})

# ==========================================
# 4. ALERT CENTER
# ==========================================
@admin_bp.route('/alerts', methods=['GET'])
def alert_center():
    if 'user_id' not in session:
        return redirect('/api/auth/login-page')
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT id, TIME(created_at) as time, DATE(created_at) as date, driver_id as vehicle,
               (SELECT name FROM drivers WHERE driver_id = alert_logs.driver_id) as driver, event_type as event, severity
        FROM alert_logs ORDER BY id DESC
    """)
    logs_data = cursor.fetchall()
    cursor.close()
    
    return render_template('alerts.html', data={"logs": logs_data})

# ==========================================
# 5. USER PROFILE PAGE
# ==========================================
@admin_bp.route('/profile', methods=['GET'])
def user_profile():
    if 'user_id' not in session:
        return redirect('/api/auth/login-page')
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id, name, email, role, created_at FROM users WHERE id = %s", (session['user_id'],))
    user_data = cursor.fetchone()
    cursor.close()
    
    return render_template('profile.html', user=user_data)