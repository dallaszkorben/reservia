# Reservia - Resource Reservation Management System

A Flask-based web application for managing and administering reservation requests for public resources.

## Description
The application is designed to manage and administer reservation requests for a given public resource. It allows users to request, book, and track availability, while providing administrators with tools to oversee and coordinate the usage of that resource.

## Technology Stack
- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML templates served by Flask
- **Web Server**: Apache2

## Project Structure
```
reservia/
├── backend/
│   ├── app/
│   │   ├── views/       # Flask blueprints and endpoints
│   │   ├── models/      # SQLAlchemy database models
│   │   └── __init__.py  # Flask application factory
│   └── config/          # Backend configuration files
├── frontend/
│   ├── templates/       # HTML templates
│   └── static/          # CSS, JavaScript, images
├── tests/               # Test files
├── docs/                # Documentation
├── app.py              # Main Flask application entry point
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Running the Server

### Temporary Development Server (Flask built-in)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the development server:
```bash
python app.py
```

3. Access the application:
- Main page: http://localhost:5000
- Health check: http://localhost:5000/info/is_alive

### Permanent Production Server (Apache2)
(To be configured in future development phases)

## Setup Instructions
(To be added in future development phases)

## Features
(To be developed step by step)