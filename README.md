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
```

- Frontend: http://localhost:3030
- API: http://localhost:8080/api/
- Docs: http://localhost:8080/api/docs/
- Admin: http://localhost:8080/admin/

## Local admin account
No admin account exists until you create one. Either:
- `docker compose exec backend python manage.py createsuperuser`, or
- set `DJANGO_SUPERUSER_EMAIL` and `DJANGO_SUPERUSER_PASSWORD` in `.env` before first boot
  (`entrypoint.sh` creates it automatically, and keeps that password in sync on restarts —
  don't set these in any shared or production `.env`).

## Demo data (local development only)
```bash
docker compose exec backend python manage.py seed_data
```
Creates demo doctor and patient accounts and prints a one-time password to the terminal.
Refuses to run unless `DEBUG=True`, so it can never touch a real deployment.
