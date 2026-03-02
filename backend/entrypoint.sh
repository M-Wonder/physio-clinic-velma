#!/bin/bash
set -e

echo "========================================="
echo "  PhysioClinic Backend Starting Up"
echo "========================================="

echo "Waiting for database at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
until python -c "
import psycopg2, os, sys
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
except Exception:
    sys.exit(1)
" 2>/dev/null; do
    echo "  Database not ready — retrying in 2s..."
    sleep 2
done
echo "Database ready."

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear 2>&1 | tail -3

python manage.py shell << 'PYEOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@physio.clinic').exists():
    User.objects.create_superuser(
        email='admin@physio.clinic',
        password='Admin@12345',
        first_name='System',
        last_name='Admin',
        role='admin',
    )
    print("  Superuser created: admin@physio.clinic / Admin@12345")
else:
    print("  Superuser already exists.")
PYEOF

echo "Starting Gunicorn on port 8080..."
exec gunicorn physio_clinic.wsgi:application \
    --bind 0.0.0.0:8080 \
    --workers 4 \
    --threads 2 \
    --timeout 60 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile -