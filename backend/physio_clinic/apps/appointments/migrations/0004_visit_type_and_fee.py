from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0003_alter_appointment_end_at_alter_appointment_start_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='visit_type',
            field=models.CharField(choices=[('clinic', 'At the clinic'), ('home', 'Home visit')],
                                   default='clinic', max_length=10),
        ),
        migrations.AddField(
            model_name='appointment',
            name='home_address',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='fee_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
