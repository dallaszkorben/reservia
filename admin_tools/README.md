# Reservia Administration Tools

This directory contains Python scripts for administering the Reservia database directly.

## Usage

Run scripts from the `admin_tools` directory:

```bash
cd admin_tools
python3 <script_name>.py [arguments]
```

## Available Tools

### User Management
- **`check_users.py`** - List all users with their roles
- **`create_admin_user.py`** - Create default admin user (admin/admin)
- **`create_super_user.py`** - Create default super user (super/super)
- **`create_user.py`** - Create custom user
  ```bash
  python3 create_user.py <name> <email> <password> <role>
  # Example: python3 create_user.py john john@example.com mypass user
  ```
- **`delete_user.py`** - Delete user (only if no active reservations)
  ```bash
  python3 delete_user.py <username>
  ```

### Resource Management
- **`check_resources.py`** - List all resources
- **`create_resource.py`** - Create new resource
  ```bash
  python3 create_resource.py <name> [comment]
  # Example: python3 create_resource.py "Meeting Room A" "10 person capacity"
  ```

### Reservation Management
- **`check_reservations.py`** - List all reservations with status and timestamps

## Notes

- All scripts connect to `../data/reservia.db`
- Scripts require the Reservia backend modules to be available
- User roles: `user`, `admin`, `super`
- Admin and super users have the same privileges currently