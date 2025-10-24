# Configuración global de pytest para Common App

import pytest
import os
import django
from django.conf import settings

# Configurar Django para testing sin Celery
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
def sample_audit_data():
    """Datos de prueba para auditoría"""
    return {
        "action": "CREATE",
        "model_name": "User",
        "object_id": "1",
        "user_id": "1",
        "ip_address": "127.0.0.1",
        "user_agent": "Test Agent",
    }


@pytest.fixture
def sample_request_data():
    """Datos de prueba para requests"""
    return {
        "method": "GET",
        "path": "/api/test/",
        "ip_address": "127.0.0.1",
        "user_agent": "Test Agent",
        "user_id": "1",
    }
