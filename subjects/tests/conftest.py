# Configuración global de pytest para Subjects App

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
def sample_subject_data():
    """Datos de prueba para materias"""
    return {
        "code": "MATH101",
        "name": "Mathematics I",
        "description": "Basic mathematics course",
        "credits": 3,
        "semester": "FIRST",
        "academic_year": 2024,
        "is_active": True,
    }


@pytest.fixture
def sample_enrollment_data():
    """Datos de prueba para inscripciones"""
    return {
        "student_id": "1",
        "subject_id": "1",
        "enrollment_date": "2024-01-01",
        "status": "ACTIVE",
        "grade": None,
    }


@pytest.fixture
def sample_prerequisite_data():
    """Datos de prueba para prerrequisitos"""
    return {
        "subject_id": "1",
        "prerequisite_id": "2",
        "is_mandatory": True,
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
        "role": "STUDENT",
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
        "role": "TEACHER",
    }


@pytest.fixture
def sample_academic_data():
    """Datos de prueba para información académica"""
    return {
        "academic_year": 2024,
        "semester": "FIRST",
        "credits_required": 120,
        "credits_completed": 60,
        "gpa": 3.5,
    }
