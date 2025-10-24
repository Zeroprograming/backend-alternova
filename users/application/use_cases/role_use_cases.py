"""
Casos de uso para gestión de roles de usuarios.
Contiene la lógica de aplicación para operaciones de roles.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..domain.entities import User
from ..domain.value_objects import UserId, UserType, UserStatus
from ..domain.repositories import UserRepository, AuditRepository
from ..domain.services import UserDomainService


class AssignRoleUseCase:
    """Caso de uso para asignar roles a usuarios."""

    def __init__(
        self, domain_service: UserDomainService, audit_repository: AuditRepository
    ):
        self._domain_service = domain_service
        self._audit_repository = audit_repository

    def execute(
        self, user_id: int, new_role: str, requesting_user: User
    ) -> Dict[str, Any]:
        """
        Asigna un nuevo rol a un usuario.

        Args:
            user_id: ID del usuario
            new_role: Nuevo rol a asignar
            requesting_user: Usuario que solicita el cambio

        Returns:
            Dict: Resultado de la asignación
        """
        try:
            # Validar entrada
            user_id_vo = UserId(user_id)
            new_role_vo = UserType(new_role)

            # Cambiar tipo de usuario usando el servicio de dominio
            updated_user = self._domain_service.change_user_type(
                user_id=user_id_vo,
                new_type=new_role_vo,
                requesting_user=requesting_user,
            )

            # Registrar auditoría
            self._audit_repository.log_action(
                user_id=requesting_user.id,
                action_type="role_assignment",
                description=f"Assigned role {new_role} to user {updated_user.username.value}",
                content_object=updated_user,
                extra_data={
                    "target_user_id": user_id,
                    "new_role": new_role,
                    "previous_role": updated_user.user_type.value,
                },
            )

            return {
                "success": True,
                "user": {
                    "id": updated_user.id.value,
                    "username": updated_user.username.value,
                    "email": updated_user.email.value,
                    "user_type": updated_user.user_type.value,
                    "full_name": updated_user.full_name,
                    "status": updated_user.status.value,
                },
                "message": f"Role {new_role} assigned successfully",
            }

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": "Role assignment failed"}


class BulkAssignRoleUseCase:
    """Caso de uso para asignar roles masivamente."""

    def __init__(
        self, domain_service: UserDomainService, audit_repository: AuditRepository
    ):
        self._domain_service = domain_service
        self._audit_repository = audit_repository

    def execute(
        self, user_ids: List[int], new_role: str, requesting_user: User
    ) -> Dict[str, Any]:
        """
        Asigna un rol a múltiples usuarios.

        Args:
            user_ids: Lista de IDs de usuarios
            new_role: Nuevo rol a asignar
            requesting_user: Usuario que solicita el cambio

        Returns:
            Dict: Resultado de la asignación masiva
        """
        try:
            # Validar entrada
            new_role_vo = UserType(new_role)

            successful_assignments = []
            failed_assignments = []

            for user_id in user_ids:
                try:
                    user_id_vo = UserId(user_id)
                    updated_user = self._domain_service.change_user_type(
                        user_id=user_id_vo,
                        new_type=new_role_vo,
                        requesting_user=requesting_user,
                    )

                    successful_assignments.append(
                        {
                            "user_id": user_id,
                            "username": updated_user.username.value,
                            "email": updated_user.email.value,
                        }
                    )

                except Exception as e:
                    failed_assignments.append({"user_id": user_id, "error": str(e)})

            # Registrar auditoría
            self._audit_repository.log_action(
                user_id=requesting_user.id,
                action_type="bulk_role_assignment",
                description=f"Bulk assigned role {new_role} to {len(successful_assignments)} users",
                extra_data={
                    "new_role": new_role,
                    "successful_count": len(successful_assignments),
                    "failed_count": len(failed_assignments),
                    "user_ids": user_ids,
                },
            )

            return {
                "success": True,
                "successful_assignments": successful_assignments,
                "failed_assignments": failed_assignments,
                "message": f"Role {new_role} assigned to {len(successful_assignments)} users",
            }

        except Exception as e:
            return {"success": False, "error": "Bulk role assignment failed"}


class GetUsersByRoleUseCase:
    """Caso de uso para obtener usuarios por rol."""

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def execute(
        self,
        role: str,
        requesting_user: User,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Obtiene usuarios por rol.

        Args:
            role: Rol a buscar
            requesting_user: Usuario que solicita la información
            limit: Límite de resultados
            offset: Offset para paginación

        Returns:
            Dict: Lista de usuarios
        """
        try:
            # Solo administradores pueden obtener usuarios por rol
            if not requesting_user.is_admin:
                raise ValueError("Insufficient permissions")

            # Validar entrada
            role_vo = UserType(role)

            # Buscar usuarios por rol
            users = self._user_repository.find_by_type(role_vo)

            # Aplicar paginación
            if offset:
                users = users[offset:]
            if limit:
                users = users[:limit]

            return {
                "success": True,
                "users": [
                    {
                        "id": user.id.value,
                        "username": user.username.value,
                        "email": user.email.value,
                        "user_type": user.user_type.value,
                        "full_name": user.full_name,
                        "status": user.status.value,
                        "academic_info": (
                            user.get_academic_summary() if user.is_student else None
                        ),
                    }
                    for user in users
                ],
                "total": len(users),
                "role": role,
            }

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": "Failed to get users by role"}


class GetRoleStatisticsUseCase:
    """Caso de uso para obtener estadísticas de roles."""

    def __init__(self, domain_service: UserDomainService):
        self._domain_service = domain_service

    def execute(self, requesting_user: User) -> Dict[str, Any]:
        """
        Obtiene estadísticas de roles de usuarios.

        Args:
            requesting_user: Usuario que solicita las estadísticas

        Returns:
            Dict: Estadísticas de roles
        """
        try:
            # Solo administradores pueden ver estadísticas
            if not requesting_user.is_admin:
                raise ValueError("Insufficient permissions")

            # Obtener estadísticas usando el servicio de dominio
            stats = self._domain_service.get_user_statistics()

            return {"success": True, "statistics": stats}

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": "Failed to get role statistics"}


class DeactivateUserUseCase:
    """Caso de uso para desactivar usuarios."""

    def __init__(
        self, domain_service: UserDomainService, audit_repository: AuditRepository
    ):
        self._domain_service = domain_service
        self._audit_repository = audit_repository

    def execute(self, user_id: int, requesting_user: User) -> Dict[str, Any]:
        """
        Desactiva un usuario.

        Args:
            user_id: ID del usuario a desactivar
            requesting_user: Usuario que solicita la desactivación

        Returns:
            Dict: Resultado de la desactivación
        """
        try:
            # Validar entrada
            user_id_vo = UserId(user_id)

            # Desactivar usuario usando el servicio de dominio
            updated_user = self._domain_service.deactivate_user(
                user_id=user_id_vo, requesting_user=requesting_user
            )

            # Registrar auditoría
            self._audit_repository.log_action(
                user_id=requesting_user.id,
                action_type="user_deactivation",
                description=f"Deactivated user {updated_user.username.value}",
                content_object=updated_user,
                extra_data={"deactivated_user_id": user_id},
            )

            return {
                "success": True,
                "user": {
                    "id": updated_user.id.value,
                    "username": updated_user.username.value,
                    "email": updated_user.email.value,
                    "user_type": updated_user.user_type.value,
                    "full_name": updated_user.full_name,
                    "status": updated_user.status.value,
                },
                "message": "User deactivated successfully",
            }

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": "User deactivation failed"}


class ActivateUserUseCase:
    """Caso de uso para activar usuarios."""

    def __init__(
        self, domain_service: UserDomainService, audit_repository: AuditRepository
    ):
        self._domain_service = domain_service
        self._audit_repository = audit_repository

    def execute(self, user_id: int, requesting_user: User) -> Dict[str, Any]:
        """
        Activa un usuario.

        Args:
            user_id: ID del usuario a activar
            requesting_user: Usuario que solicita la activación

        Returns:
            Dict: Resultado de la activación
        """
        try:
            # Validar entrada
            user_id_vo = UserId(user_id)

            # Activar usuario usando el servicio de dominio
            updated_user = self._domain_service.activate_user(
                user_id=user_id_vo, requesting_user=requesting_user
            )

            # Registrar auditoría
            self._audit_repository.log_action(
                user_id=requesting_user.id,
                action_type="user_activation",
                description=f"Activated user {updated_user.username.value}",
                content_object=updated_user,
                extra_data={"activated_user_id": user_id},
            )

            return {
                "success": True,
                "user": {
                    "id": updated_user.id.value,
                    "username": updated_user.username.value,
                    "email": updated_user.email.value,
                    "user_type": updated_user.user_type.value,
                    "full_name": updated_user.full_name,
                    "status": updated_user.status.value,
                },
                "message": "User activated successfully",
            }

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": "User activation failed"}

