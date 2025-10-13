#!/bin/bash

case "$1" in
    start)
        echo "Starting Reservia container..."
        docker compose up -d
        ;;
    stop)
        echo "Stopping Reservia container..."
        docker compose down
        ;;
    restart)
        echo "Restarting Reservia container..."
        docker compose restart
        ;;
    logs)
        docker compose logs -f
        ;;
    build)
        echo "Building Reservia container..."
        docker compose build
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|build}"
        exit 1
        ;;
esac