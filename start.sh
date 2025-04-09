#!/bin/sh
# Wait for database to be available
until python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')" 2>/dev/null; do
  sleep 1
done

# Run migrations and start app
flask db upgrade
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 --preload main:app
