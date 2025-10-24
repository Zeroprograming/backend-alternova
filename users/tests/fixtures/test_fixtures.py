# Fixtures de prueba para Users App

import pytest
from django.contrib.auth.models import User
from users.infrastructure.models import User as UserModel, UserProfile


@pytest.fixture
def test_user():
    """Usuario de prueba"""
    return UserModel.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def admin_user():
    """Usuario administrador de prueba"""
    return UserModel.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User",
    )


@pytest.fixture
def teacher_user():
    """Usuario profesor de prueba"""
    user = UserModel.objects.create_user(
        username="teacher",
        email="teacher@example.com",
        password="teacherpass123",
        first_name="Teacher",
        last_name="User",
    )
    user.role = "TEACHER"
    user.save()
    return user


@pytest.fixture
def student_user():
    """Usuario estudiante de prueba"""
    user = UserModel.objects.create_user(
        username="student",
        email="student@example.com",
        password="studentpass123",
        first_name="Student",
        last_name="User",
    )
    user.role = "STUDENT"
    user.save()
    return user


@pytest.fixture
def test_user_profile(test_user):
    """Perfil de usuario de prueba"""
    return UserProfile.objects.create(
        user=test_user,
        phone_number="+1234567890",
        academic_year=2024,
        current_semester="FIRST",
        credits=30,
    )


@pytest.fixture
def admin_user_profile(admin_user):
    """Perfil de administrador de prueba"""
    return UserProfile.objects.create(
        user=admin_user,
        phone_number="+1234567891",
        academic_year=2024,
        current_semester="FIRST",
        credits=0,
    )


@pytest.fixture
def teacher_user_profile(teacher_user):
    """Perfil de profesor de prueba"""
    return UserProfile.objects.create(
        user=teacher_user,
        phone_number="+1234567892",
        academic_year=2024,
        current_semester="FIRST",
        credits=0,
    )


@pytest.fixture
def student_user_profile(student_user):
    """Perfil de estudiante de prueba"""
    return UserProfile.objects.create(
        user=student_user,
        phone_number="+1234567893",
        academic_year=2024,
        current_semester="FIRST",
        credits=30,
    )


@pytest.fixture
def multiple_users():
    """Múltiples usuarios de prueba"""
    users = []
    for i in range(5):
        user = UserModel.objects.create_user(
            username=f"user{i+1}",
            email=f"user{i+1}@example.com",
            password="testpass123",
            first_name=f"User{i+1}",
            last_name="Test",
        )
        users.append(user)
    return users


@pytest.fixture
def multiple_user_profiles(multiple_users):
    """Múltiples perfiles de usuario de prueba"""
    profiles = []
    for i, user in enumerate(multiple_users):
        profile = UserProfile.objects.create(
            user=user,
            phone_number=f"+123456789{i}",
            academic_year=2024,
            current_semester="FIRST",
            credits=30,
        )
        profiles.append(profile)
    return profiles


@pytest.fixture
def sample_user_data():
    """Datos de usuario de prueba"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+1234567890",
        "role": "STUDENT",
    }


@pytest.fixture
def sample_admin_data():
    """Datos de administrador de prueba"""
    return {
        "username": "admin",
        "email": "admin@example.com",
        "password": "adminpass123",
        "first_name": "Admin",
        "last_name": "User",
        "phone_number": "+1234567891",
        "role": "ADMIN",
    }


@pytest.fixture
def sample_teacher_data():
    """Datos de profesor de prueba"""
    return {
        "username": "teacher",
        "email": "teacher@example.com",
        "password": "teacherpass123",
        "first_name": "Teacher",
        "last_name": "User",
        "phone_number": "+1234567892",
        "role": "TEACHER",
    }


@pytest.fixture
def sample_student_data():
    """Datos de estudiante de prueba"""
    return {
        "username": "student",
        "email": "student@example.com",
        "password": "studentpass123",
        "first_name": "Student",
        "last_name": "User",
        "phone_number": "+1234567893",
        "role": "STUDENT",
    }


@pytest.fixture
def sample_auth_data():
    """Datos de autenticación de prueba"""
    return {
        "username": "testuser",
        "password": "testpass123",
        "email": "test@example.com",
    }


@pytest.fixture
def sample_login_data():
    """Datos de login de prueba"""
    return {
        "username": "testuser",
        "password": "testpass123",
    }


@pytest.fixture
def sample_register_data():
    """Datos de registro de prueba"""
    return {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpass123",
        "first_name": "New",
        "last_name": "User",
        "phone_number": "+1234567894",
    }


@pytest.fixture
def sample_update_data():
    """Datos de actualización de prueba"""
    return {
        "first_name": "Updated",
        "last_name": "Name",
        "phone_number": "+1234567895",
    }


@pytest.fixture
def sample_role_data():
    """Datos de rol de prueba"""
    return {
        "role": "TEACHER",
        "permissions": ["manage_subjects", "view_reports"],
    }


@pytest.fixture
def sample_permission_data():
    """Datos de permiso de prueba"""
    return {
        "permission": "manage_users",
        "description": "Can manage user accounts",
    }


@pytest.fixture
def sample_profile_data():
    """Datos de perfil de prueba"""
    return {
        "phone_number": "+1234567890",
        "academic_year": 2024,
        "current_semester": "FIRST",
        "credits": 30,
    }


@pytest.fixture
def sample_email_data():
    """Datos de email de prueba"""
    return {
        "to_email": "test@example.com",
        "subject": "Test Subject",
        "message": "Test Message",
        "user_name": "Test User",
    }


@pytest.fixture
def sample_welcome_email_data():
    """Datos de email de bienvenida de prueba"""
    return {
        "to_email": "test@example.com",
        "user_name": "Test User",
    }


@pytest.fixture
def sample_password_reset_email_data():
    """Datos de email de reset de contraseña de prueba"""
    return {
        "to_email": "test@example.com",
        "reset_token": "reset_token_123",
    }


@pytest.fixture
def sample_notification_email_data():
    """Datos de email de notificación de prueba"""
    return {
        "to_email": "test@example.com",
        "subject": "Test Notification",
        "message": "Test notification message",
    }
