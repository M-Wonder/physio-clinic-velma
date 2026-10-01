import django.contrib.postgres.operations
from django.db import migrations, models


def backfill_start_end_at(apps, schema_editor):
    Appointment = apps.get_model('appointments', 'Appointment')
    from django.utils import timezone as tz
    for appt in Appointment.objects.all().iterator():
        appt.start_at = tz.make_aware(tz.datetime.combine(appt.appointment_date, appt.start_time))
        appt.end_at = tz.make_aware(tz.datetime.combine(appt.appointment_date, appt.end_time))
        appt.save(update_fields=['start_at', 'end_at'])


class Migration(migrations.Migration):

    dependencies = [('appointments', '0001_initial')]

    operations = [
        django.contrib.postgres.operations.BtreeGistExtension(),
        migrations.AddField('appointment', 'start_at', models.DateTimeField(null=True, editable=False)),
        migrations.AddField('appointment', 'end_at', models.DateTimeField(null=True, editable=False)),
        migrations.RunPython(backfill_start_end_at, migrations.RunPython.noop),
        migrations.AlterField('appointment', 'start_at', models.DateTimeField(editable=False)),
        migrations.AlterField('appointment', 'end_at', models.DateTimeField(editable=False)),
        migrations.RunSQL(
            sql="""
                ALTER TABLE appointments_appointment
                ADD CONSTRAINT no_overlapping_appointments
                EXCLUDE USING gist (
                    doctor_id WITH =,
                    tstzrange(start_at, end_at, '[)') WITH &&
                )
                WHERE (status IN ('scheduled', 'confirmed', 'in_progress'));
            """,
            reverse_sql="ALTER TABLE appointments_appointment DROP CONSTRAINT no_overlapping_appointments;",
        ),
    ]
