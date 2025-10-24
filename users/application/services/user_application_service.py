"""
Servicios de aplicación para usuarios.
Contiene la lógica de aplicación que coordina casos de uso.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..domain.entities import User
from ..domain.value_objects import (
    UserId,
    Username,
    Email,
    Password,
    UserType,
    UserStatus,
)
from ..domain.repositories import (
    UserRepository,
    UserProfileRepository,
    UserSessionRepository,
    AuditRepository,
)
from ..domain.services import UserDomainService, AcademicDomainService
from .use_cases.auth_use_cases import (
    LoginUseCase,
    LogoutUseCase,
    RefreshTokenUseCase,
    VerifyTokenUseCase,
)
from .use_cases.user_use_cases import (
    CreateUserUseCase,
    GetUserUseCase,
    ListUsersUseCase,
    UpdateUserUseCase,
    DeleteUserUseCase,
)
from .use_cases.role_use_cases import (
    AssignRoleUseCase,
    BulkAssignRoleUseCase,
    GetUsersByRoleUseCase,
    GetRoleStatisticsUseCase,
    DeactivateUserUseCase,
    ActivateUserUseCase,
)


class UserApplicationService:
    """Servicio de aplicación para gestión de usuarios."""

    def __init__(
        self,
        user_repository: UserRepository,
        profile_repository: UserProfileRepository,
        session_repository: UserSessionRepository,
        audit_repository: AuditRepository,
        domain_service: UserDomainService,
    ):
        self._user_repository = user_repository
        self._profile_repository = profile_repository
        self._session_repository = session_repository
        self._audit_repository = audit_repository
        self._domain_service = domain_service

        # Inicializar casos de uso
        self._create_user_use_case = CreateUserUseCase(domain_service, audit_repository)
        self._get_user_use_case = GetUserUseCase(user_repository)
        self._list_users_use_case = ListUsersUseCase(user_repository)
        self._update_user_use_case = UpdateUserUseCase(
            user_repository, audit_repository
        )
        self._delete_user_use_case = DeleteUserUseCase(
            user_repository, audit_repository
        )

    def create_user(
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
        """Crea un nuevo usuario."""
        return self._create_user_use_case.execute(
            username=username,
            email=email,
            password=password,
            user_type=user_type,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            max_credits_per_semester=max_credits_per_semester,
            academic_year=academic_year,
            requesting_user=requesting_user,
        )

    def get_user(self, user_id: int, requesting_user: User) -> Dict[str, Any]:
        """Obtiene un usuario por ID."""
        return self._get_user_use_case.execute(user_id, requesting_user)

    def list_users(
        self,
        requesting_user: User,
        user_type: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Lista usuarios con filtros."""
        return self._list_users_use_case.execute(
            requesting_user=requesting_user,
            user_type=user_type,
            status=status,
            search=search,
            limit=limit,
            offset=offset,
        )

    def update_user(
        self, user_id: int, requesting_user: User, **update_data
    ) -> Dict[str, Any]:
        """Actualiza un usuario."""
        return self._update_user_use_case.execute(
            user_id=user_id, requesting_user=requesting_user, **update_data
        )

    def delete_user(self, user_id: int, requesting_user: User) -> Dict[str, Any]:
        """Elimina un usuario."""
        return self._delete_user_use_case.execute(user_id, requesting_user)

    def get_user_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de usuarios."""
        return self._domain_service.get_user_statistics()

    def search_users(
        self,
        query: str,
        user_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[User]:
        """Busca usuarios con filtros."""
        user_type_vo = UserType(user_type) if user_type else None
        status_vo = UserStatus(status) if status else None

        return self._domain_service.search_users(
            query=query, user_type=user_type_vo, status=status_vo, limit=limit
        )


class AuthApplicationService:
    """Servicio de aplicación para autenticación."""

    def __init__(
        self,
        user_repository: UserRepository,
        session_repository: UserSessionRepository,
        audit_repository: AuditRepository,
        domain_service: UserDomainService,
    ):
        self._user_repository = user_repository
        self._session_repository = session_repository
        self._audit_repository = audit_repository
        self._domain_service = domain_service

        # Inicializar casos de uso
        self._login_use_case = LoginUseCase(
            user_repository, session_repository, audit_repository, domain_service
        )
        self._logout_use_case = LogoutUseCase(session_repository, audit_repository)
        self._refresh_token_use_case = RefreshTokenUseCase(user_repository)
        self._verify_token_use_case = VerifyTokenUseCase(user_repository)

    def login(
        self, username: str, password: str, ip_address: str, user_agent: str
    ) -> Dict[str, Any]:
        """Realiza login de usuario."""
        return self._login_use_case.execute(username, password, ip_address, user_agent)

    def logout(self, session_id: str, user_id: int) -> Dict[str, Any]:
        """Realiza logout de usuario."""
        return self._logout_use_case.execute(session_id, UserId(user_id))

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresca un token JWT."""
        return self._refresh_token_use_case.execute(refresh_token)

    def verify_token(self, access_token: str) -> Dict[str, Any]:
        """Verifica un token JWT."""
        return self._verify_token_use_case.execute(access_token)

    def get_active_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtiene sesiones activas de un usuario."""
        sessions = self._session_repository.find_active_sessions(UserId(user_id))

        return [
            {
                "session_id": session.get("session_id"),
                "ip_address": session.get("ip_address"),
                "user_agent": session.get("user_agent"),
                "created_at": session.get("created_at"),
                "last_activity": session.get("last_activity"),
                "is_active": session.get("is_active", True),
            }
            for session in sessions
        ]

    def revoke_session(self, session_id: str, user_id: int) -> Dict[str, Any]:
        """Revoca una sesión específica."""
        try:
            success = self._session_repository.delete(session_id)
            if success:
                self._audit_repository.log_action(
                    user_id=UserId(user_id),
                    action_type="session_revocation",
                    description=f"Revoked session {session_id}",
                    extra_data={"session_id": session_id},
                )
                return {"success": True, "message": "Session revoked successfully"}
            else:
                return {"success": False, "error": "Session not found"}
        except Exception as e:
            return {"success": False, "error": "Failed to revoke session"}

    def revoke_all_sessions(self, user_id: int) -> Dict[str, Any]:
        """Revoca todas las sesiones de un usuario."""
        try:
            count = self._session_repository.delete_all_user_sessions(UserId(user_id))
            self._audit_repository.log_action(
                user_id=UserId(user_id),
                action_type="all_sessions_revocation",
                description=f"Revoked all sessions for user {user_id}",
                extra_data={"revoked_count": count},
            )
            return {"success": True, "message": f"Revoked {count} sessions"}
        except Exception as e:
            return {"success": False, "error": "Failed to revoke sessions"}


class RoleApplicationService:
    """Servicio de aplicación para gestión de roles."""

    def __init__(
        self,
        user_repository: UserRepository,
        audit_repository: AuditRepository,
        domain_service: UserDomainService,
    ):
        self._user_repository = user_repository
        self._audit_repository = audit_repository
        self._domain_service = domain_service

        # Inicializar casos de uso
        self._assign_role_use_case = AssignRoleUseCase(domain_service, audit_repository)
        self._bulk_assign_role_use_case = BulkAssignRoleUseCase(
            domain_service, audit_repository
        )
        self._get_users_by_role_use_case = GetUsersByRoleUseCase(user_repository)
        self._get_role_statistics_use_case = GetRoleStatisticsUseCase(domain_service)
        self._deactivate_user_use_case = DeactivateUserUseCase(
            domain_service, audit_repository
        )
        self._activate_user_use_case = ActivateUserUseCase(
            domain_service, audit_repository
        )

    def assign_role(
        self, user_id: int, new_role: str, requesting_user: User
    ) -> Dict[str, Any]:
        """Asigna un rol a un usuario."""
        return self._assign_role_use_case.execute(user_id, new_role, requesting_user)

    def bulk_assign_role(
        self, user_ids: List[int], new_role: str, requesting_user: User
    ) -> Dict[str, Any]:
        """Asigna un rol a múltiples usuarios."""
        return self._bulk_assign_role_use_case.execute(
            user_ids, new_role, requesting_user
        )

    def get_users_by_role(
        self,
        role: str,
        requesting_user: User,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Obtiene usuarios por rol."""
        return self._get_users_by_role_use_case.execute(
            role, requesting_user, limit, offset
        )

    def get_role_statistics(self, requesting_user: User) -> Dict[str, Any]:
        """Obtiene estadísticas de roles."""
        return self._get_role_statistics_use_case.execute(requesting_user)

    def deactivate_user(self, user_id: int, requesting_user: User) -> Dict[str, Any]:
        """Desactiva un usuario."""
        return self._deactivate_user_use_case.execute(user_id, requesting_user)

    def activate_user(self, user_id: int, requesting_user: User) -> Dict[str, Any]:
        """Activa un usuario."""
        return self._activate_user_use_case.execute(user_id, requesting_user)

    def get_user_permissions(self, user_id: int) -> Dict[str, Any]:
        """Obtiene permisos de un usuario."""
        try:
            user = self._user_repository.find_by_id(UserId(user_id))
            if not user:
                return {"success": False, "error": "User not found"}

            # Definir permisos por rol
            permissions = {
                "admin": ["all"],
                "teacher": [
                    "view_subjects",
                    "assign_grades",
                    "view_students",
                    "create_reports",
                    "view_own_data",
                ],
                "student": [
                    "view_own_data",
                    "enroll_subjects",
                    "view_grades",
                    "view_notifications",
                ],
            }

            return {
                "success": True,
                "user_id": user_id,
                "user_type": user.user_type.value,
                "permissions": permissions.get(user.user_type.value, []),
                "is_active": user.status.value == "active",
            }

        except Exception as e:
            return {"success": False, "error": "Failed to get user permissions"}


class AcademicApplicationService:
    """Servicio de aplicación para lógica académica."""

    def __init__(
        self,
        user_repository: UserRepository,
        academic_domain_service: AcademicDomainService,
    ):
        self._user_repository = user_repository
        self._academic_domain_service = academic_domain_service

    def can_student_enroll(
        self, student_id: int, subject_credits: int
    ) -> Dict[str, Any]:
        """Verifica si un estudiante puede inscribirse en una materia."""
        try:
            can_enroll = self._academic_domain_service.can_student_enroll(
                UserId(student_id), subject_credits
            )

            return {
                "success": True,
                "can_enroll": can_enroll,
                "student_id": student_id,
                "subject_credits": subject_credits,
            }

        except Exception as e:
            return {"success": False, "error": "Failed to check enrollment eligibility"}

    def enroll_student(self, student_id: int, subject_credits: int) -> Dict[str, Any]:
        """Inscribe un estudiante en una materia."""
        try:
            updated_student = self._academic_domain_service.enroll_student(
                UserId(student_id), subject_credits
            )

            return {
                "success": True,
                "student": {
                    "id": updated_student.id.value,
                    "username": updated_student.username.value,
                    "academic_info": updated_student.get_academic_summary(),
                },
                "message": "Student enrolled successfully",
            }

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": "Enrollment failed"}

    def get_student_academic_summary(self, student_id: int) -> Dict[str, Any]:
        """Obtiene resumen académico de un estudiante."""
        try:
            summary = self._academic_domain_service.get_student_academic_summary(
                UserId(student_id)
            )

            return {
                "success": True,
                "student_id": student_id,
                "academic_summary": summary,
            }

        except Exception as e:
            return {"success": False, "error": "Failed to get academic summary"}

    def get_students_by_credits_range(
        self, min_credits: int, max_credits: int
    ) -> Dict[str, Any]:
        """Busca estudiantes por rango de créditos."""
        try:
            students = self._academic_domain_service.get_students_by_credits_range(
                min_credits, max_credits
            )

            return {
                "success": True,
                "students": [
                    {
                        "id": student.id.value,
                        "username": student.username.value,
                        "email": student.email.value,
                        "full_name": student.full_name,
                        "academic_info": student.get_academic_summary(),
                    }
                    for student in students
                ],
                "total": len(students),
                "credits_range": f"{min_credits}-{max_credits}",
            }

        except Exception as e:
            return {
                "success": False,
                "error": "Failed to get students by credits range",
            }

