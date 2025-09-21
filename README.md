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
│   │   ├── views/           # Flask blueprints and endpoints
│   │   │   ├── base_view.py     # Base view class for inheritance
│   │   │   ├── home_bp.py       # Home blueprint manager
│   │   │   └── info_bp.py       # Info blueprint manager
│   │   ├── models/          # SQLAlchemy database models
│   │   ├── application.py   # Main ReserviaApp class
│   │   ├── constants.py     # Global constants (log prefixes)
│   │   ├── database.py      # Database singleton class
│   │   └── __init__.py      # Package initialization
│   └── config/          # Backend configuration files
├── frontend/
│   ├── templates/       # HTML templates
│   └── static/          # CSS, JavaScript, images
├── tests/
│   └── test_database.py # Database functionality tests
├── docs/                # Documentation
├── app.py              # Main Flask application entry point
├── requirements.txt    # Python dependencies
├── project_context.md  # Amazon Q session context
└── README.md           # This file
```

## Running the Server

### Temporary Development Server (Flask built-in)

1. Create and activate virtual environment:
```bash
python3 -m venv env
source env/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the development server:
```bash
python app.py
```

4. Access the application:
- Main page: http://localhost:5000
- Health check: http://localhost:5000/info/is_alive
- Version info: http://localhost:5000/info/get_version

### Permanent Production Server (Apache2)
(To be configured in future development phases)

## Setup Instructions
(To be added in future development phases)

## Database Schema

### Users Table
- `id` (INTEGER, Primary Key, Auto-increment)
- `email` (TEXT, Unique, NOT NULL)
- `name` (TEXT, NOT NULL)

### Resources Table
- `id` (INTEGER, Primary Key, Auto-increment)
- `name` (TEXT, Unique, NOT NULL)
- `comment` (TEXT, NULL)

### Request Table
- `id` (INTEGER, Primary Key, Auto-increment)
- `user_id` (INTEGER, Foreign Key → Users.id)
- `resource_id` (INTEGER, Foreign Key → Resources.id)
- `request_date` (INTEGER, NOT NULL) - Unix timestamp
- `approved_date` (INTEGER, NULL) - Unix timestamp
- `cancelled_date` (INTEGER, NULL) - Unix timestamp

## Current Features

### API Endpoints
- **GET /** - Main application page
- **GET /info/is_alive** - Health check endpoint
- **GET /info/get_version** - Application version information
- **POST /admin/user/add** - Add new user (requires JSON payload)

### Database Management
- SQLite database with SQLAlchemy ORM
- Automatic table creation on first run
- User management (create/retrieve users)
- SQL injection protection through ORM

### Logging System
- Rotating log files in user home directory (~/.reservia/)
- Configurable log levels and backup count
- Structured logging with component prefixes
- Both file and console output

### Architecture
- Object-oriented design with class-based views
- Singleton database pattern
- Blueprint-based modular endpoint organization
- Configuration-driven application setup

## Usage

### Usage of Endpoints

Once the server is running, you can test the endpoints using curl from the console:

#### Home Page
```bash
curl http://localhost:5000/
```

#### Health Check
```bash
curl http://localhost:5000/info/is_alive
```
Expected response:
```json
{"status": "alive", "service": "Reservia"}
```

#### Version Information
```bash
curl http://localhost:5000/info/get_version
```
Expected response:
```json
{"version": "1.0.0"}
```

#### Add User (Admin)
```bash
curl --header "Content-Type: application/json" --request POST --data '{"name": "John Doe", "email": "john@example.com"}' http://localhost:5000/admin/user/add
```
Expected response:
```json
{"message": "User created successfully", "user_id": 1}
```

## Features In Development
- Resource management endpoints
- Request/booking system
- User authentication
- Frontend templates and forms