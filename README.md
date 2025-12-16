# 🐔 PoultraGuard — Poultry Monitoring & Simulation System

PoultraGuard is a web-based poultry monitoring and simulation application built to demonstrate how smart poultry farms can monitor environmental conditions in real time — without relying on physical IoT hardware.

The system simulates environmental sensor data such as temperature, humidity, ammonia levels, feed status, water availability, and bird activity. It is designed for education, research, prototyping, and demonstration purposes, with a backend architecture that can later be extended to support real IoT sensor integration.

## 🎯 Project Purpose

This project aims to:
- Demonstrate how modern poultry monitoring systems work
- Provide a realistic simulation of farm conditions
- Support block-based flock management (multiple poultry sections)
- Show how alerts and historical data improve farm decision-making
- Serve as a foundation for future IoT-enabled poultry systems

## ✨ Key Features

- **User authentication and access control**
- **Block-based flock management** (up to multiple poultry blocks per user)
- **Real-time virtual sensor simulation** per flock block
- **Environmental monitoring**:
  - Temperature
  - Humidity
  - Ammonia levels
  - Feed level
  - Water level
  - Bird activity level
- **Automatic alert generation** for abnormal conditions
- **Dashboard** with summarized block statistics
- **Live simulation page** with real-time updates
- **Historical data tracking** and visualization
- **Clean, responsive UI** using Bootstrap 5

## ⚙️ How the System Works (Developer Overview)

1. Users create one or more flock blocks, each representing a poultry section.
2. When a block simulation starts, a background simulation engine runs independently for that block.
3. The simulation engine continuously generates realistic sensor values using Python logic.
4. Generated data is saved to the database using Django ORM.
5. Threshold checks run automatically to detect abnormal conditions.
6. Alerts are created and stored when thresholds are exceeded.
7. The dashboard displays a snapshot of the latest data per block.
8. The live simulation page shows real-time updates and movement behavior.
9. Historical data can be viewed for trend analysis.

*This mirrors a real smart-farm architecture, with software-based sensors replacing physical devices.*

## 🗂️ System Architecture (High Level)

- **Django** handles routing, authentication, business logic, and database interaction
- A **background simulation service** generates data per flock block
- **REST endpoints** expose monitoring data and alerts
- **Server-rendered templates** display dashboards and live views
- **SQLite** is used during development, while **MySQL** is used in production

## 🛠️ Technology Stack

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript

### Backend
- Python
- Django Framework

### Database
- SQLite (development)
- MySQL (production deployment on PythonAnywhere)

### Other Tools & Libraries
- Django ORM for database operations
- Django REST Framework (for APIs)
- Chart.js for data visualization
- Thread-based background simulation engine

## 📸 Screenshots

Screenshots of the application interface are included in the repository to demonstrate the system visually.

**Planned screenshots include:**
- Home page
- Dashboard overview
- Blocks list page
- Block creation page
- Live simulation page
- Block details page
- History and charts view

📁 Screenshots will be stored in the repository under a directory such as:

/screenshots/


## 🚀 Setup & Development Notes

- Designed for local development using SQLite
- Easily deployable to PythonAnywhere using MySQL
- Simulation engine runs automatically when blocks are started
- No external hardware dependencies required
- Suitable for academic projects and demonstrations

## 🔮 Future Improvements

- Integration with real IoT sensors
- Mobile-optimized interface
- Advanced analytics and prediction models
- Notification delivery via email or SMS
- Role-based access (admin / farm manager)
- Cloud-based scaling for large farms

## 📌 Author & Project Status

This project is actively developed as a simulation-driven poultry monitoring system and serves as a strong foundation for future smart agriculture solutions.