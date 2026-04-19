# Smart Home IoT Device Management App

## Project Description
This project is a full-stack Python web application for managing smart home devices.
It allows users to organize devices by room, track device status, and store activity logs for each device.

The app is designed for a simple smart home environment where users can:
- manage rooms
- manage devices
- track device activity logs
- view summary information about the system

The database design is based on four related tables:
- users
- rooms
- devices
- device_logs

---

## Features
- Multi-table CRUD across related tables
- One-to-many relationship handling
- Device log tracking
- Server-side validation for bad input
- Summary dashboard using aggregate queries
- Transaction-based update logic for device status and log creation

## Technical Stack
- SQLite
- Python3
- HTML
- CSS

---

## Installation Instructions

### 1. Clone the repository
```bash
git clone 
cd database_project3
```

