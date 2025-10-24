"""
Servicios para gestión de roles y usuarios.
"""

from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from common.audit_services import AuditService
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class RoleManagementService:
    """Servicio para gestión de roles de usuarios."""

    VALID_ROLES = ["admin", "teacher", "student"]
    ROLE_PERMISSIONS = {
        "admin": ["all"],
        "teacher": [
            "view_subjects",
            "assign_grades",
            "view_students",
            "create_reports",
        ],
        "student": ["view_own_data", "enroll_subjects", "view_grades"],
    }

    @staticmethod
    def assign_role(user_id, new_role, requesting_user):
        """
        Asigna un nuevo rol a un usuario.

        Args:
            user_id: ID del usuario a modificar
            new_role: Nuevo rol a asignar
            requesting_user: Usuario que hace la petición

        Returns:
            User: Usuario actualizado

        Raises:
            PermissionError: Si no tiene permisos
            ValueError: Si el rol no es válido
        """
        # Solo administradores pueden asignar roles
        if not requesting_user.is_staff:
            raise PermissionError("Solo administradores pueden asignar roles")

        # Validar rol
        if new_role not in RoleManagementService.VALID_ROLES:
            raise ValueError(
                f"Rol inválido. Roles válidos: {RoleManagementService.VALID_ROLES}"
            )

        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")

        # No permitir cambiar rol de otro administrador
        if user.is_staff and user != requesting_user:
            raise PermissionError("No puedes cambiar el rol de otro administrador")

        # Guardar rol anterior para auditoría
        old_role = user.user_type
        old_is_staff = user.is_staff

        # Actualizar rol
        user.user_type = new_role
        user.is_staff = new_role == "admin"
        user.save()

        # Log de auditoría
        AuditService.log_action(
            user=requesting_user,
            action_type="role_change",
            description=f"Rol cambiado de {old_role} a {new_role} para usuario {user.username}",
            content_object=user,
            extra_data={
                "old_role": old_role,
                "new_role": new_role,
                "old_is_staff": old_is_staff,
                "new_is_staff": user.is_staff,
            },
        )

        logger.info(
            f"Rol {new_role} asignado a {user.username} por {requesting_user.username}"
        )

        return user

    @staticmethod
    def get_user_permissions(user):
        """
        Obtiene los permisos de un usuario según su rol.

        Args:
            user: Usuario

        Returns:
            list: Lista de permisos
        """
        if not user.is_authenticated:
            return []

        role = user.user_type
        return RoleManagementService.ROLE_PERMISSIONS.get(role, [])

    @staticmethod
    def can_user_perform_action(user, action):
        """
        Verifica si un usuario puede realizar una acción específica.

        Args:
            user: Usuario
            action: Acción a verificar

        Returns:
            bool: True si puede realizar la acción
        """
        permissions = RoleManagementService.get_user_permissions(user)
        return "all" in permissions or action in permissions

    @staticmethod
    def get_users_by_role(role):
        """
        Obtiene todos los usuarios de un rol específico.

        Args:
            role: Rol a filtrar

        Returns:
            QuerySet: Usuarios del rol
        """
        if role not in RoleManagementService.VALID_ROLES:
            raise ValueError(f"Rol inválido: {role}")

        return User.objects.filter(user_type=role, is_active=True)

    @staticmethod
    def get_role_statistics():
        """
        Obtiene estadísticas de roles en el sistema.

        Returns:
            dict: Estadísticas de roles
        """
        stats = {}
        for role in RoleManagementService.VALID_ROLES:
            count = User.objects.filter(user_type=role, is_active=True).count()
            stats[role] = count

        stats["total_active"] = User.objects.filter(is_active=True).count()
        stats["total_inactive"] = User.objects.filter(is_active=False).count()

        return stats

    @staticmethod
    @transaction.atomic
    def bulk_assign_role(user_ids, new_role, requesting_user):
        """
        Asigna un rol a múltiples usuarios.

        Args:
            user_ids: Lista de IDs de usuarios
            new_role: Rol a asignar
            requesting_user: Usuario que hace la petición

        Returns:
            list: Usuarios actualizados

        Raises:
            PermissionError: Si no tiene permisos
            ValueError: Si el rol no es válido
        """
        # Solo administradores pueden hacer asignaciones masivas
        if not requesting_user.is_staff:
            raise PermissionError(
                "Solo administradores pueden hacer asignaciones masivas"
            )

        # Validar rol
        if new_role not in RoleManagementService.VALID_ROLES:
            raise ValueError(
                f"Rol inválido. Roles válidos: {RoleManagementService.VALID_ROLES}"
            )

        updated_users = []
        for user_id in user_ids:
            try:
                user = RoleManagementService.assign_role(
                    user_id, new_role, requesting_user
                )
                updated_users.append(user)
            except (ValueError, PermissionError) as e:
                logger.warning(f"Error asignando rol a usuario {user_id}: {e}")
                continue

        logger.info(
            f"Asignación masiva de rol {new_role} completada por {requesting_user.username}. "
            f"{len(updated_users)} usuarios actualizados."
        )

        return updated_users


class UserManagementService:
    """Servicio para gestión general de usuarios."""

    @staticmethod
    def create_user_with_role(user_data, role, requesting_user):
        """
        Crea un usuario con un rol específico.

        Args:
            user_data: Datos del usuario
            role: Rol a asignar
            requesting_user: Usuario que crea

        Returns:
            User: Usuario creado

        Raises:
            PermissionError: Si no tiene permisos
            ValueError: Si los datos son inválidos
        """
        # Solo administradores pueden crear usuarios
        if not requesting_user.is_staff:
            raise PermissionError("Solo administradores pueden crear usuarios")

        # Validar rol
        if role not in RoleManagementService.VALID_ROLES:
            raise ValueError(f"Rol inválido: {role}")

        # Crear usuario
        user = User.objects.create_user(
            username=user_data["username"],
            email=user_data.get("email", ""),
            password=user_data["password"],
            first_name=user_data.get("first_name", ""),
            last_name=user_data.get("last_name", ""),
            user_type=role,
            is_staff=role == "admin",
        )

        # Agregar información para el signal de notificación
        user._created_by = requesting_user

        # Log de auditoría
        AuditService.log_action(
            user=requesting_user,
            action_type="user_creation",
            description=f"Usuario {user.username} creado con rol {role}",
            content_object=user,
            extra_data={"role": role, "created_by": requesting_user.username},
        )

        logger.info(
            f"Usuario {user.username} creado con rol {role} por {requesting_user.username}"
        )

        return user

    @staticmethod
    def deactivate_user(user_id, requesting_user):
        """
        Desactiva un usuario.

        Args:
            user_id: ID del usuario a desactivar
            requesting_user: Usuario que desactiva

        Returns:
            User: Usuario desactivado

        Raises:
            PermissionError: Si no tiene permisos
            ValueError: Si el usuario no existe
        """
        # Solo administradores pueden desactivar usuarios
        if not requesting_user.is_staff:
            raise PermissionError("Solo administradores pueden desactivar usuarios")

        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")

        # No permitir desactivar a otro administrador
        if user.is_staff and user != requesting_user:
            raise PermissionError("No puedes desactivar a otro administrador")

        # Desactivar usuario
        user.is_active = False
        user.save()

        # Log de auditoría
        AuditService.log_action(
            user=requesting_user,
            action_type="user_deactivation",
            description=f"Usuario {user.username} desactivado",
            content_object=user,
        )

        logger.info(
            f"Usuario {user.username} desactivado por {requesting_user.username}"
        )

        return user

    @staticmethod
    def activate_user(user_id, requesting_user):
        """
        Activa un usuario.

        Args:
            user_id: ID del usuario a activar
            requesting_user: Usuario que activa

        Returns:
            User: Usuario activado

        Raises:
            PermissionError: Si no tiene permisos
            ValueError: Si el usuario no existe
        """
        # Solo administradores pueden activar usuarios
        if not requesting_user.is_staff:
            raise PermissionError("Solo administradores pueden activar usuarios")

        try:
            user = User.objects.get(id=user_id, is_active=False)
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")

        # Activar usuario
        user.is_active = True
        user.save()

        # Log de auditoría
        AuditService.log_action(
            user=requesting_user,
            action_type="user_activation",
            description=f"Usuario {user.username} activado",
            content_object=user,
        )

        logger.info(f"Usuario {user.username} activado por {requesting_user.username}")

        return user

    @staticmethod
    def reset_user_password(user_id, new_password, requesting_user):
        """
        Resetea la contraseña de un usuario.

        Args:
            user_id: ID del usuario
            new_password: Nueva contraseña
            requesting_user: Usuario que resetea

        Returns:
            User: Usuario actualizado

        Raises:
            PermissionError: Si no tiene permisos
            ValueError: Si el usuario no existe
        """
        # Solo administradores pueden resetear contraseñas
        if not requesting_user.is_staff:
            raise PermissionError("Solo administradores pueden resetear contraseñas")

        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")

        # Resetear contraseña
        user.set_password(new_password)
        user.save()

        # Log de auditoría
        AuditService.log_action(
            user=requesting_user,
            action_type="password_reset",
            description=f"Contraseña reseteada para usuario {user.username}",
            content_object=user,
        )

        logger.info(
            f"Contraseña reseteada para {user.username} por {requesting_user.username}"
        )

        return user
