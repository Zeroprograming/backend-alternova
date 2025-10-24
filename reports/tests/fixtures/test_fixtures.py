# Fixtures de prueba para Reports App

import pytest
from django.contrib.auth.models import User


@pytest.fixture
def test_user():
    """Usuario de prueba"""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def admin_user():
    """Usuario administrador de prueba"""
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User",
    )


@pytest.fixture
def sample_report():
    """Reporte de prueba"""
    return {
        "title": "Academic Report 2024",
        "description": "Comprehensive academic report for 2024",
        "report_type": "ACADEMIC",
        "status": "DRAFT",
        "created_by": "1",
        "data": {"students": 100, "subjects": 20},
    }


@pytest.fixture
def sample_reports():
    """Múltiples reportes de prueba"""
    reports = []
    for i in range(5):
        report = {
            "id": str(i + 1),
            "title": f"Report {i+1}",
            "description": f"Description for report {i+1}",
            "report_type": "ACADEMIC" if i % 2 == 0 else "FINANCIAL",
            "status": "DRAFT" if i % 2 == 0 else "COMPLETED",
            "created_by": str((i % 2) + 1),
            "data": {"students": 100 + i, "subjects": 20 + i},
        }
        reports.append(report)
    return reports


@pytest.fixture
def sample_csv_report():
    """Reporte CSV de prueba"""
    return {
        "title": "Students CSV Report",
        "description": "CSV report of all students",
        "report_type": "CSV",
        "status": "COMPLETED",
        "created_by": "1",
        "file_path": "/reports/students_2024.csv",
        "row_count": 100,
        "headers": ["ID", "Name", "Email", "Grade", "Status"],
    }


@pytest.fixture
def sample_csv_reports():
    """Múltiples reportes CSV de prueba"""
    csv_reports = []
    for i in range(3):
        csv_report = {
            "id": str(i + 1),
            "title": f"CSV Report {i+1}",
            "description": f"CSV description {i+1}",
            "report_type": "CSV",
            "status": "COMPLETED",
            "created_by": str((i % 2) + 1),
            "file_path": f"/reports/csv_report_{i+1}.csv",
            "row_count": 50 + (i * 25),
        }
        csv_reports.append(csv_report)
    return csv_reports


@pytest.fixture
def sample_report_filters():
    """Filtros de reporte de prueba"""
    return {
        "date_from": "2024-01-01",
        "date_to": "2024-12-31",
        "academic_year": 2024,
        "semester": "FIRST",
        "subject_id": "1",
        "student_id": "1",
        "report_type": "ACADEMIC",
    }


@pytest.fixture
def sample_report_metrics():
    """Métricas de reporte de prueba"""
    return {
        "total_students": 100,
        "total_subjects": 20,
        "total_enrollments": 500,
        "average_gpa": 3.5,
        "completion_rate": 85.5,
        "pass_rate": 90.0,
        "total_credits": 1200,
    }


@pytest.fixture
def sample_csv_data():
    """Datos CSV de prueba"""
    return {
        "headers": ["ID", "Name", "Email", "Grade", "Status"],
        "rows": [
            ["1", "John Doe", "john@example.com", "85", "ACTIVE"],
            ["2", "Jane Smith", "jane@example.com", "92", "ACTIVE"],
            ["3", "Bob Johnson", "bob@example.com", "78", "ACTIVE"],
            ["4", "Alice Brown", "alice@example.com", "88", "ACTIVE"],
            ["5", "Charlie Wilson", "charlie@example.com", "95", "ACTIVE"],
        ],
    }


@pytest.fixture
def sample_report_data():
    """Datos de reporte de prueba"""
    return {
        "students": [
            {"id": "1", "name": "John Doe", "email": "john@example.com", "gpa": 3.5},
            {"id": "2", "name": "Jane Smith", "email": "jane@example.com", "gpa": 3.8},
            {"id": "3", "name": "Bob Johnson", "email": "bob@example.com", "gpa": 3.2},
        ],
        "subjects": [
            {"id": "1", "name": "Mathematics", "credits": 3, "enrollments": 50},
            {"id": "2", "name": "Physics", "credits": 4, "enrollments": 30},
            {"id": "3", "name": "Chemistry", "credits": 3, "enrollments": 40},
        ],
        "metrics": {
            "total_students": 3,
            "total_subjects": 3,
            "total_enrollments": 120,
            "average_gpa": 3.5,
        },
    }


@pytest.fixture
def report_service_mock():
    """Mock del servicio de reportes"""
    from unittest.mock import Mock

    service = Mock()
    service.create_report.return_value = {"id": "1", "title": "Test Report"}
    service.get_report.return_value = {
        "id": "1",
        "title": "Test Report",
        "status": "DRAFT",
    }
    service.generate_report.return_value = {
        "status": "COMPLETED",
        "file_path": "/reports/test.csv",
    }
    service.update_report.return_value = True
    service.delete_report.return_value = True
    service.get_all_reports.return_value = []
    service.get_reports_by_type.return_value = []
    service.get_reports_by_status.return_value = []

    return service


@pytest.fixture
def csv_report_service_mock():
    """Mock del servicio de reportes CSV"""
    from unittest.mock import Mock

    service = Mock()
    service.generate_csv_report.return_value = {
        "status": "COMPLETED",
        "file_path": "/reports/test.csv",
        "row_count": 100,
    }
    service.export_to_csv.return_value = "/reports/export.csv"
    service.validate_csv_data.return_value = True
    service.parse_csv_data.return_value = {"headers": [], "rows": []}

    return service


@pytest.fixture
def report_request_data():
    """Datos de request para crear reporte"""
    return {
        "title": "Test Report",
        "description": "Test description",
        "report_type": "ACADEMIC",
        "filters": {
            "date_from": "2024-01-01",
            "date_to": "2024-12-31",
            "academic_year": 2024,
        },
    }


@pytest.fixture
def csv_report_request_data():
    """Datos de request para reporte CSV"""
    return {
        "title": "CSV Test Report",
        "description": "CSV test description",
        "report_type": "CSV",
        "filters": {
            "academic_year": 2024,
            "semester": "FIRST",
        },
        "format": "csv",
    }


@pytest.fixture
def report_response_data():
    """Datos de respuesta para reporte"""
    return {
        "id": "1",
        "title": "Test Report",
        "description": "Test description",
        "report_type": "ACADEMIC",
        "status": "DRAFT",
        "created_by": "1",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def csv_report_response_data():
    """Datos de respuesta para reporte CSV"""
    return {
        "id": "1",
        "title": "CSV Test Report",
        "description": "CSV test description",
        "report_type": "CSV",
        "status": "COMPLETED",
        "created_by": "1",
        "file_path": "/reports/test.csv",
        "row_count": 100,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }
