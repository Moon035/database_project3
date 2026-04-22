# Normalization Report

## 1. Original Functional Dependencies

### users
- user_id -> username, email, created_date, last_updated_metadata
- email -> user_id, username, created_date, last_updated_metadata

### rooms
- room_id -> room_name, floor_number, created_date, last_updated_metadata

### devices
- device_id -> user_id, room_id, device_name, device_type, status, install_date, power_usage_watts, last_updated_metadata

### device_logs
- log_id -> device_id, action_type, action_date, notes, last_updated_metadata

---

## 2. Anomalies

### users
- Update anomaly is minimized since each user is stored in a single row.
- Insertion anomaly is minimal.
- Deletion must consider dependent device records.

### rooms
- Data is separated from devices, reducing redundancy.
- Deletion may affect related devices.

### devices
- Requires existing user and room (insertion dependency).
- Removing a device may affect related logs.

### device_logs
- Depends on devices.
- Deleting logs removes history information.

---

## 3. Normalization

Each table structured so taht:
- All attributes depends on the priamry key
- No martial dependencies exist
- No transitive dependencies exist

Therefore, the schema satisfies BCNF.

No additional decomposition was required.

--- 

## 4. Final Schema

### users
(user_id PK, username, email, created_date, last_updated_metadata)

### rooms
(room_id PK, room_name, floor_number, created_date, last_updated_metadata)

### devices
(device_id PK, user_id FK, room_id FK, device_name, device_type, status, install_date, power_usage_watts, last_updated_metadate)

### device_logs
(log_id PK, device_id FK, action_type, action_date, notes, last_updated_metadata)