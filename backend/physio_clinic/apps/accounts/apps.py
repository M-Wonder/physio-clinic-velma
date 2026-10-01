from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'physio_clinic.apps.accounts'
    label = 'accounts'

    def ready(self):
        from django.conf import settings
        if not settings.DEBUG:
            # Fail fast at process boot, not on the first patient save mid-request.
            from physio_clinic.apps.accounts.encryption import get_fernet
            get_fernet()  # raises ImproperlyConfigured immediately if ENCRYPTION_KEY is missing
