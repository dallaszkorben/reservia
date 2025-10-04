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
├── docs/                # General documentation
├── amazonq-context/     # Amazon Q session context files
│   ├── backend_context.md   # Backend architecture and setup
│   └── frontend_context.md  # Frontend architecture and components
├── app.py              # Main Flask application entry point
├── requirements.txt    # Python dependencies
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

### Passwords Table
- `id` (INTEGER, Primary Key, Auto-increment)
- `user_id` (INTEGER, Foreign Key → Users.id)
- `password_hash` (TEXT, NOT NULL) - SHA-256 hashed password

### ReservationLifecycle Table
- `id` (INTEGER, Primary Key, Auto-increment)
- `user_id` (INTEGER, Foreign Key → Users.id)
- `resource_id` (INTEGER, Foreign Key → Resources.id)
- `request_date` (INTEGER, NOT NULL) - Unix timestamp
- `approved_date` (INTEGER, NULL) - Unix timestamp
- `cancelled_date` (INTEGER, NULL) - Unix timestamp
- `released_date` (INTEGER, NULL) - Unix timestamp

## Current Features

### API Endpoints
- **GET /** - Main application page
- **GET /info/is_alive** - Health check endpoint
- **GET /info/get_version** - Application version information
- **POST /session/login** - User login (requires JSON payload)
- **POST /session/logout** - User logout
- **POST /admin/user/add** - Add new user (requires admin login and JSON payload)
- **POST /admin/resource/add** - Add new resource (requires admin login and JSON payload)
- **POST /reservation/request** - Request resource reservation (requires user login)
- **GET /reservation/active** - Get all active reservations (requires user login)
- **POST /reservation/cancel** - Cancel user's reservation (requires user login)
- **POST /reservation/release** - Release approved reservation (requires user login)

### Database Management
- SQLite database with SQLAlchemy ORM
- Automatic table creation on first run
- User management (create/retrieve users)
- Resource management (create/retrieve resources)
- Reservation lifecycle management with queue system
- SQL injection protection through ORM
- Structured error handling with specific error codes

### Logging System
- Rotating log files in user home directory (~/.reservia/)
- Configurable log levels and backup count
- Structured logging with component prefixes
- Both file and console output

### Backend Architecture
- Object-oriented design with class-based views
- Singleton database pattern
- Blueprint-based modular endpoint organization
- Configuration-driven application setup
- Reservation queue system with auto-approval logic
- Thread-safe database operations with locking
- Google Style documentation standards

### Frontend Architecture
- **LayoutManager**: Static utility class for responsive grid positioning calculations
- **ResourcePool**: Singleton managing resource collection and layout updates
- **Resource**: Pure data model with user management and configurable font sizes
- **ResourceView**: DOM rendering and event handling with proper separation of concerns
- Clean separation between data models and view components
- Independent Resource class with static configuration
- Dependency injection for view components

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

#### User Login (Save Session Cookie)
```bash
curl -H "Content-Type: application/json" -X POST -c cookies.txt -d '{"name": "admin", "password": "admin"}' http://localhost:5000/session/login
```
Expected response:
```json
{"message": "Login successful", "user_name": "admin"}
```
**Note**: The `-c cookies.txt` saves the session cookie to a file for subsequent requests.

#### User Logout (Use Session Cookie)
```bash
curl -X POST -b cookies.txt http://localhost:5000/session/logout
```
Expected response:
```json
{"message": "Logout successful"}
```

#### Add User (Admin Only - Requires Session Cookie)
```bash
curl -H "Content-Type: application/json" -X POST -b cookies.txt -d '{"name": "John Doe", "email": "john@example.com", "password": "password123"}' http://localhost:5000/admin/user/add
```
Expected response:
```json
{"message": "User created successfully", "user_id": 2}
```

#### Add Resource (Admin Only - Requires Session Cookie)
```bash
curl -H "Content-Type: application/json" -X POST -b cookies.txt -d '{"name": "Meeting Room", "comment": "Conference room for 10 people"}' http://localhost:5000/admin/resource/add
```
Expected response:
```json
{"message": "Resource created successfully", "resource_id": 1}
```

#### Request Reservation (User Login Required)
```bash
curl -H "Content-Type: application/json" -X POST -b cookies.txt -d '{"resource_id": 1}' http://localhost:5000/reservation/request
```
Expected response:
```json
{"message": "Reservation request successful", "reservation_id": 1, "resource_id": 1, "status": "approved"}
```

#### Get Active Reservations (User Login Required)
```bash
curl -H "Content-Type: application/json" -X GET -b cookies.txt http://localhost:5000/reservation/active
```
Expected response:
```json
{"message": "Active reservations retrieved successfully", "reservations": [...], "count": 2}
```

#### Cancel Reservation (User Login Required)
```bash
curl -H "Content-Type: application/json" -X POST -b cookies.txt -d '{"resource_id": 1}' http://localhost:5000/reservation/cancel
```
Expected response:
```json
{"message": "Reservation cancelled successfully", "reservation_id": 1, "resource_id": 1, "cancelled_date": "2023-12-21T10:45:30+01:00"}
```

#### Release Reservation (User Login Required)
```bash
curl -H "Content-Type: application/json" -X POST -b cookies.txt -d '{"resource_id": 1}' http://localhost:5000/reservation/release
```
Expected response:
```json
{"message": "Reservation released successfully", "reservation_id": 1, "resource_id": 1, "released_date": "2023-12-21T11:00:15+01:00"}
```

### Session Management Workflow
1. **Login**: Use `-c cookies.txt` to save session cookie
2. **Authenticated requests**: Use `-b cookies.txt` to send session cookie
3. **Logout**: Use `-b cookies.txt -c cookies.txt` to properly clear session cookie

**Note**: The logout endpoint properly invalidates the session cookie. After logout, subsequent requests to admin endpoints will fail with authentication errors.

## Reservation System Features

### Queue Management
- Multiple users can request the same resource
- First user gets auto-approved if resource is available
- Subsequent users are queued (request_date set, approved_date null)
- When approved user releases resource, next queued user is auto-approved

### Resource Status Logic
- **Available**: No active reservations or last reservation has released_date
- **Occupied**: Last non-cancelled reservation has no released_date
- **Queued**: Multiple users waiting for resource availability

### Error Handling
- Structured database responses with specific error codes
- Proper HTTP status codes (401, 403, 404, 409)
- Comprehensive logging with user and resource details

### Frontend Features
- **Responsive Resource Grid**: Automatic layout calculation based on screen width
- **Scrollable User Lists**: Apple-styled blue scrollbars with overflow handling
- **Interactive Resource Management**: Click handling for both resources and individual users
- **Customizable Font Sizes**: Per-resource user list font size configuration
- **Real-time Layout Updates**: Window resize support with automatic repositioning
- **Event System**: Separate event handlers for resource selection and user selection

### User Interface Components
- **Resource Rectangles**: 200x400px containers with titles and user lists
- **User List Items**: Scrollable containers with customizable font sizes (default 20px)
- **Apple Design System**: Blue gradient themes and glass effects
- **Responsive Layout**: Centered grid with proper spacing and gaps

### Event Handling
- **Resource Click**: Triggers `ResourcePool.onResourceSelected(resource_id)`
- **User Click**: Triggers `Resource.onUserSelected(user_id, user_name)`
- **Proper Event Separation**: No event bubbling conflicts between resource and user clicks

## Features In Development
- Enhanced resource management
- User dashboard and reservation history
- Backend integration for frontend components