"""
Data Transfer Objects (DTOs) para la capa de aplicación.
Objetos para transferir datos entre capas sin exponer entidades de dominio.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class UserDTO:
    """DTO para usuarios."""

    id: int
    username: str
    email: str
    user_type: str
    first_name: str
    last_name: str
    phone: str
    status: str
    full_name: str
    is_student: bool
    is_teacher: bool
    is_admin: bool
    academic_info: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class UserProfileDTO:
    """DTO para perfiles de usuario."""

    user_id: int
    address: str
    city: str
    country: str
    emergency_contact_name: str
    emergency_contact_phone: str
    full_address: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class CreateUserDTO:
    """DTO para crear usuarios."""

    username: str
    email: str
    password: str
    user_type: str
    first_name: str = ""
    last_name: str = ""
    phone: str = ""
    max_credits_per_semester: Optional[int] = None
    academic_year: str = "2024-1"


@dataclass
class UpdateUserDTO:
    """DTO para actualizar usuarios."""

    user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    user_type: Optional[str] = None


@dataclass
class LoginDTO:
    """DTO para login."""

    username: str
    password: str
    ip_address: str
    user_agent: str


@dataclass
class LoginResponseDTO:
    """DTO para respuesta de login."""

    success: bool
    user: Optional[UserDTO] = None
    tokens: Optional[Dict[str, str]] = None
    session_id: Optional[str] = None
    error: Optional[str] = None


@dataclass
class LogoutDTO:
    """DTO para logout."""

    session_id: str
    user_id: int


@dataclass
class LogoutResponseDTO:
    """DTO para respuesta de logout."""

    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


@dataclass
class RefreshTokenDTO:
    """DTO para refresh token."""

    refresh_token: str


@dataclass
class RefreshTokenResponseDTO:
    """DTO para respuesta de refresh token."""

    success: bool
    tokens: Optional[Dict[str, str]] = None
    error: Optional[str] = None


@dataclass
class VerifyTokenDTO:
    """DTO para verificar token."""

    access_token: str


@dataclass
class VerifyTokenResponseDTO:
    """DTO para respuesta de verificar token."""

    success: bool
    user: Optional[UserDTO] = None
    error: Optional[str] = None


@dataclass
class RoleAssignmentDTO:
    """DTO para asignación de roles."""

    user_id: int
    new_role: str


@dataclass
class RoleAssignmentResponseDTO:
    """DTO para respuesta de asignación de roles."""

    success: bool
    user: Optional[UserDTO] = None
    message: Optional[str] = None
    error: Optional[str] = None


@dataclass
class BulkRoleAssignmentDTO:
    """DTO para asignación masiva de roles."""

    user_ids: List[int]
    new_role: str


@dataclass
class BulkRoleAssignmentResponseDTO:
    """DTO para respuesta de asignación masiva de roles."""

    success: bool
    successful_assignments: List[Dict[str, Any]] = None
    failed_assignments: List[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None


@dataclass
class UserSessionDTO:
    """DTO para sesiones de usuario."""

    session_id: str
    user_id: int
    ip_address: str
    user_agent: str
    created_at: datetime
    last_activity: datetime
    is_active: bool


@dataclass
class AcademicInfoDTO:
    """DTO para información académica."""

    max_credits_per_semester: int
    current_semester_credits: int
    available_credits: int
    academic_year: str
    can_enroll: bool


@dataclass
class StudentAcademicSummaryDTO:
    """DTO para resumen académico de estudiante."""

    student_id: int
    username: str
    email: str
    full_name: str
    academic_info: AcademicInfoDTO
    total_subjects: int
    approved_subjects: int
    failed_subjects: int
    cumulative_average: float


@dataclass
class UserStatisticsDTO:
    """DTO para estadísticas de usuarios."""

    total_users: int
    active_users: int
    inactive_users: int
    suspended_users: int
    students: int
    teachers: int
    admins: int
    activation_rate: float


@dataclass
class SearchUsersDTO:
    """DTO para búsqueda de usuarios."""

    query: str
    user_type: Optional[str] = None
    status: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


@dataclass
class SearchUsersResponseDTO:
    """DTO para respuesta de búsqueda de usuarios."""

    success: bool
    users: List[UserDTO] = None
    total: int = 0
    error: Optional[str] = None


@dataclass
class UserPermissionsDTO:
    """DTO para permisos de usuario."""

    user_id: int
    user_type: str
    permissions: List[str]
    is_active: bool


@dataclass
class AuditLogDTO:
    """DTO para logs de auditoría."""

    id: int
    user_id: int
    action_type: str
    description: str
    content_object_type: Optional[str] = None
    content_object_id: Optional[int] = None
    extra_data: Optional[Dict[str, Any]] = None
    created_at: datetime


@dataclass
class NotificationDTO:
    """DTO para notificaciones."""

    id: int
    user_id: int
    title: str
    message: str
    notification_type: str
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime


@dataclass
class CreateNotificationDTO:
    """DTO para crear notificaciones."""

    user_id: int
    title: str
    message: str
    notification_type: str = "info"
    send_email: bool = True


@dataclass
class NotificationResponseDTO:
    """DTO para respuesta de notificaciones."""

    success: bool
    notification: Optional[NotificationDTO] = None
    message: Optional[str] = None
    error: Optional[str] = None

