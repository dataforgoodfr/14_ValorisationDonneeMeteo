#!/bin/bash
# Script to load mock data into TimescaleDB
# This script is meant to be run from inside the Docker container

set -e

echo "🔄 Waiting for PostgreSQL to be ready..."

# Wait for PostgreSQL to be ready (use socket, not TCP, during init)
until pg_isready -U infoclimat -d meteodb > /dev/null 2>&1; do
    echo "⏳ Waiting for database..."
    sleep 2
done

echo "✓ Database is ready!"

# Initialize schema
echo "📋 Initializing schema..."
psql -U infoclimat -d meteodb -f /docker-entrypoint-initdb.d/init-schema.sql

# Note: The Python script should be run from outside the container
# using: uv run docker/generate-mock-data.py

echo "✓ Schema initialization complete!"
echo ""
echo "Next step: Run 'uv run docker/generate-mock-data.py' from the host to populate data"
