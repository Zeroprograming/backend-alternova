"""
Casos de uso para gestión de usuarios.
Contiene la lógica de aplicación para operaciones CRUD de usuarios.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..domain.entities import User, UserProfile
from ..domain.value_objects import (
    UserId,
    Username,
    Email,
    Password,
    UserType,
    UserStatus,
    AcademicInfo,
)
from ..domain.repositories import UserRepository, UserProfileRepository, AuditRepository
from ..domain.services import UserDomainService


class CreateUserUseCase:
    """Caso de uso para crear usuarios."""

    def __init__(
        self, domain_service: UserDomainService, audit_repository: AuditRepository
    ):
        self._domain_service = domain_service
        self._audit_repository = audit_repository

    def execute(
        self,
        username: str,
        email: str,
        password: str,
        user_type: str,
        first_name: str = "",
        last_name: str = "",
        phone: str = "",
        max_credits_per_semester: Optional[int] = None,
        academic_year: str = "2024-1",
        requesting_user: Optional[User] = None,
    ) -> Dict[str, Any]:
        """
        Crea un nuevo usuario.

        Args:
            username: Nombre de usuario
            email: Email
            password: Contraseña
            user_type: Tipo de usuario
            first_name: Nombre
            last_name: Apellido
            phone: Teléfono
            max_credits_per_semester: Créditos máximos por semestre
            academic_year: Año académico
            requesting_user: Usuario que solicita la creación

        Returns:
            Dict: Resultado de la creación
        """
        try:
            # Validar entrada
            username_vo = Username(username)
            email_vo = Email(email)
            password_vo = Password(password)
            user_type_vo = UserType(user_type)

            # Crear información académica si es estudiante
            academic_info = None
            if user_type_vo == UserType.STUDENT:
                academic_info = AcademicInfo(
                    max_credits_per_semester=max_credits_per_semester or 18,
                    current_semester_credits=0,
                    academic_year=academic_year,
                )

            # Crear usuario usando el servicio de dominio
            user = self._domain_service.create_user(
                username=username_vo,
                email=email_vo,
                password=password_vo,
                user_type=user_type_vo,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                academic_info=academic_info,
            )

            # Registrar auditoría
            if requesting_user:
                self._audit_repository.log_action(
                    user_id=requesting_user.id,
                    action_type="user_creation",
                    description=f"Created user {username} with type {user_type}",
                    content_object=user,
                    extra_data={
                        "created_user_id": user.id.value,
                        "user_type": user_type,
                    },
                )

            return {
                "success": True,
                "user": {
                    "id": user.id.value,
                    "username": user.username.value,
                    "email": user.email.value,
                    "user_type": user.user_type.value,
                    "full_name": user.full_name,
                    "status": user.status.value,
                },
                "message": "User created successfully",
            }

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": "User creation failed"}


class GetUserUseCase:
    """Caso de uso para obtener un usuario."""

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def execute(self, user_id: int, requesting_user: User) -> Dict[str, Any]:
        """
        Obtiene un usuario por ID.

        Args:
            user_id: ID del usuario
            requesting_user: Usuario que solicita la información

        Returns:
            Dict: Información del usuario
        """
        try:
            user = self._user_repository.find_by_id(UserId(user_id))
            if not user:
                raise ValueError("User not found")

            # Verificar permisos
            if not requesting_user.is_admin and user.id != requesting_user.id:
                raise ValueError("Insufficient permissions")

            return {
                "success": True,
                "user": {
                    "id": user.id.value,
                    "username": user.username.value,
                    "email": user.email.value,
                    "user_type": user.user_type.value,
                    "full_name": user.full_name,
                    "status": user.status.value,
                    "academic_info": (
                        user.get_academic_summary() if user.is_student else None
                    ),
                },
            }

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": "Failed to get user"}


class ListUsersUseCase:
    """Caso de uso para listar usuarios."""

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def execute(
        self,
        requesting_user: User,
        user_type: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Lista usuarios con filtros.

        Args:
            requesting_user: Usuario que solicita la lista
            user_type: Filtro por tipo de usuario
            status: Filtro por estado
            search: Texto de búsqueda
            limit: Límite de resultados
            offset: Offset para paginación

        Returns:
            Dict: Lista de usuarios
        """
        try:
            # Solo administradores pueden listar usuarios
            if not requesting_user.is_admin:
                raise ValueError("Insufficient permissions")

            # Convertir filtros a enums
            user_type_vo = UserType(user_type) if user_type else None
            status_vo = UserStatus(status) if status else None

            # Buscar usuarios
            if search:
                users = self._user_repository.search(search, user_type_vo)
            else:
                users = self._user_repository.find_all(limit, offset)

            # Aplicar filtro de estado
            if status_vo:
                users = [user for user in users if user.status == status_vo]

            # Aplicar límite
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
            }

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": "Failed to list users"}


class UpdateUserUseCase:
    """Caso de uso para actualizar usuarios."""

    def __init__(
        self, user_repository: UserRepository, audit_repository: AuditRepository
    ):
        self._user_repository = user_repository
        self._audit_repository = audit_repository

    def execute(
        self, user_id: int, requesting_user: User, **update_data
    ) -> Dict[str, Any]:
        """
        Actualiza un usuario.

        Args:
            user_id: ID del usuario a actualizar
            requesting_user: Usuario que solicita la actualización
            **update_data: Datos a actualizar

        Returns:
            Dict: Resultado de la actualización
        """
        try:
            user = self._user_repository.find_by_id(UserId(user_id))
            if not user:
                raise ValueError("User not found")

            # Verificar permisos
            if not requesting_user.is_admin and user.id != requesting_user.id:
                raise ValueError("Insufficient permissions")

            # Actualizar campos permitidos
            if "first_name" in update_data:
                user._first_name = update_data["first_name"]
            if "last_name" in update_data:
                user._last_name = update_data["last_name"]
            if "phone" in update_data:
                user._phone = update_data["phone"]

            # Solo administradores pueden cambiar tipo de usuario
            if "user_type" in update_data and requesting_user.is_admin:
                new_type = UserType(update_data["user_type"])
                user.change_user_type(new_type)

            # Guardar cambios
            updated_user = self._user_repository.save(user)

            # Registrar auditoría
            self._audit_repository.log_action(
                user_id=requesting_user.id,
                action_type="user_update",
                description=f"Updated user {user.username.value}",
                content_object=updated_user,
                extra_data={"updated_user_id": user.id.value, "changes": update_data},
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
                "message": "User updated successfully",
            }

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": "User update failed"}


class DeleteUserUseCase:
    """Caso de uso para eliminar usuarios."""

    def __init__(
        self, user_repository: UserRepository, audit_repository: AuditRepository
    ):
        self._user_repository = user_repository
        self._audit_repository = audit_repository

    def execute(self, user_id: int, requesting_user: User) -> Dict[str, Any]:
        """
        Elimina un usuario.

        Args:
            user_id: ID del usuario a eliminar
            requesting_user: Usuario que solicita la eliminación

        Returns:
            Dict: Resultado de la eliminación
        """
        try:
            # Solo administradores pueden eliminar usuarios
            if not requesting_user.is_admin:
                raise ValueError("Insufficient permissions")

            user = self._user_repository.find_by_id(UserId(user_id))
            if not user:
                raise ValueError("User not found")

            # No se puede eliminar a sí mismo
            if user.id == requesting_user.id:
                raise ValueError("Cannot delete yourself")

            # Eliminar usuario
            success = self._user_repository.delete(user.id)
            if not success:
                raise ValueError("Failed to delete user")

            # Registrar auditoría
            self._audit_repository.log_action(
                user_id=requesting_user.id,
                action_type="user_deletion",
                description=f"Deleted user {user.username.value}",
                content_object=user,
                extra_data={"deleted_user_id": user.id.value},
            )

            return {"success": True, "message": "User deleted successfully"}

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": "User deletion failed"}

