import os
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "project3.db")

# Connect to DB
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# Home
@app.route("/")
def index():
    conn = get_db_connection()

    devices = conn.execute("""
        SELECT devices.device_id, devices.device_name, devices.device_type, devices.status,
               devices.install_date, devices.power_usage_watts, users.username, rooms.room_name
                           
        FROM devices
                           
        JOIN users ON devices.user_id = users.user_id
        JOIN rooms ON devices.room_id = rooms.room_id
        ORDER BY devices.device_id""").fetchall()
    
    conn.close()
    return render_template("index.html", devices=devices)


# Add device
@app.route("/add", methods=("GET", "POST"))
def add_device():
    conn = get_db_connection()

    users = conn.execute("SELECT * FROM users").fetchall()
    rooms = conn.execute("SELECT * FROM rooms").fetchall()

    if request.method == "POST":
        name = request.form["device_name"].strip()
        dtype = request.form["device_type"].strip()
        status = request.form["status"]
        user_id = request.form["user_id"]
        room_id = request.form["room_id"]

        if not name or not dtype:
            conn.close()
            return "Device name and device type are required.", 400
        
        cursor = conn.cursor()

        try:
            # insert device
            cursor.execute("""
                INSERT INTO devices(device_name, device_type, status, user_id, room_id, install_date, 
                                    power_usage_watts, last_updated_metadata) 
                VALUES (?, ?, ?, ?, ?, DATE('now'), 0, DATETIME('now'))""", (name, dtype, status, user_id, room_id))
            new_device_id = cursor.lastrowid

            # insert log
            cursor.execute("""
                INSERT INTO device_logs (
                           device_id, action_type, action_date, notes, last_updated_metadata)
                VALUES (?, ?, DATE('now'), ?, DATETIME('now'))""", (new_device_id, "Created", f"{name} was added"))
            conn.commit()

        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return f"Database error: {e}", 500
        
        conn.close()
        return redirect(url_for("index"))
    
    conn.close()
    return render_template("add.html", users=users, rooms=rooms)


# Edit device
@app.route("/edit/<int:id>", methods=("GET", "POST"))
def edit_device(id):
    conn = get_db_connection()

    device = conn.execute(
        "SELECT * FROM devices WHERE device_id = ?",
        (id,)
    ).fetchone()

    users = conn.execute("SELECT * FROM users ORDER BY user_id").fetchall()
    rooms = conn.execute("SELECT * FROM rooms ORDER BY room_id").fetchall()

    if device is None:
        conn.close()
        return "Device not found", 404

    if request.method == "POST":
        name = request.form["device_name"].strip()
        dtype = request.form["device_type"].strip()
        status = request.form["status"]
        user_id = request.form["user_id"]
        room_id = request.form["room_id"]
        power_usage = request.form["power_usage_watts"]

        if not name or not dtype:
            conn.close()
            return "Device name and device type are required.", 400

        try:
            power_usage_value = float(power_usage)
            if power_usage_value < 0:
                conn.close()
                return "Power usage cannot be negative.", 400
        except ValueError:
            conn.close()
            return "Power usage must be a valid number.", 400

        cursor = conn.cursor()

        try:
            # update device
            cursor.execute("""
                UPDATE devices
                SET device_name = ?,
                    device_type = ?,
                    status = ?,
                    user_id = ?,
                    room_id = ?,
                    power_usage_watts = ?,
                    last_updated_metadata = DATETIME('now')
                WHERE device_id = ?
            """, (name, dtype, status, user_id, room_id, power_usage_value, id))

            # insert log
            cursor.execute("""
                INSERT INTO device_logs (
                    device_id, action_type, action_date, notes, last_updated_metadata)
                VALUES (?, ?, DATE('now'), ?, DATETIME('now'))""", (id, "Updated", f"{name} was updated."))

            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return f"Database error: {e}", 500

        conn.close()
        return redirect(url_for("index"))

    conn.close()
    return render_template("edit.html", device=device, users=users, rooms=rooms)


# Delete device
@app.route("/delete/<int:id>")
def delete_device(id):
    conn = get_db_connection()

    device = conn.execute(
        "SELECT * FROM devices WHERE device_id = ?",
        (id,)
    ).fetchone()

    if device is None:
        conn.close()
        return "Device not found", 404

    try:
        conn.execute("DELETE FROM devices WHERE device_id = ?", (id,))
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        return f"Database error: {e}", 500

    conn.close()
    return redirect(url_for("index"))


# Dashboard
@app.route("/dashboard")
def dashboard():
    conn = get_db_connection()

    total_devices = conn.execute(
        "SELECT COUNT(*) AS count FROM devices"
    ).fetchone()["count"]

    on_devices = conn.execute(
        "SELECT COUNT(*) AS count FROM devices WHERE status = 'ON'"
    ).fetchone()["count"]

    avg_power = conn.execute(
        "SELECT AVG(power_usage_watts) AS avg_power FROM devices"
    ).fetchone()["avg_power"]

    conn.close()

    return render_template(
        "dashboard.html",
        total_devices=total_devices,
        on_devices=on_devices,
        avg_power=avg_power
    )


# View logs
@app.route("/logs")
def view_logs():
    conn = get_db_connection()

    logs = conn.execute("""
        SELECT device_logs.log_id, device_logs.device_id, devices.device_name, device_logs.action_type,
               device_logs.action_date, device_logs.notes, device_logs.last_updated_metadata
        FROM device_logs
        JOIN devices ON device_logs.device_id = devices.device_id
        ORDER BY device_logs.log_id DESC
    """).fetchall()

    conn.close()
    return render_template("logs.html", logs=logs)


if __name__ == "__main__":
    app.run(debug=True)
    