# Configuración global de pytest para Reports App

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
def sample_report_data():
    """Datos de prueba para reportes"""
    return {
        "title": "Academic Report 2024",
        "description": "Comprehensive academic report for 2024",
        "report_type": "ACADEMIC",
        "status": "DRAFT",
        "created_by": "1",
        "data": {"students": 100, "subjects": 20},
    }


@pytest.fixture
def sample_csv_report_data():
    """Datos de prueba para reportes CSV"""
    return {
        "title": "Students CSV Report",
        "description": "CSV report of all students",
        "report_type": "CSV",
        "status": "COMPLETED",
        "created_by": "1",
        "file_path": "/reports/students_2024.csv",
        "row_count": 100,
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
        "role": "ADMIN",
    }


@pytest.fixture
def sample_report_filters():
    """Filtros de prueba para reportes"""
    return {
        "date_from": "2024-01-01",
        "date_to": "2024-12-31",
        "academic_year": 2024,
        "semester": "FIRST",
        "subject_id": "1",
        "student_id": "1",
    }


@pytest.fixture
def sample_report_metrics():
    """Métricas de prueba para reportes"""
    return {
        "total_students": 100,
        "total_subjects": 20,
        "total_enrollments": 500,
        "average_gpa": 3.5,
        "completion_rate": 85.5,
    }
