# Configuración global de pytest para Notifications App

import pytest
import os
import django
from django.conf import settings

# Configurar Django para testing
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.test_settings")

try:
    django.setup()
except Exception as e:
    print(f"Warning: Django setup failed: {e}")


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Configuración de base de datos para testing"""
    pass


@pytest.fixture
def sample_notification_data():
    """Datos de prueba para notificaciones"""
    return {
        "title": "Test Notification",
        "message": "This is a test notification",
        "notification_type": "INFO",
        "user_id": "1",
        "is_read": False,
    }


@pytest.fixture
def sample_user_data():
    """Datos de prueba para usuarios"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "testpass123",
    }


@pytest.fixture
def sample_email_data():
    """Datos de prueba para emails"""
    return {
        "to_email": "test@example.com",
        "subject": "Test Email",
        "message": "This is a test email",
        "template": "notification",
    }
