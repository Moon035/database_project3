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

## 2. Analysis of Possible Anomalies

### users
User information is stored in a separate table, so updating a user's information only requires modifying one row.

### rooms
Room data is isolated from device records, which avoids repeating room details for every device.

### devices
Each device references one user and one room through foreign keys, which prevents duplicate ownership or location data.

### device_logs
Log records are separated from devices so multiple log entries can be stored without duplicating device information.

---

## 3. Normal Form Evaluation

The schema was reviewed for normalization as follows:

- All tables satisfy **1NF** because each column stores atomic values.
- All tables satisfy **2NF** because every non-key attribute fully depends on the entire primary key.
- All tables satisfy **3NF** because no non-key attribute depends on another non-key attribute.
- The schema satisfies **BCNF** because every determinant in each table is a candidate key.

No further decomposition was necessary.

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