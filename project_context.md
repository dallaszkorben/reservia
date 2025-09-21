# Project Context for Amazon Q Sessions

## Project Overview
**Project Name**: Reservia - Resource Reservation Management System

**Description**: A Flask-based web application for managing and administering reservation requests for a given public resource. It allows users to request, book, and track availability, while providing administrators with tools to oversee and coordinate the usage of that resource.

## Technology Stack
- **Backend Framework**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML templates served by Flask
- **Web Server**: Apache2 (production deployment)

## Project Architecture
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
└── README.md           # GitHub documentation
```

## Development Approach
- **Step-by-step development** - Only implement what is explicitly requested
- **Minimal code approach** - Write only essential code for each requirement
- **GitHub ready** - Project structured for version control

## Current Status
✅ **Phase 1 Complete**: Initial project structure created
- Separated backend (Python) from frontend (HTML/JS/CSS)
- Created Flask blueprint architecture
- Added info view with /info/is_alive endpoint
- Added README.md for GitHub with running instructions
- Added project_context.md for Amazon Q sessions
- Basic requirements.txt with Flask dependencies

## Next Steps
(To be updated as development progresses)

## Important Notes
- Always follow step-by-step approach
- Do not jump ahead in implementation
- Keep code minimal and focused
- Update this file after each development phase