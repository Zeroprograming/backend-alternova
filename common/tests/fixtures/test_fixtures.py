# Fixtures de prueba para Common App

import pytest
from django.contrib.auth.models import User
from common.infrastructure.audit_models import AuditLog, UserSession


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
def sample_audit_log(test_user):
    """Log de auditoría de prueba"""
    return AuditLog.objects.create(
        action="CREATE",
        model_name="User",
        object_id="1",
        user_id=str(test_user.id),
        ip_address="127.0.0.1",
        user_agent="Test Agent",
        additional_data={"test": "data"},
    )


@pytest.fixture
def sample_user_session(test_user):
    """Sesión de usuario de prueba"""
    return UserSession.objects.create(
        user_id=str(test_user.id),
        session_key="test_session_key",
        ip_address="127.0.0.1",
        user_agent="Test Agent",
        is_active=True,
    )


@pytest.fixture
def multiple_audit_logs(test_user):
    """Múltiples logs de auditoría de prueba"""
    logs = []
    for i in range(5):
        log = AuditLog.objects.create(
            action="CREATE",
            model_name="User",
            object_id=str(i + 1),
            user_id=str(test_user.id),
            ip_address="127.0.0.1",
            user_agent="Test Agent",
        )
        logs.append(log)
    return logs


@pytest.fixture
def sample_request_data():
    """Datos de request de prueba"""
    return {
        "method": "GET",
        "path": "/api/test/",
        "ip_address": "127.0.0.1",
        "user_agent": "Mozilla/5.0 (Test Agent)",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer test-token",
        },
    }


@pytest.fixture
def sample_query_data():
    """Datos de consulta de prueba"""
    return {
        "sql": "SELECT * FROM users WHERE id = %s",
        "params": [1],
        "execution_time": 0.05,
        "query_count": 1,
    }


@pytest.fixture
def sample_performance_data():
    """Datos de performance de prueba"""
    return {
        "total_queries": 100,
        "avg_execution_time": 0.1,
        "slow_queries": 5,
        "optimized_queries": 10,
    }
