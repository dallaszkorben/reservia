# Backend Context for Amazon Q

> This document provides complete backend architecture context for Amazon Q to reproduce the project from scratch.

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
✅ **Phase 1 Complete**: Project Foundation
- Separated backend (Python) from frontend (HTML/JS/CSS)
- Object-oriented Flask architecture with class-based views
- Blueprint managers for modular endpoint organization
- Proper singleton Database class with SQLAlchemy ORM
- Global configuration management
- Comprehensive logging system with rotating file handler
- Global constants for maintainable log prefixes

✅ **Phase 2 Complete**: Core Infrastructure
- Database schema: Users, Resources, ReservationLifecycle tables
- SQLite database with automatic table creation
- User management: create_user() and get_users() methods
- INFO level logging for endpoint access tracking
- Test framework for database operations
- Apache-ready WSGI configuration

✅ **Phase 3 Complete**: Authentication & Session Management
- User login/logout with secure password hashing (SHA256)
- Flask session management with proper cookie handling
- Session validation for admin endpoints
- Proper session invalidation on logout (cookie expiration)
- Admin-only user and resource creation endpoints
- Default admin user creation (admin/admin)

✅ **Phase 4 Complete**: Reservation System
- Complete reservation lifecycle: request → approve → release/cancel
- Queue system for multiple users requesting same resource
- Auto-approval for available resources
- Auto-approval of next queued user when resource is released
- Structured database method returns with error codes
- Comprehensive Google Style documentation
- Full reservation management endpoints

## Implemented Features
- `/info/is_alive` - Health check endpoint
- `/info/get_version` - Version information endpoint
- `/session/login` - User authentication with session creation
- `/session/logout` - Session termination with cookie invalidation
- `/admin/user/add` - Admin-only user creation
- `/admin/resource/add` - Resource creation
- `/reservation/request` - Create reservation requests with auto-approval
- `/reservation/active` - Get all active reservations
- `/reservation/cancel` - Cancel user's reservation request
- `/reservation/release` - Release approved reservation
- Database singleton with ORM protection against SQL injection
- Secure password hashing and validation
- Flask session management with proper logout handling
- Rotating log files in user home directory (~/.reservia/)
- Configuration-driven logging levels and file management
- Reservation queue system with automatic resource management
- Structured error handling with specific HTTP status codes

## Next Steps
- Frontend templates and forms
- Enhanced resource management features
- User dashboard and reservation history

## Important Notes
- Always follow step-by-step approach
- Do not jump ahead in implementation
- Keep code minimal and focused
- Update this file after each development phase