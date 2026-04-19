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
