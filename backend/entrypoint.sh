#!/bin/bash
set -e

echo "========================================="
echo "  PhysioClinic Backend Starting Up"
echo "========================================="

# Use PORT environment variable provided by Render (default to 8080 if not set)
PORT=${PORT:-8080}
echo "Using port: $PORT"

# Check if we're on Render (they provide RENDER_INSTANCE_ID)
if [ -n "$RENDER_INSTANCE_ID" ]; then
    echo "Running on Render - skipping database wait (managed service)"
else
    echo "Waiting for database at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
    until python -c "
import psycopg2, os, sys, time
try:
    psycopg2.connect(
        host=os.environ['POSTGRES_HOST'],
        port=os.environ.get('POSTGRES_PORT', 5432),
        dbname=os.environ['POSTGRES_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD'],
        connect_timeout=3
    )
    sys.exit(0)
except Exception as e:
    print(f'Database not ready: {e}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null; do
        echo "  Database not ready — retrying in 2s..."
        sleep 2
    done
    echo "Database ready."
fi

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear 2>&1 | tail -5

# Create superuser only if environment variables are set (safer approach)
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating/updating superuser..."
    python manage.py shell << EOF
from django.contrib.auth import get_user_model
import os
User = get_user_model()
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@physio.clinic')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
first_name = os.environ.get('DJANGO_SUPERUSER_FIRST_NAME', 'Admin')
last_name = os.environ.get('DJANGO_SUPERUSER_LAST_NAME', 'User')

if password:
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        user.set_password(password)
        user.save()
        print(f"  Superuser created: {email}")
    else:
        # Update existing superuser password if needed
        user.set_password(password)
        user.save()
        print(f"  Superuser password updated: {email}")
else:
    print("  DJANGO_SUPERUSER_PASSWORD not set, skipping superuser creation")
EOF
else
    echo "  Superuser environment variables not set, skipping superuser creation"
fi

# Start Gunicorn with the PORT from Render
echo "Starting Gunicorn on port $PORT..."
exec gunicorn physio_clinic.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    --log-level info