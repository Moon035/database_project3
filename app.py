from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DB_NAME = "project3.db"

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
               devices.install_date, users.username, rooms.room_name
                           
        FROM devices
                           
        JOIN users ON devices.user_id = users.user_id
        JOIN rooms ON devices.room_id = rooms.room_id""").fetchall()
    
    conn.close()
    return render_template("index.html", devices=devices)


# Add device
@app.route("/add", methods=("GET", "POST"))
def add_device():
    conn = get_db_connection()

    users = conn.execute("SELECT * FROM users").fetchall()
    rooms = conn.execute("SELECT * FROM rooms").fetchall()

    if request.method == "POST":
        name = request.form["device_name"]
        dtype = request.form["device_type"]
        status = request.form["status"]
        user_id = request.form["user_id"]
        room_id = request.form["room_id"]

        conn.execute("""
                     INSERT INTO devices (device_name, device_type, status, user_id, room_id,
                                          install_date, power_usage_watts, last_updated_metadata)
                     VALUES (?, ?, ?, ?, ?, DATE('now'), 0, DATETIME('now'))"""), (name, dtype, status, user_id, room_id)
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    
    conn.close()
    return render_template("add.html", users=users, rooms=rooms)


# Edit device
@app.route("/edit/<int:id>", methods=("GET", "POST"))
def edit_device(id):
    conn = get_db_connection()

    device = conn.execute(
        "SELECT * FROM devices WHERE device_id = ?", (id,)
    ).fetchone()
    users = conn.execute("SELECT * FROM users").fetchall()
    rooms = conn.execute("SELECT * FROM rooms").fetchall()

    if device is None:
        conn.close()
        return "Device not found", 404
    
    if request.method == "POST":
        name = request.form["device_name"]
        dtype = request.form["device_type"]
        status = request.form["status"]
        user_id = request.form["user_id"]
        room_id = request.form["room_id"]
        power_usage = request.form["power_usage_watts"]

        conn.execute("""
            UPDATE devices
            SET device_name = ?,
                device_type = ?,
                status = ?,
                user_id = ?,
                room_id = ?,
                power_usage_watts = ?,
                last_updated_metadata = DATETIME('now')
            WHERE device_id = ?""",
            (name, dtype, status, user_id, room_id, power_usage, id))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    conn.close()
    return render_template("edit.html", device=device, users=users, rooms=rooms)


# Delete device
@app.route("/delete<int:id>")
def delete_device(id):
    conn = get_db_connection()

    conn.execute("DELETE FROM devices WHERE device_id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
    