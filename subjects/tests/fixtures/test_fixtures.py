# Fixtures de prueba para Subjects App

import pytest
from django.contrib.auth.models import User


@pytest.fixture
def test_student():
    """Estudiante de prueba"""
    return User.objects.create_user(
        username="student",
        email="student@example.com",
        password="studentpass123",
        first_name="Student",
        last_name="User",
    )


@pytest.fixture
def test_teacher():
    """Profesor de prueba"""
    return User.objects.create_user(
        username="teacher",
        email="teacher@example.com",
        password="teacherpass123",
        first_name="Teacher",
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
def sample_subject():
    """Materia de prueba"""
    return {
        "code": "MATH101",
        "name": "Mathematics I",
        "description": "Basic mathematics course",
        "credits": 3,
        "semester": "FIRST",
        "academic_year": 2024,
        "is_active": True,
        "teacher_id": "1",
    }


@pytest.fixture
def sample_subjects():
    """Múltiples materias de prueba"""
    subjects = []
    for i in range(5):
        subject = {
            "id": str(i + 1),
            "code": f"SUB{i+1:03d}",
            "name": f"Subject {i+1}",
            "description": f"Description for subject {i+1}",
            "credits": (i % 3) + 1,
            "semester": "FIRST" if i % 2 == 0 else "SECOND",
            "academic_year": 2024,
            "is_active": True,
            "teacher_id": str((i % 2) + 1),
        }
        subjects.append(subject)
    return subjects


@pytest.fixture
def sample_enrollment():
    """Inscripción de prueba"""
    return {
        "student_id": "1",
        "subject_id": "1",
        "enrollment_date": "2024-01-01",
        "status": "ACTIVE",
        "grade": None,
        "credits": 3,
    }


@pytest.fixture
def sample_enrollments():
    """Múltiples inscripciones de prueba"""
    enrollments = []
    for i in range(5):
        enrollment = {
            "id": str(i + 1),
            "student_id": str((i % 2) + 1),
            "subject_id": str((i % 3) + 1),
            "enrollment_date": "2024-01-01",
            "status": "ACTIVE" if i % 2 == 0 else "COMPLETED",
            "grade": 85 if i % 2 == 1 else None,
            "credits": 3,
        }
        enrollments.append(enrollment)
    return enrollments


@pytest.fixture
def sample_prerequisite():
    """Prerrequisito de prueba"""
    return {
        "subject_id": "1",
        "prerequisite_id": "2",
        "is_mandatory": True,
        "description": "Must complete prerequisite before enrollment",
    }


@pytest.fixture
def sample_prerequisites():
    """Múltiples prerrequisitos de prueba"""
    prerequisites = []
    for i in range(3):
        prerequisite = {
            "id": str(i + 1),
            "subject_id": str(i + 1),
            "prerequisite_id": str(i + 2),
            "is_mandatory": i % 2 == 0,
            "description": f"Prerequisite {i+1}",
        }
        prerequisites.append(prerequisite)
    return prerequisites


@pytest.fixture
def sample_academic_info():
    """Información académica de prueba"""
    return {
        "student_id": "1",
        "academic_year": 2024,
        "semester": "FIRST",
        "credits_required": 120,
        "credits_completed": 60,
        "credits_enrolled": 15,
        "gpa": 3.5,
        "status": "ACTIVE",
    }


@pytest.fixture
def sample_grade():
    """Calificación de prueba"""
    return {
        "enrollment_id": "1",
        "student_id": "1",
        "subject_id": "1",
        "grade": 85,
        "grade_letter": "B",
        "is_passing": True,
        "graded_date": "2024-06-01",
    }


@pytest.fixture
def sample_grades():
    """Múltiples calificaciones de prueba"""
    grades = []
    for i in range(5):
        grade = {
            "id": str(i + 1),
            "enrollment_id": str(i + 1),
            "student_id": str((i % 2) + 1),
            "subject_id": str((i % 3) + 1),
            "grade": 70 + (i * 5),
            "grade_letter": "A" if i > 2 else "B" if i > 1 else "C",
            "is_passing": True,
            "graded_date": "2024-06-01",
        }
        grades.append(grade)
    return grades


@pytest.fixture
def subject_service_mock():
    """Mock del servicio de materias"""
    from unittest.mock import Mock

    service = Mock()
    service.create_subject.return_value = {"id": "1", "code": "MATH101"}
    service.get_subject.return_value = {
        "id": "1",
        "code": "MATH101",
        "name": "Mathematics I",
    }
    service.update_subject.return_value = True
    service.delete_subject.return_value = True
    service.get_all_subjects.return_value = []
    service.get_subjects_by_semester.return_value = []
    service.get_subjects_by_teacher.return_value = []

    return service


@pytest.fixture
def enrollment_service_mock():
    """Mock del servicio de inscripciones"""
    from unittest.mock import Mock

    service = Mock()
    service.enroll_student.return_value = {"id": "1", "status": "ACTIVE"}
    service.get_student_enrollments.return_value = []
    service.get_subject_enrollments.return_value = []
    service.update_grade.return_value = True
    service.drop_enrollment.return_value = True
    service.check_prerequisites.return_value = True

    return service


@pytest.fixture
def academic_service_mock():
    """Mock del servicio académico"""
    from unittest.mock import Mock

    service = Mock()
    service.get_student_academic_info.return_value = {}
    service.calculate_gpa.return_value = 3.5
    service.get_graduation_requirements.return_value = {}
    service.check_graduation_eligibility.return_value = True

    return service


@pytest.fixture
def subject_request_data():
    """Datos de request para crear materia"""
    return {
        "code": "MATH101",
        "name": "Mathematics I",
        "description": "Basic mathematics course",
        "credits": 3,
        "semester": "FIRST",
        "academic_year": 2024,
        "teacher_id": "1",
    }


@pytest.fixture
def enrollment_request_data():
    """Datos de request para inscripción"""
    return {
        "student_id": "1",
        "subject_id": "1",
        "enrollment_date": "2024-01-01",
    }


@pytest.fixture
def grade_request_data():
    """Datos de request para calificación"""
    return {
        "enrollment_id": "1",
        "grade": 85,
        "graded_date": "2024-06-01",
    }


@pytest.fixture
def subject_response_data():
    """Datos de respuesta para materia"""
    return {
        "id": "1",
        "code": "MATH101",
        "name": "Mathematics I",
        "description": "Basic mathematics course",
        "credits": 3,
        "semester": "FIRST",
        "academic_year": 2024,
        "is_active": True,
        "teacher_id": "1",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def enrollment_response_data():
    """Datos de respuesta para inscripción"""
    return {
        "id": "1",
        "student_id": "1",
        "subject_id": "1",
        "enrollment_date": "2024-01-01",
        "status": "ACTIVE",
        "grade": None,
        "credits": 3,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }
