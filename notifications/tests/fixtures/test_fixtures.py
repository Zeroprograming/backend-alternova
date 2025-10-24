# Fixtures de prueba para Notifications App

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
def sample_notification():
    """Notificación de prueba"""
    return {
        "title": "Test Notification",
        "message": "This is a test notification",
        "notification_type": "INFO",
        "user_id": "1",
        "is_read": False,
        "priority": "MEDIUM",
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_notifications():
    """Múltiples notificaciones de prueba"""
    notifications = []
    for i in range(5):
        notification = {
            "id": str(i + 1),
            "title": f"Notification {i+1}",
            "message": f"Message {i+1}",
            "notification_type": "INFO",
            "user_id": "1",
            "is_read": i % 2 == 0,  # Alternar entre leída y no leída
            "priority": "MEDIUM",
            "created_at": f"2024-01-0{i+1}T00:00:00Z",
        }
        notifications.append(notification)
    return notifications


@pytest.fixture
def notification_types():
    """Tipos de notificación disponibles"""
    return ["INFO", "WARNING", "ERROR", "SUCCESS"]


@pytest.fixture
def notification_priorities():
    """Prioridades de notificación disponibles"""
    return ["LOW", "MEDIUM", "HIGH", "URGENT"]


@pytest.fixture
def sample_email_notification():
    """Notificación por email de prueba"""
    return {
        "to_email": "test@example.com",
        "subject": "Test Email Notification",
        "message": "This is a test email notification",
        "template": "notification",
        "notification_type": "INFO",
        "user_id": "1",
    }


@pytest.fixture
def sample_push_notification():
    """Notificación push de prueba"""
    return {
        "title": "Push Notification",
        "message": "This is a push notification",
        "notification_type": "INFO",
        "user_id": "1",
        "device_token": "test_device_token",
        "platform": "android",
    }


@pytest.fixture
def sample_sms_notification():
    """Notificación SMS de prueba"""
    return {
        "phone_number": "+1234567890",
        "message": "This is a test SMS notification",
        "notification_type": "INFO",
        "user_id": "1",
    }


@pytest.fixture
def notification_service_mock():
    """Mock del servicio de notificaciones"""
    from unittest.mock import Mock

    service = Mock()
    service.send_notification.return_value = True
    service.mark_as_read.return_value = True
    service.delete_notification.return_value = True
    service.get_user_notifications.return_value = []
    service.send_batch_notifications.return_value = 0

    return service


@pytest.fixture
def email_service_mock():
    """Mock del servicio de email"""
    from unittest.mock import Mock

    service = Mock()
    service.send_email.return_value = True
    service.send_bulk_email.return_value = 0
    service.validate_email.return_value = True

    return service


@pytest.fixture
def push_service_mock():
    """Mock del servicio de push notifications"""
    from unittest.mock import Mock

    service = Mock()
    service.send_push.return_value = True
    service.send_bulk_push.return_value = 0
    service.validate_device_token.return_value = True

    return service


@pytest.fixture
def sms_service_mock():
    """Mock del servicio de SMS"""
    from unittest.mock import Mock

    service = Mock()
    service.send_sms.return_value = True
    service.send_bulk_sms.return_value = 0
    service.validate_phone_number.return_value = True

    return service


@pytest.fixture
def notification_request_data():
    """Datos de request para crear notificación"""
    return {
        "title": "Request Notification",
        "message": "This notification was created via request",
        "notification_type": "INFO",
        "user_id": "1",
        "priority": "MEDIUM",
        "send_email": True,
        "send_push": False,
        "send_sms": False,
    }


@pytest.fixture
def notification_response_data():
    """Datos de respuesta para notificación"""
    return {
        "id": "1",
        "title": "Response Notification",
        "message": "This is a response notification",
        "notification_type": "INFO",
        "user_id": "1",
        "is_read": False,
        "priority": "MEDIUM",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }
