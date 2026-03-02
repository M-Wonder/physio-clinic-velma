"""Services catalog models."""
from django.db import models


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Icon class or emoji')

    class Meta:
        db_table = 'services_category'
        verbose_name_plural = 'Service Categories'

    def __str__(self):
        return self.name


class Service(models.Model):
    """A physiotherapy service offered by the clinic."""
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='services')
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    conditions_treated = models.TextField(blank=True, help_text='Comma-separated list')
    treatment_methods = models.TextField(blank=True)
    session_duration_minutes = models.PositiveIntegerField(default=60)
    price_per_session = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    icon = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='services/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0, help_text='Display order')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'services_service'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name
