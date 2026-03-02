from django.urls import path
from physio_clinic.apps.notifications import views

urlpatterns = [
    path('preferences/', views.NotificationPreferencesView.as_view(), name='notification-prefs'),
    path('logs/', views.NotificationLogListView.as_view(), name='notification-logs'),
]
