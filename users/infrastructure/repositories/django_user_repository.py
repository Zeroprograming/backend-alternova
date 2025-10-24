"""
Implementaciones de repositorio para la capa de infraestructura.
Implementa las interfaces definidas en el dominio usando Django ORM.
"""

from typing import List, Optional, Dict, Any
from django.db import models
from django.contrib.auth import get_user_model
from ..domain.entities import User, UserProfile
from ..domain.value_objects import UserId, Email, Username, UserType, UserStatus
from ..domain.repositories import (
    UserRepository,
    UserProfileRepository,
    UserSessionRepository,
    AuditRepository,
    NotificationRepository,
)
from ..domain.services import UserDomainService, AcademicDomainService
from common.audit_models import AuditLog, UserSession
from common.audit_services import AuditService
from notifications.models import Notification

DjangoUser = get_user_model()


class DjangoUserRepository(UserRepository):
    """Implementación de UserRepository usando Django ORM."""

    def save(self, user: User) -> User:
        """Guarda un usuario."""
        try:
            # Convertir entidad de dominio a modelo Django
            django_user = self._domain_to_django(user)
            django_user.save()

            # Convertir de vuelta a entidad de dominio
            return self._django_to_domain(django_user)
        except Exception as e:
            raise ValueError(f"Failed to save user: {str(e)}")

    def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Busca un usuario por ID."""
        try:
            django_user = DjangoUser.objects.get(id=user_id.value, is_active=True)
            return self._django_to_domain(django_user)
        except DjangoUser.DoesNotExist:
            return None

    def find_by_email(self, email: Email) -> Optional[User]:
        """Busca un usuario por email."""
        try:
            django_user = DjangoUser.objects.get(email=email.value, is_active=True)
            return self._django_to_domain(django_user)
        except DjangoUser.DoesNotExist:
            return None

    def find_by_username(self, username: Username) -> Optional[User]:
        """Busca un usuario por nombre de usuario."""
        try:
            django_user = DjangoUser.objects.get(
                username=username.value, is_active=True
            )
            return self._django_to_domain(django_user)
        except DjangoUser.DoesNotExist:
            return None

    def find_by_type(self, user_type: UserType) -> List[User]:
        """Busca usuarios por tipo."""
        django_users = DjangoUser.objects.filter(
            user_type=user_type.value, is_active=True
        )
        return [self._django_to_domain(user) for user in django_users]

    def find_by_status(self, status: UserStatus) -> List[User]:
        """Busca usuarios por estado."""
        django_users = DjangoUser.objects.filter(
            is_active=(status == UserStatus.ACTIVE)
        )
        return [self._django_to_domain(user) for user in django_users]

    def find_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[User]:
        """Busca todos los usuarios con paginación."""
        queryset = DjangoUser.objects.filter(is_active=True)

        if offset:
            queryset = queryset[offset:]
        if limit:
            queryset = queryset[:limit]

        return [self._django_to_domain(user) for user in queryset]

    def count(self) -> int:
        """Cuenta el total de usuarios."""
        return DjangoUser.objects.filter(is_active=True).count()

    def exists_by_email(self, email: Email) -> bool:
        """Verifica si existe un usuario con el email dado."""
        return DjangoUser.objects.filter(email=email.value, is_active=True).exists()

    def exists_by_username(self, username: Username) -> bool:
        """Verifica si existe un usuario con el nombre de usuario dado."""
        return DjangoUser.objects.filter(
            username=username.value, is_active=True
        ).exists()

    def delete(self, user_id: UserId) -> bool:
        """Elimina un usuario."""
        try:
            django_user = DjangoUser.objects.get(id=user_id.value)
            django_user.is_active = False
            django_user.save()
            return True
        except DjangoUser.DoesNotExist:
            return False

    def search(self, query: str, user_type: Optional[UserType] = None) -> List[User]:
        """Busca usuarios por texto."""
        queryset = DjangoUser.objects.filter(
            models.Q(username__icontains=query)
            | models.Q(email__icontains=query)
            | models.Q(first_name__icontains=query)
            | models.Q(last_name__icontains=query),
            is_active=True,
        )

        if user_type:
            queryset = queryset.filter(user_type=user_type.value)

        return [self._django_to_domain(user) for user in queryset]

    def _django_to_domain(self, django_user: DjangoUser) -> User:
        """Convierte modelo Django a entidad de dominio."""
        from ..domain.value_objects import AcademicInfo

        # Crear información académica si es estudiante
        academic_info = None
        if django_user.user_type == "student":
            academic_info = AcademicInfo(
                max_credits_per_semester=django_user.max_credits_per_semester,
                current_semester_credits=django_user.current_semester_credits,
                academic_year=django_user.academic_year,
            )

        return User(
            user_id=UserId(django_user.id),
            username=Username(django_user.username),
            email=Email(django_user.email),
            user_type=UserType(django_user.user_type),
            academic_info=academic_info,
            first_name=django_user.first_name,
            last_name=django_user.last_name,
            phone=django_user.phone,
            status=UserStatus.ACTIVE if django_user.is_active else UserStatus.INACTIVE,
        )

    def _domain_to_django(self, user: User) -> DjangoUser:
        """Convierte entidad de dominio a modelo Django."""
        try:
            django_user = DjangoUser.objects.get(id=user.id.value)
        except DjangoUser.DoesNotExist:
            django_user = DjangoUser()

        django_user.username = user.username.value
        django_user.email = user.email.value
        django_user.user_type = user.user_type.value
        django_user.first_name = user._first_name
        django_user.last_name = user._last_name
        django_user.phone = user._phone
        django_user.is_active = user.status == UserStatus.ACTIVE

        # Actualizar información académica si es estudiante
        if user.academic_info:
            django_user.max_credits_per_semester = (
                user.academic_info.max_credits_per_semester
            )
            django_user.current_semester_credits = (
                user.academic_info.current_semester_credits
            )
            django_user.academic_year = user.academic_info.academic_year

        return django_user


class DjangoUserProfileRepository(UserProfileRepository):
    """Implementación de UserProfileRepository usando Django ORM."""

    def save(self, profile: UserProfile) -> UserProfile:
        """Guarda un perfil de usuario."""
        try:
            # Convertir entidad de dominio a modelo Django
            django_profile = self._domain_to_django(profile)
            django_profile.save()

            # Convertir de vuelta a entidad de dominio
            return self._django_to_domain(django_profile)
        except Exception as e:
            raise ValueError(f"Failed to save profile: {str(e)}")

    def find_by_user_id(self, user_id: UserId) -> Optional[UserProfile]:
        """Busca un perfil por ID de usuario."""
        try:
            django_profile = DjangoUser.objects.get(id=user_id.value).profile
            return self._django_to_domain(django_profile)
        except (DjangoUser.DoesNotExist, AttributeError):
            return None

    def delete(self, user_id: UserId) -> bool:
        """Elimina un perfil de usuario."""
        try:
            django_user = DjangoUser.objects.get(id=user_id.value)
            if hasattr(django_user, "profile"):
                django_user.profile.delete()
            return True
        except DjangoUser.DoesNotExist:
            return False

    def _django_to_domain(self, django_profile) -> UserProfile:
        """Convierte modelo Django a entidad de dominio."""
        # Crear usuario de dominio
        user = User(
            user_id=UserId(django_profile.user.id),
            username=Username(django_profile.user.username),
            email=Email(django_profile.user.email),
            user_type=UserType(django_profile.user.user_type),
            first_name=django_profile.user.first_name,
            last_name=django_profile.user.last_name,
            phone=django_profile.user.phone,
            status=(
                UserStatus.ACTIVE
                if django_profile.user.is_active
                else UserStatus.INACTIVE
            ),
        )

        return UserProfile(
            user=user,
            address=django_profile.address,
            city=django_profile.city,
            country=django_profile.country,
            emergency_contact_name=django_profile.emergency_contact_name,
            emergency_contact_phone=django_profile.emergency_contact_phone,
        )

    def _domain_to_django(self, profile: UserProfile) -> Any:
        """Convierte entidad de dominio a modelo Django."""
        try:
            django_user = DjangoUser.objects.get(id=profile.user.id.value)
            django_profile = django_user.profile
        except (DjangoUser.DoesNotExist, AttributeError):
            from users.models import UserProfile as DjangoUserProfile

            django_profile = DjangoUserProfile(user=django_user)

        django_profile.address = profile.address
        django_profile.city = profile.city
        django_profile.country = profile.country
        django_profile.emergency_contact_name = profile.emergency_contact_name
        django_profile.emergency_contact_phone = profile.emergency_contact_phone

        return django_profile


class DjangoUserSessionRepository(UserSessionRepository):
    """Implementación de UserSessionRepository usando Django ORM."""

    def save(self, session_data: Dict[str, Any]) -> Any:
        """Guarda una sesión de usuario."""
        try:
            session = UserSession.objects.create(**session_data)
            return session
        except Exception as e:
            raise ValueError(f"Failed to save session: {str(e)}")

    def find_by_session_id(self, session_id: str) -> Optional[Any]:
        """Busca una sesión por ID."""
        try:
            return UserSession.objects.get(session_id=session_id, is_active=True)
        except UserSession.DoesNotExist:
            return None

    def find_by_user_id(self, user_id: UserId) -> List[Any]:
        """Busca sesiones por ID de usuario."""
        return UserSession.objects.filter(user_id=user_id.value, is_active=True)

    def find_active_sessions(self, user_id: UserId) -> List[Any]:
        """Busca sesiones activas de un usuario."""
        return UserSession.objects.filter(user_id=user_id.value, is_active=True)

    def delete(self, session_id: str) -> bool:
        """Elimina una sesión."""
        try:
            session = UserSession.objects.get(session_id=session_id)
            session.is_active = False
            session.save()
            return True
        except UserSession.DoesNotExist:
            return False

    def delete_all_user_sessions(self, user_id: UserId) -> int:
        """Elimina todas las sesiones de un usuario."""
        sessions = UserSession.objects.filter(user_id=user_id.value, is_active=True)
        count = sessions.count()
        sessions.update(is_active=False)
        return count

    def cleanup_expired_sessions(self) -> int:
        """Limpia sesiones expiradas."""
        from django.utils import timezone
        from datetime import timedelta

        cutoff_date = timezone.now() - timedelta(hours=24)
        sessions = UserSession.objects.filter(
            last_activity__lt=cutoff_date, is_active=True
        )
        count = sessions.count()
        sessions.update(is_active=False)
        return count


class DjangoAuditRepository(AuditRepository):
    """Implementación de AuditRepository usando Django ORM."""

    def log_action(
        self,
        user_id: UserId,
        action_type: str,
        description: str,
        content_object: Optional[Any] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Registra una acción de auditoría."""
        return AuditService.log_action(
            user_id=user_id,
            action_type=action_type,
            description=description,
            content_object=content_object,
            extra_data=extra_data,
        )

    def log_login(self, user_id: UserId, ip_address: str, user_agent: str) -> Any:
        """Registra un login."""
        return AuditService.log_login(user_id, ip_address, user_agent)

    def log_logout(self, user_id: UserId, session_id: str) -> Any:
        """Registra un logout."""
        return AuditService.log_logout(user_id, session_id)

    def find_user_actions(
        self, user_id: UserId, limit: Optional[int] = None
    ) -> List[Any]:
        """Busca acciones de un usuario."""
        queryset = AuditLog.objects.filter(user_id=user_id.value)
        if limit:
            queryset = queryset[:limit]
        return list(queryset)

    def find_recent_logins(self, user_id: UserId, days: int = 30) -> List[Any]:
        """Busca logins recientes de un usuario."""
        from django.utils import timezone
        from datetime import timedelta

        cutoff_date = timezone.now() - timedelta(days=days)
        return list(
            AuditLog.objects.filter(
                user_id=user_id.value, action_type="login", created_at__gte=cutoff_date
            )
        )


class DjangoNotificationRepository(NotificationRepository):
    """Implementación de NotificationRepository usando Django ORM."""

    def save(self, notification_data: Dict[str, Any]) -> Any:
        """Guarda una notificación."""
        try:
            notification = Notification.objects.create(**notification_data)
            return notification
        except Exception as e:
            raise ValueError(f"Failed to save notification: {str(e)}")

    def find_by_user_id(self, user_id: UserId, unread_only: bool = False) -> List[Any]:
        """Busca notificaciones por ID de usuario."""
        queryset = Notification.objects.filter(user_id=user_id.value, is_active=True)
        if unread_only:
            queryset = queryset.filter(is_read=False)
        return list(queryset)

    def mark_as_read(self, notification_id: int, user_id: UserId) -> bool:
        """Marca una notificación como leída."""
        try:
            notification = Notification.objects.get(
                id=notification_id, user_id=user_id.value
            )
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False

    def mark_all_as_read(self, user_id: UserId) -> int:
        """Marca todas las notificaciones de un usuario como leídas."""
        notifications = Notification.objects.filter(
            user_id=user_id.value, is_read=False
        )
        count = notifications.count()
        for notification in notifications:
            notification.mark_as_read()
        return count

    def count_unread(self, user_id: UserId) -> int:
        """Cuenta notificaciones no leídas."""
        return Notification.objects.filter(
            user_id=user_id.value, is_active=True, is_read=False
        ).count()

    def cleanup_old_notifications(self, days: int = 30) -> int:
        """Limpia notificaciones antiguas."""
        from django.utils import timezone
        from datetime import timedelta

        cutoff_date = timezone.now() - timedelta(days=days)
        notifications = Notification.objects.filter(
            is_read=True, read_at__lt=cutoff_date, is_active=True
        )
        count = notifications.count()
        notifications.update(is_active=False)
        return count

