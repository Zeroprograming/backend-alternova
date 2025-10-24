# Configuración global de pytest para Users App

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
        "phone_number": "+1234567890",
        "role": "STUDENT",
    }


@pytest.fixture
def sample_admin_data():
    """Datos de prueba para administradores"""
    return {
        "username": "admin",
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "password": "adminpass123",
        "phone_number": "+1234567891",
        "role": "ADMIN",
    }


@pytest.fixture
def sample_teacher_data():
    """Datos de prueba para profesores"""
    return {
        "username": "teacher",
        "email": "teacher@example.com",
        "first_name": "Teacher",
        "last_name": "User",
        "password": "teacherpass123",
        "phone_number": "+1234567892",
        "role": "TEACHER",
    }


@pytest.fixture
def sample_auth_data():
    """Datos de prueba para autenticación"""
    return {
        "username": "testuser",
        "password": "testpass123",
        "email": "test@example.com",
    }


@pytest.fixture
def sample_role_data():
    """Datos de prueba para roles"""
    return {
        "role": "STUDENT",
        "permissions": ["read_profile", "update_profile"],
    }


@pytest.fixture
def sample_permission_data():
    """Datos de prueba para permisos"""
    return {
        "permission": "manage_users",
        "description": "Can manage user accounts",
    }
