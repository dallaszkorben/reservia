# Docker Setup for Reservia

## Quick Start

### Using Docker Compose (Recommended)

The `docker-compose.yml` file defines the service configuration including volume mounting and port mapping.

1. **Build and start the container:**
   ```bash
   docker compose up -d
   ```

2. **Access the application:**
   - Open http://localhost:5000
   - Default login: Username: `admin`, Password: `admin`

3. **Stop the container:**
   ```bash
   docker compose down
   ```

4. **Restart the container:**
   ```bash
   docker compose restart
   ```

5. **View logs:**
   ```bash
   docker compose logs -f
   ```

### Using Management Script

The `docker-run.sh` script is a wrapper around `docker compose` commands for convenience:

```bash
# Start container (uses docker compose up -d)
./docker-run.sh start

# Stop container (uses docker compose down)
./docker-run.sh stop

# Restart container (uses docker compose restart)
./docker-run.sh restart

# View logs (uses docker compose logs -f)
./docker-run.sh logs

# Rebuild container (uses docker compose build)
./docker-run.sh build
```

### Additional Docker Compose Commands

```bash
# Build without starting
docker compose build

# Start in foreground (see logs directly)
docker compose up

# Check container status
docker compose ps

# Remove containers and networks
docker compose down --volumes
```

## File Overview

- **`Dockerfile`** - Defines how to build the container image
- **`docker-compose.yml`** - Defines the service configuration (ports, volumes, environment)
- **`docker-run.sh`** - Convenience script that wraps docker compose commands
- **`.dockerignore`** - Excludes files from the Docker build context

## Data Persistence

The `data/` directory is mounted as a volume, ensuring:
- Database (`reservia.db`) persists between container restarts
- Log files are preserved
- Data survives container recreation

## Environment Variables

- `FLASK_ENV=production` - Disables debug mode for production use

## Troubleshooting

- **Port already in use:** Change port mapping in `docker-compose.yml` from `5000:5000` to `8080:5000`
- **Permission issues:** Ensure `data/` directory has proper permissions
- **Container won't start:** Check logs with `docker compose logs`