"""
Interfaces de repositorio para el dominio de usuarios.
Define contratos para el acceso a datos sin depender de implementaciones específicas.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from .entities import User, UserProfile
from .value_objects import UserId, Email, Username, UserType, UserStatus


class UserRepository(ABC):
    """Interfaz para el repositorio de usuarios."""

    @abstractmethod
    def save(self, user: User) -> User:
        """Guarda un usuario."""
        pass

    @abstractmethod
    def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Busca un usuario por ID."""
        pass

    @abstractmethod
    def find_by_email(self, email: Email) -> Optional[User]:
        """Busca un usuario por email."""
        pass

    @abstractmethod
    def find_by_username(self, username: Username) -> Optional[User]:
        """Busca un usuario por nombre de usuario."""
        pass

    @abstractmethod
    def find_by_type(self, user_type: UserType) -> List[User]:
        """Busca usuarios por tipo."""
        pass

    @abstractmethod
    def find_by_status(self, status: UserStatus) -> List[User]:
        """Busca usuarios por estado."""
        pass

    @abstractmethod
    def find_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[User]:
        """Busca todos los usuarios con paginación."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Cuenta el total de usuarios."""
        pass

    @abstractmethod
    def exists_by_email(self, email: Email) -> bool:
        """Verifica si existe un usuario con el email dado."""
        pass

    @abstractmethod
    def exists_by_username(self, username: Username) -> bool:
        """Verifica si existe un usuario con el nombre de usuario dado."""
        pass

    @abstractmethod
    def delete(self, user_id: UserId) -> bool:
        """Elimina un usuario."""
        pass

    @abstractmethod
    def search(self, query: str, user_type: Optional[UserType] = None) -> List[User]:
        """Busca usuarios por texto."""
        pass


class UserProfileRepository(ABC):
    """Interfaz para el repositorio de perfiles de usuario."""

    @abstractmethod
    def save(self, profile: UserProfile) -> UserProfile:
        """Guarda un perfil de usuario."""
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: UserId) -> Optional[UserProfile]:
        """Busca un perfil por ID de usuario."""
        pass

    @abstractmethod
    def delete(self, user_id: UserId) -> bool:
        """Elimina un perfil de usuario."""
        pass


class UserSessionRepository(ABC):
    """Interfaz para el repositorio de sesiones de usuario."""

    @abstractmethod
    def save(self, session) -> Any:
        """Guarda una sesión de usuario."""
        pass

    @abstractmethod
    def find_by_session_id(self, session_id: str) -> Optional[Any]:
        """Busca una sesión por ID."""
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: UserId) -> List[Any]:
        """Busca sesiones por ID de usuario."""
        pass

    @abstractmethod
    def find_active_sessions(self, user_id: UserId) -> List[Any]:
        """Busca sesiones activas de un usuario."""
        pass

    @abstractmethod
    def delete(self, session_id: str) -> bool:
        """Elimina una sesión."""
        pass

    @abstractmethod
    def delete_all_user_sessions(self, user_id: UserId) -> int:
        """Elimina todas las sesiones de un usuario."""
        pass

    @abstractmethod
    def cleanup_expired_sessions(self) -> int:
        """Limpia sesiones expiradas."""
        pass


class AuditRepository(ABC):
    """Interfaz para el repositorio de auditoría."""

    @abstractmethod
    def log_action(
        self,
        user_id: UserId,
        action_type: str,
        description: str,
        content_object: Optional[Any] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Registra una acción de auditoría."""
        pass

    @abstractmethod
    def log_login(self, user_id: UserId, ip_address: str, user_agent: str) -> Any:
        """Registra un login."""
        pass

    @abstractmethod
    def log_logout(self, user_id: UserId, session_id: str) -> Any:
        """Registra un logout."""
        pass

    @abstractmethod
    def find_user_actions(
        self, user_id: UserId, limit: Optional[int] = None
    ) -> List[Any]:
        """Busca acciones de un usuario."""
        pass

    @abstractmethod
    def find_recent_logins(self, user_id: UserId, days: int = 30) -> List[Any]:
        """Busca logins recientes de un usuario."""
        pass


class NotificationRepository(ABC):
    """Interfaz para el repositorio de notificaciones."""

    @abstractmethod
    def save(self, notification) -> Any:
        """Guarda una notificación."""
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: UserId, unread_only: bool = False) -> List[Any]:
        """Busca notificaciones por ID de usuario."""
        pass

    @abstractmethod
    def mark_as_read(self, notification_id: int, user_id: UserId) -> bool:
        """Marca una notificación como leída."""
        pass

    @abstractmethod
    def mark_all_as_read(self, user_id: UserId) -> int:
        """Marca todas las notificaciones de un usuario como leídas."""
        pass

    @abstractmethod
    def count_unread(self, user_id: UserId) -> int:
        """Cuenta notificaciones no leídas."""
        pass

    @abstractmethod
    def cleanup_old_notifications(self, days: int = 30) -> int:
        """Limpia notificaciones antiguas."""
        pass
