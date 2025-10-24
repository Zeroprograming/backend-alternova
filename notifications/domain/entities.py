"""
Entidades del dominio para notifications.
Contiene las entidades principales del dominio de notificaciones.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class NotificationType(Enum):
    """Tipo de notificación."""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    SYSTEM = "system"


class NotificationStatus(Enum):
    """Estado de una notificación."""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class NotificationPriority(Enum):
    """Prioridad de una notificación."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Notification:
    """Entidad Notification - Notificación."""

    id: str
    title: str
    message: str
    notification_type: NotificationType
    recipient_id: str
    sender_id: Optional[str] = None
    status: NotificationStatus = NotificationStatus.PENDING
    priority: NotificationPriority = NotificationPriority.NORMAL
    metadata: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None

    def mark_as_sent(self) -> None:
        """Marca la notificación como enviada."""
        self.status = NotificationStatus.SENT
        self.sent_at = datetime.now()
        self.updated_at = datetime.now()

    def mark_as_delivered(self) -> None:
        """Marca la notificación como entregada."""
        self.status = NotificationStatus.DELIVERED
        self.updated_at = datetime.now()

    def mark_as_read(self) -> None:
        """Marca la notificación como leída."""
        self.status = NotificationStatus.READ
        self.read_at = datetime.now()
        self.updated_at = datetime.now()

    def mark_as_failed(self) -> None:
        """Marca la notificación como fallida."""
        self.status = NotificationStatus.FAILED
        self.updated_at = datetime.now()

    def is_read(self) -> bool:
        """Verifica si la notificación está leída."""
        return self.status == NotificationStatus.READ

    def is_sent(self) -> bool:
        """Verifica si la notificación está enviada."""
        return self.status in [
            NotificationStatus.SENT,
            NotificationStatus.DELIVERED,
            NotificationStatus.READ,
        ]


@dataclass
class NotificationTemplate:
    """Entidad NotificationTemplate - Plantilla de notificación."""

    id: str
    name: str
    title_template: str
    message_template: str
    notification_type: NotificationType
    variables: List[str]
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None

    def render(self, variables: Dict[str, Any]) -> tuple[str, str]:
        """Renderiza la plantilla con las variables."""
        title = self.title_template
        message = self.message_template

        for key, value in variables.items():
            title = title.replace(f"{{{key}}}", str(value))
            message = message.replace(f"{{{key}}}", str(value))

        return title, message

    def validate_variables(self, variables: Dict[str, Any]) -> bool:
        """Valida que todas las variables requeridas estén presentes."""
        return all(var in variables for var in self.variables)


@dataclass
class NotificationPreferences:
    """Entidad NotificationPreferences - Preferencias de notificación."""

    id: str
    user_id: str
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    in_app_enabled: bool = True
    system_enabled: bool = True
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None

    def is_notification_allowed(self, notification_type: NotificationType) -> bool:
        """Verifica si el tipo de notificación está permitido."""
        type_mapping = {
            NotificationType.EMAIL: self.email_enabled,
            NotificationType.SMS: self.sms_enabled,
            NotificationType.PUSH: self.push_enabled,
            NotificationType.IN_APP: self.in_app_enabled,
            NotificationType.SYSTEM: self.system_enabled,
        }
        return type_mapping.get(notification_type, False)

    def is_quiet_time(self, current_time: datetime) -> bool:
        """Verifica si es hora silenciosa."""
        if not self.quiet_hours_start or not self.quiet_hours_end:
            return False

        # Implementar lógica de hora silenciosa
        return False
