-- Project 3: Smart Home IoT Device Management App

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS device_logs;
DROP TABLE IF EXISTS devices;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS users;

-- Table 1: users
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT UNIQUE,
    created_date DATE NOT NULL,
    last_updated_metadata TIMESTAMP NOT NULL
);

-- Table 2: rooms
CREATE TABLE rooms (
    room_id INTEGER PRIMARY KEY,
    room_name TEXT NOT NULL,
    floor_number INTEGER NOT NULL CHECK (floor_number >= 0),
    created_date DATE NOT NULL,
    last_updated_metadata TIMESTAMP NOT NULL
);

-- Table 3: devices
CREATE TABLE devices (
    device_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    device_name TEXT NOT NULL,
    device_type TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('ON', 'OFF', 'STANDBY', 'ERROR')),
    install_date DATE NOT NULL,
    power_usage_watts REAL NOT NULL CHECK (power_usage_watts >= 0),
    last_updated_metadata TIMESTAMP NOT NULL,

    CONSTRAINT fk_devices_user
        FOREIGN KEY(user_id) REFERENCES users(user_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_devices_room
        FOREIGN KEY(room_id) REFERENCES rooms(room_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- Table 4: device_logs
CREATE TABLE device_logs (
    log_id INTEGER PRIMARY KEY,
    device_id INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    action_date DATE NOT NULL,
    notes TEXT,
    last_updated_metadata TIMESTAMP NOT NULL,

    CONSTRAINT fk_logs_device
        FOREIGN KEY(device_id) REFERENCES devices(device_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);



-- Insert Data into users
INSERT INTO users(user_id, username, email, created_date, last_updated_metadata) VALUES
(1, 'isaac', 'isaac@example.com', '2026-04-01', '2026-04-01 09:00:00'),
(2, 'julian', 'julian@example.com', '2026-04-01', '2026-04-01 10:30:00'),
(3, 'justin', 'justin@example.com', '2026-04-02', '2026-04-02 09:10:30'),
(4, 'sofia', 'sofia@example.com', '2026-04-05', '2026-04-05 11:04:17'),
(5, 'lousia', 'lousia@example.com', '2026-04-06', '2026-04-06 08:37:49');

-- Insert data into rooms
INSERT INTO rooms(room_id, room_name, floor_number, created_date, last_updated_metadata) VALUES
(1, 'Living Room', 1, '2026-04-01', '2026-04-01 09:00:00'),
(2, 'Kitchen', 1, '2026-04-01', '2026-04-01 09:05:13'),
(3, 'Bedroom', 2, '2026-04-02', '2026-04-02 10:34:07'),
(4, 'Garage', 1, '2026-04-02', '2026-04-02 10:43:24'),
(5, 'Entrance', 1, '2026-04-05', '2026-04-05 11:27:53');

-- Insert data into devices
INSERT INTO devices(device_id, user_id, room_id, device_name, device_type, status, install_date, power_usage_watts, last_updated_metadata) VALUES
(1, 1, 5, 'Front Door Lock', 'Door Lock', 'ON', '2026-04-01', 5.50, '2026-04-02 13:00:00'),
(2, 2, 5, 'Outdoor Camera', 'Security Camera', 'ON', '2026-04-02', 18.00, '2026-04-02 13:30:00'),
(3, 3, 1, 'Living Room Light', 'Room Light', 'OFF', '2026-04-03', 10.00, '2026-04-03 14:00:00'),
(4, 4, 4, 'Garage Door', 'Garage Door', 'ON', '2026-04-04', 50.00, '2026-04-04 15:00:00'),
(5, 1, 2, 'Smart Refrigerator', 'Refrigerator', 'ON', '2026-04-06', 2.50, '2026-04-06 17:00:00'),
(6, 2, 3, 'Window Sensor', 'Window Sensor', 'ON', '2026-04-06', 2.50, '2026-04-06 17:00:00');

-- Insert data into device_logs
INSERT INTO device_logs(log_id, device_id, action_type, action_date, notes, last_updated_metadata) VALUES
(1, 1, 'Locked', '2026-04-01', 'Door locked', '2026-04-01 18:00:00'),
(2, 2, 'Motion Detected', '2026-04-02', 'Camera detected movement', '2026-04-02 19:00:00'),
(3, 3, 'Turned Off', '2026-04-03', 'Light turned off', '2026-04-03 22:00:00'),
(4, 4, 'Opened', '2026-04-04', 'Garage opened', '2026-04-04 21:00:00'),
(5, 5, 'Temp Changed', '2026-04-05', 'Fridge temp adjusted', '2026-04-05 21:37:00'),
(6, 6, 'Window Opened', '2026-04-06', 'Window Opened', '2026-04-06 23:00:00');