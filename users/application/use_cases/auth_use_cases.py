"""
Casos de uso para autenticación de usuarios.
Contiene la lógica de aplicación para operaciones de autenticación.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from ..domain.entities import User
from ..domain.value_objects import Username, Password, Email, UserId
from ..domain.repositories import UserRepository, UserSessionRepository, AuditRepository
from ..domain.services import UserDomainService


class LoginUseCase:
    """Caso de uso para login de usuarios."""

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

    def execute(
        self, username: str, password: str, ip_address: str, user_agent: str
    ) -> Dict[str, Any]:
        """
        Ejecuta el login de un usuario.

        Args:
            username: Nombre de usuario
            password: Contraseña
            ip_address: Dirección IP
            user_agent: User Agent del navegador

        Returns:
            Dict: Resultado del login con tokens y datos del usuario

        Raises:
            ValueError: Si las credenciales son inválidas
        """
        try:
            # Validar entrada
            username_vo = Username(username)
            password_vo = Password(password)

            # Autenticar usuario
            user = self._domain_service.authenticate_user(username_vo, password_vo)
            if not user:
                raise ValueError("Invalid credentials")

            # Crear sesión
            session_id = self._generate_session_id()
            session = self._session_repository.save(
                {
                    "session_id": session_id,
                    "user_id": user.id.value,
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "is_active": True,
                }
            )

            # Registrar auditoría
            self._audit_repository.log_login(user.id, ip_address, user_agent)

            # Generar tokens JWT (esto se haría en la capa de infraestructura)
            tokens = self._generate_jwt_tokens(user)

            return {
                "success": True,
                "user": {
                    "id": user.id.value,
                    "username": user.username.value,
                    "email": user.email.value,
                    "user_type": user.user_type.value,
                    "full_name": user.full_name,
                    "is_student": user.is_student,
                    "is_teacher": user.is_teacher,
                    "is_admin": user.is_admin,
                },
                "tokens": tokens,
                "session_id": session_id,
            }

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": "Login failed"}

    def _generate_session_id(self) -> str:
        """Genera un ID de sesión único."""
        import uuid

        return str(uuid.uuid4())

    def _generate_jwt_tokens(self, user: User) -> Dict[str, str]:
        """Genera tokens JWT para el usuario."""
        # Esta implementación se haría en la capa de infraestructura
        return {"access": "mock_access_token", "refresh": "mock_refresh_token"}


class LogoutUseCase:
    """Caso de uso para logout de usuarios."""

    def __init__(
        self,
        session_repository: UserSessionRepository,
        audit_repository: AuditRepository,
    ):
        self._session_repository = session_repository
        self._audit_repository = audit_repository

    def execute(self, session_id: str, user_id: UserId) -> Dict[str, Any]:
        """
        Ejecuta el logout de un usuario.

        Args:
            session_id: ID de la sesión
            user_id: ID del usuario

        Returns:
            Dict: Resultado del logout
        """
        try:
            # Buscar sesión
            session = self._session_repository.find_by_session_id(session_id)
            if not session:
                raise ValueError("Session not found")

            # Eliminar sesión
            self._session_repository.delete(session_id)

            # Registrar auditoría
            self._audit_repository.log_logout(user_id, session_id)

            return {"success": True, "message": "Logout successful"}

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": "Logout failed"}


class RefreshTokenUseCase:
    """Caso de uso para refrescar tokens JWT."""

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def execute(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresca un token JWT.

        Args:
            refresh_token: Token de refresh

        Returns:
            Dict: Nuevos tokens
        """
        try:
            # Validar refresh token (esto se haría en la capa de infraestructura)
            user_id = self._validate_refresh_token(refresh_token)
            if not user_id:
                raise ValueError("Invalid refresh token")

            # Buscar usuario
            user = self._user_repository.find_by_id(UserId(user_id))
            if not user:
                raise ValueError("User not found")

            # Generar nuevos tokens
            new_tokens = self._generate_jwt_tokens(user)

            return {"success": True, "tokens": new_tokens}

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": "Token refresh failed"}

    def _validate_refresh_token(self, token: str) -> Optional[int]:
        """Valida un refresh token y retorna el user_id."""
        # Esta implementación se haría en la capa de infraestructura
        return 1  # Mock implementation

    def _generate_jwt_tokens(self, user: User) -> Dict[str, str]:
        """Genera tokens JWT para el usuario."""
        # Esta implementación se haría en la capa de infraestructura
        return {"access": "mock_access_token", "refresh": "mock_refresh_token"}


class VerifyTokenUseCase:
    """Caso de uso para verificar tokens JWT."""

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def execute(self, access_token: str) -> Dict[str, Any]:
        """
        Verifica un token JWT.

        Args:
            access_token: Token de acceso

        Returns:
            Dict: Resultado de la verificación
        """
        try:
            # Validar access token (esto se haría en la capa de infraestructura)
            user_id = self._validate_access_token(access_token)
            if not user_id:
                raise ValueError("Invalid access token")

            # Buscar usuario
            user = self._user_repository.find_by_id(UserId(user_id))
            if not user:
                raise ValueError("User not found")

            return {
                "success": True,
                "user": {
                    "id": user.id.value,
                    "username": user.username.value,
                    "email": user.email.value,
                    "user_type": user.user_type.value,
                    "full_name": user.full_name,
                },
            }

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": "Token verification failed"}

    def _validate_access_token(self, token: str) -> Optional[int]:
        """Valida un access token y retorna el user_id."""
        # Esta implementación se haría en la capa de infraestructura
        return 1  # Mock implementation

