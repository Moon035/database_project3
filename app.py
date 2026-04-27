import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "project3.db")


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# User selection page
@app.route("/")
def index():
    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users ORDER BY user_id").fetchall()
    conn.close()
    return render_template("index.html", users=users)


# Add new user
@app.route("/users/add", methods=("GET", "POST"))
def add_user():
    conn = get_db_connection()

    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()

        if not username or not email:
            conn.close()
            return "Username and email are required", 400
        
        try:
            conn.execute("""
                INSERT INTO users(
                    username,
                    email,
                    created_date,
                    last_updated_metadata)
                VALUES (?, ?, DATE('now'), DATETIME('now'))""", (username, email))
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return f"Database error: {e}", 500
        
        conn.close()
        return redirect(url_for("index"))
    
    conn.close()
    return render_template("add_user.html")


# Room List
@app.route("/rooms")
def room_list():
    conn = get_db_connection()

    rooms = conn.execute("""
                SELECT rooms.room_id,
                       rooms.room_name,
                       rooms.floor_number,
                       rooms.created_date,
                       rooms.last_updated_metadata,
                       COUNT(devices.device_id) AS device_count
                FROM rooms
                LEFT JOIN devices ON rooms.room_id = devices.room_id
                GROUP BY rooms.room_id
                ORDER BY rooms.room_id""").fetchall()
    conn.close()
    return render_template("rooms.html", rooms=rooms)


# Add new room
@app.route("/rooms/add", methods=("GET", "POST"))
def add_room():
    conn = get_db_connection()

    if request.method == "POST":
        room_name = request.form["room_name"].strip()
        floor_number = request.form["floor_number"]

        if not room_name:
            conn.close()
            return "Room name is required.", 400
        
        try:
            floor_value = int(floor_number)
            if floor_value < 0:
                conn.close()
                return "Floor number can't be negative.", 400
        except ValueError:
            conn.close()
            return "Floor number must be a valid integer.", 400
        
        try:
            conn.execute("""
                INSERT INTO rooms (
                    room_name,
                    floor_number,
                    created_date,
                    last_updated_metadata)
                VALUES (?, ?, DATE('now'), DATETIME('now'))""", (room_name, floor_value))
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return f"Database error: {e}", 500
        
        conn.close()
        return redirect(url_for("room_list"))
    
    conn.close()
    return render_template("add_room.html")


# Device list for selected user
@app.route("/user/<int:user_id>")
def user_devices(user_id):
    conn = get_db_connection()

    user = conn.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    if user is None:
        conn.close()
        return "User not found", 404

    devices = conn.execute("""
        SELECT devices.device_id,
               devices.device_name,
               devices.device_type,
               devices.status,
               devices.install_date,
               devices.power_usage_watts,
               rooms.room_name
        FROM devices
        JOIN rooms ON devices.room_id = rooms.room_id
        WHERE devices.user_id = ?
        ORDER BY devices.device_id
    """, (user_id,)).fetchall()

    conn.close()
    return render_template("devices.html", user=user, devices=devices)


# Add device for selected user
@app.route("/user/<int:user_id>/add", methods=("GET", "POST"))
def add_device(user_id):
    conn = get_db_connection()

    user = conn.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    rooms = conn.execute("SELECT * FROM rooms ORDER BY room_id").fetchall()

    if user is None:
        conn.close()
        return "User not found", 404

    if request.method == "POST":
        name = request.form["device_name"].strip()
        dtype = request.form["device_type"].strip()
        status = request.form["status"]
        room_id = request.form["room_id"]

        if not name or not dtype:
            conn.close()
            return "Device name and device type are required.", 400

        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO devices (
                    device_name,
                    device_type,
                    status,
                    user_id,
                    room_id,
                    install_date,
                    power_usage_watts,
                    last_updated_metadata
                )
                VALUES (?, ?, ?, ?, ?, DATE('now'), 0, DATETIME('now'))
            """, (name, dtype, status, user_id, room_id))

            new_device_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO device_logs (
                    device_id,
                    action_type,
                    action_date,
                    notes,
                    last_updated_metadata
                )
                VALUES (?, ?, DATE('now'), ?, DATETIME('now'))
            """, (new_device_id, "Created", f"{name} was added."))

            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return f"Database error: {e}", 500

        conn.close()
        return redirect(url_for("user_devices", user_id=user_id))

    conn.close()
    return render_template("add.html", user=user, rooms=rooms)


# Edit selected user's device
@app.route("/user/<int:user_id>/edit/<int:device_id>", methods=("GET", "POST"))
def edit_device(user_id, device_id):
    conn = get_db_connection()

    user = conn.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    device = conn.execute(
        "SELECT * FROM devices WHERE device_id = ? AND user_id = ?",
        (device_id, user_id)
    ).fetchone()

    rooms = conn.execute("SELECT * FROM rooms ORDER BY room_id").fetchall()

    if user is None:
        conn.close()
        return "User not found", 404

    if device is None:
        conn.close()
        return "Device not found", 404

    if request.method == "POST":
        name = request.form["device_name"].strip()
        dtype = request.form["device_type"].strip()
        status = request.form["status"]
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
            cursor.execute("""
                UPDATE devices
                SET device_name = ?,
                    device_type = ?,
                    status = ?,
                    room_id = ?,
                    power_usage_watts = ?,
                    last_updated_metadata = DATETIME('now')
                WHERE device_id = ? AND user_id = ?
            """, (name, dtype, status, room_id, power_usage_value, device_id, user_id))

            cursor.execute("""
                INSERT INTO device_logs (
                    device_id,
                    action_type,
                    action_date,
                    notes,
                    last_updated_metadata
                )
                VALUES (?, ?, DATE('now'), ?, DATETIME('now'))
            """, (device_id, "Updated", f"{name} was updated."))

            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return f"Database error: {e}", 500

        conn.close()
        return redirect(url_for("user_devices", user_id=user_id))

    conn.close()
    return render_template("edit.html", user=user, device=device, rooms=rooms)


# Delete selected user's device
@app.route("/user/<int:user_id>/delete/<int:device_id>")
def delete_device(user_id, device_id):
    conn = get_db_connection()

    device = conn.execute(
        "SELECT * FROM devices WHERE device_id = ? AND user_id = ?",
        (device_id, user_id)
    ).fetchone()

    if device is None:
        conn.close()
        return "Device not found", 404

    try:
        conn.execute(
            "DELETE FROM devices WHERE device_id = ? AND user_id = ?",
            (device_id, user_id)
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        return f"Database error: {e}", 500

    conn.close()
    return redirect(url_for("user_devices", user_id=user_id))


# Dashboard for selected user
@app.route("/user/<int:user_id>/dashboard")
def dashboard(user_id):
    conn = get_db_connection()

    user = conn.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    if user is None:
        conn.close()
        return "User not found", 404

    total_devices = conn.execute("""
        SELECT COUNT(*) AS count
        FROM devices
        WHERE user_id = ?
    """, (user_id,)).fetchone()["count"]

    on_devices = conn.execute("""
        SELECT COUNT(*) AS count
        FROM devices
        WHERE user_id = ? AND status = 'ON'
    """, (user_id,)).fetchone()["count"]

    avg_power = conn.execute("""
        SELECT AVG(power_usage_watts) AS avg_power
        FROM devices
        WHERE user_id = ?
    """, (user_id,)).fetchone()["avg_power"]

    conn.close()

    return render_template(
        "dashboard.html",
        user=user,
        total_devices=total_devices,
        on_devices=on_devices,
        avg_power=avg_power
    )


# Logs for selected user's devices
@app.route("/user/<int:user_id>/logs")
def view_logs(user_id):
    conn = get_db_connection()

    user = conn.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    if user is None:
        conn.close()
        return "User not found", 404

    logs = conn.execute("""
        SELECT device_logs.log_id,
               device_logs.device_id,
               devices.device_name,
               device_logs.action_type,
               device_logs.action_date,
               device_logs.notes,
               device_logs.last_updated_metadata
        FROM device_logs
        JOIN devices ON device_logs.device_id = devices.device_id
        WHERE devices.user_id = ?
        ORDER BY device_logs.log_id DESC
    """, (user_id,)).fetchall()

    conn.close()
    return render_template("logs.html", user=user, logs=logs)


if __name__ == "__main__":
    app.run(debug=True)