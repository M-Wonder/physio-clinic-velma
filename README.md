# PhysioClinic Management System

A full-stack physiotherapy clinic management system built with Django REST Framework + React, containerized with Docker.

## Features
- Service Catalog (7 physiotherapy specialties)
- Doctor Profiles with real-time availability
- Appointment Booking (concurrency-safe)
- Notifications via Celery (Email/SMS)
- Treatment Records with file attachments
- Role-Based Access Control (Patient/Doctor/Admin/Receptionist)
- Walk-in Patient Support
- HIPAA/GDPR Compliance

## Quick Start
```bash
cp .env.example .env
docker compose up --build
# Seed demo data:
docker compose exec backend python manage.py seed_data
```

- Frontend: http://localhost:3000
- API: http://localhost:8000/api/
- Docs: http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/

Default admin: admin@physio.clinic / Admin@12345
