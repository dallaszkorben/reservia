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

✅ **Phase 5 Complete**: Resource Management
- `/admin/resource/modify` - Admin-only resource modification endpoint
- `/admin/user/modify` - Admin and self-user modification endpoint
- Complete CRUD operations for resources and users
- Proper authorization checks (admin-only vs self-modification)
- Comprehensive test coverage for all modification endpoints

✅ **Phase 6 Complete**: Reservation Expiration & Keep-Alive System
- Database schema enhancement: `valid_until_date` field in reservation_lifecycle table
- Centralized configuration system with `approved_keep_alive_sec` (600s default)
- `/reservation/keep_alive` endpoint for extending approved reservations
- Automatic reservation expiration with background thread monitoring
- Application-level thread management (moved from Database to ReserviaApp class)
- Real-time countdown display in frontend with dual-timer system
- Authentication refactoring: moved from database to endpoint level
- Comprehensive test coverage for keep-alive functionality

✅ **Phase 7 Complete**: Hover Action Interface
- Icon-based user actions: ❌ (Release/Cancel) and ⏰ (Keep Alive)
- Multi-line user item layout: name and countdown on separate lines
- Hover-only action visibility for logged-in user's reservations
- Disabled simple click actions to prevent accidental operations
- Transparent action button backgrounds for subtle UI integration
- Enhanced user experience with intentional action requirements

✅ **Phase 8 Complete**: Configurable Requested Reservation Expiration
- Added `requested_keep_alive_sec` configuration option (default: 1800 seconds)
- **Option 1**: When `requested_keep_alive_sec > 0` - requested reservations show countdown and auto-expire
- **Option 2**: When `requested_keep_alive_sec = 0` or `None` - requested reservations have no expiration
- Database schema updated: `valid_until_date` changed to nullable with automatic migration
- Frontend conditional display: countdown/keep-alive only when `valid_until_date` is not null
- Background expiration thread handles both approved and requested reservations
- Keep-alive endpoint supports both approved and requested reservations with appropriate timeouts

## Implemented Features
- `/info/is_alive` - Health check endpoint
- `/info/get_version` - Version information endpoint
- `/session/login` - User authentication with session creation
- `/session/logout` - Session termination with cookie invalidation
- `/session/status` - Check current session status
- `/admin/user/add` - Admin-only user creation
- `/admin/user/modify` - Admin can modify any user, user can modify self
- `/admin/resource/add` - Admin-only resource creation
- `/admin/resource/modify` - Admin-only resource modification
- `/info/resources` - Get all resources
- `/reservation/request` - Create reservation requests with auto-approval
- `/reservation/active` - Get all active reservations
- `/reservation/cancel` - Cancel user's reservation request
- `/reservation/release` - Release approved reservation
- `/reservation/keep_alive` - Extend approved reservation validity
- Database singleton with ORM protection against SQL injection
- Secure password hashing and validation
- Flask session management with proper logout handling
- Rotating log files in user home directory (~/.reservia/)
- Configuration-driven logging levels and file management
- Reservation queue system with automatic resource management
- Structured error handling with specific HTTP status codes
- Automatic reservation expiration system with configurable timeouts
- Background thread monitoring for expired reservations
- Keep-alive functionality for extending reservation validity
- Application-level thread management with proper shutdown handling

## Next Steps
- Frontend templates and forms
- Enhanced resource management features
- User dashboard and reservation history

## Important Notes
- Always follow step-by-step approach
- Do not jump ahead in implementation
- Keep code minimal and focused
- Update this file after each development phase