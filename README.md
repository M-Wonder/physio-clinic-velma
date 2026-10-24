# Neuromotion Physiotherapy Clinic — Booking & Records

Online booking and patient records for Neuromotion Physiotherapy Clinic, Nairobi. Django REST Framework + React, containerised with Docker.

*Move Better. Feel Better.*

## Features
- Service catalogue: Musculoskeletal, Neurological, Women's Health, Rehabilitation & Recovery, Hands-On & Soft Tissue, Home Physiotherapy
- Clinic sessions and home visits, with rates in KES (set in `.env`)
- Therapist profiles with real-time availability
- Appointment Booking (concurrency-safe)
- Notifications via Celery (Email/SMS)
- Treatment Records with file attachments
- Role-Based Access Control (Patient/Doctor/Admin/Receptionist)
- Walk-in Patient Support
- Patient health fields encrypted at rest; role-based access

## Quick Start
```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:3030
- API: http://localhost:8080/api/
- Docs: http://localhost:8080/api/docs/
- Admin: http://localhost:8080/admin/

## Clinic details
Name, phone, WhatsApp, email, address and rates come from environment variables (`CLINIC_*`, see `.env.example`) and are served at `/api/clinic/`, so the website and emails always agree. Blank values are hidden. **Set the real phone/WhatsApp/address before launch.**

The six services load automatically on `migrate`; edit them any time in Django admin.

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
