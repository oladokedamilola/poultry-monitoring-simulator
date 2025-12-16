# 🐔 Poultry Monitoring Simulation Web App

A web-based simulation system designed to mimic real-time poultry farm monitoring using virtual environmental sensors. This system continuously generates and analyzes simulated data for conditions like temperature, humidity, ammonia levels, feed status, and bird activity — without relying on physical IoT hardware.

The purpose is to demonstrate how smart poultry monitoring systems work in real farm scenarios, while keeping the implementation cost-effective and suitable for research, education, and future IoT integration.

---

## ✨ Features

- 🔹 Real-time simulation of poultry environmental conditions
- 🔹 Smart alert system for abnormal readings
- 🔹 Data visualization through interactive charts and UI indicators
- 🔹 Historical data storage for trends and analysis
- 🔹 Fully responsive dashboard (Bootstrap 5)
- 🔹 Scalable backend ready for real sensor integration in the future

---

## ⚙️ How It Works

1. A **simulation engine** generates synthetic sensor data at regular intervals.
2. Generated data is stored in the database using Django ORM.
3. The system checks for threshold violations and triggers alerts when necessary.
4. The **frontend dashboard** fetches live data through API requests and updates visual components:
   - Live charts
   - Feed/water indicators
   - Alerts panel
   - Environmental gauges

This architecture mirrors a real IoT monitoring workflow — but replaces hardware sensors with software logic.

---

## 🛠️ Tech Stack

**Frontend**
- HTML5
- CSS3
- Bootstrap 5
- JavaScript

**Backend**
- Python
- Django Framework

**Database**
- PostgreSQL / MySQL (configurable)

---

📍 *Future improvements may include real sensor integration, authentication, device management, predictive analytics, and mobile UI optimization.*

