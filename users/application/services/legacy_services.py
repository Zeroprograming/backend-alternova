"""
Servicios de lógica de negocio para usuarios.
Toda la lógica compleja debe estar aquí, NO en views ni serializers.
"""

from django.contrib.auth import authenticate
from django.db import transaction
from ...infrastructure.models import User, UserProfile
import logging

logger = logging.getLogger(__name__)


class UserService:
    """
    Servicio para gestión de usuarios.
    Contiene toda la lógica de negocio relacionada con usuarios.
    """

    @staticmethod
    @transaction.atomic
    def create_user(username, email, password, user_type="student", **extra_data):
        """
        Crea un nuevo usuario con su perfil.

        Args:
            username: Nombre de usuario
            email: Correo electrónico
            password: Contraseña
            user_type: Tipo de usuario (student, teacher, admin)
            **extra_data: Datos adicionales del usuario

        Returns:
            User: Usuario creado

        Raises:
            ValueError: Si los datos son inválidos
        """
        # Validar que el email no existe
        if User.objects.filter(email=email).exists():
            raise ValueError("El email ya está registrado")

        # Validar que el username no existe
        if User.objects.filter(username=username).exists():
            raise ValueError("El username ya existe")

        try:
            # Crear usuario
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                user_type=user_type,
                **extra_data,
            )

            # Crear perfil automáticamente
            UserProfile.objects.create(user=user)

            logger.info(f"Usuario creado: {username} ({user_type})")

            # Enviar email de bienvenida (tarea asíncrona)
            # from .tasks import send_welcome_email_task
            # send_welcome_email_task.delay(user.id)

            return user

        except Exception as e:
            logger.error(f"Error creando usuario: {str(e)}")
            raise ValueError(f"Error al crear usuario: {str(e)}")

    @staticmethod
    def authenticate_user(username, password):
        """
        Autentica un usuario.

        Args:
            username: Nombre de usuario o email
            password: Contraseña

        Returns:
            User o None: Usuario autenticado o None si falla
        """
        user = authenticate(username=username, password=password)

        if user and user.is_active:
            logger.info(f"Usuario autenticado: {username}")
            return user

        logger.warning(f"Intento de autenticación fallido: {username}")
        return None

    @staticmethod
    def update_user_profile(user, profile_data):
        """
        Actualiza el perfil de un usuario.

        Args:
            user: Usuario a actualizar
            profile_data: Diccionario con datos del perfil

        Returns:
            UserProfile: Perfil actualizado
        """
        try:
            profile = user.profile
            for key, value in profile_data.items():
                setattr(profile, key, value)
            profile.save()

            logger.info(f"Perfil actualizado para usuario: {user.username}")
            return profile

        except UserProfile.DoesNotExist:
            # Crear perfil si no existe
            profile = UserProfile.objects.create(user=user, **profile_data)
            logger.info(f"Perfil creado para usuario: {user.username}")
            return profile

    @staticmethod
    def deactivate_user(user):
        """
        Desactiva un usuario (soft delete).

        Args:
            user: Usuario a desactivar

        Returns:
            User: Usuario desactivado
        """
        user.is_active = False
        user.save()
        logger.info(f"Usuario desactivado: {user.username}")
        return user

    @staticmethod
    def activate_user(user):
        """
        Activa un usuario.

        Args:
            user: Usuario a activar

        Returns:
            User: Usuario activado
        """
        user.is_active = True
        user.save()
        logger.info(f"Usuario activado: {user.username}")
        return user

    @staticmethod
    def change_user_type(user, new_type):
        """
        Cambia el tipo de un usuario.

        Args:
            user: Usuario a modificar
            new_type: Nuevo tipo de usuario

        Returns:
            User: Usuario modificado

        Raises:
            ValueError: Si el tipo es inválido
        """
        valid_types = ["student", "teacher", "admin"]
        if new_type not in valid_types:
            raise ValueError(f"Tipo de usuario inválido. Use: {', '.join(valid_types)}")

        old_type = user.user_type
        user.user_type = new_type
        user.save()

        logger.info(
            f"Tipo de usuario cambiado: {user.username} ({old_type} -> {new_type})"
        )
        return user

    @staticmethod
    def get_users_by_type(user_type, active_only=True):
        """
        Obtiene usuarios por tipo.

        Args:
            user_type: Tipo de usuario a filtrar
            active_only: Solo usuarios activos

        Returns:
            QuerySet: Usuarios filtrados
        """
        queryset = User.objects.filter(user_type=user_type)
        if active_only:
            queryset = queryset.filter(is_active=True)
        return queryset

    @staticmethod
    def search_users(search_term):
        """
        Busca usuarios por nombre o email.

        Args:
            search_term: Término de búsqueda

        Returns:
            QuerySet: Usuarios encontrados
        """
        from django.db.models import Q

        return User.objects.filter(
            Q(username__icontains=search_term)
            | Q(email__icontains=search_term)
            | Q(first_name__icontains=search_term)
            | Q(last_name__icontains=search_term)
        )

    @staticmethod
    def list_users(requesting_user, user_type=None, search_term=None):
        """
        Lista usuarios con filtros.

        Args:
            requesting_user: Usuario que hace la petición
            user_type: Filtro opcional por tipo
            search_term: Término de búsqueda opcional

        Returns:
            QuerySet: Usuarios filtrados
        """
        # Admin ve todos, otros solo activos
        if requesting_user.is_staff:
            queryset = User.objects.all()
        else:
            queryset = User.objects.filter(is_active=True)

        # Filtro por tipo
        if user_type:
            queryset = queryset.filter(user_type=user_type)

        # Búsqueda
        if search_term:
            queryset = UserService.search_users(search_term)

        return queryset

    @staticmethod
    def retrieve_user(user_id, requesting_user):
        """
        Obtiene un usuario con control de privacidad.

        Args:
            user_id: ID del usuario a obtener
            requesting_user: Usuario que hace la petición

        Returns:
            tuple: (user, show_full_details)

        Raises:
            ValueError: Si el usuario no existe
        """
        try:
            user = User.objects.get(id=user_id)

            # Owner o admin ven detalles completos
            show_full_details = requesting_user == user or requesting_user.is_staff

            return user, show_full_details

        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")

    @staticmethod
    @transaction.atomic
    def update_user(user, data, requesting_user):
        """
        Actualiza un usuario con validaciones.

        Args:
            user: Usuario a actualizar
            data: Datos nuevos
            requesting_user: Usuario que hace la petición

        Returns:
            User: Usuario actualizado

        Raises:
            ValueError: Si hay errores de validación
            PermissionError: Si no tiene permisos
        """
        # Validar permisos
        if requesting_user != user and not requesting_user.is_staff:
            raise PermissionError("No tienes permiso para modificar este usuario")

        # Actualizar campos
        for key, value in data.items():
            setattr(user, key, value)

        user.save()

        logger.info(
            f"Usuario {user.username} actualizado por {requesting_user.username}"
        )

        # Notificación opcional
        # NotificationService.create_notification(
        #     user, "Perfil actualizado", "Tu perfil ha sido actualizado"
        # )

        return user

    @staticmethod
    def partial_update_user(user, data, requesting_user):
        """
        Actualiza parcialmente un usuario con validaciones.

        Args:
            user: Usuario a actualizar
            data: Datos nuevos (parciales)
            requesting_user: Usuario que hace la petición

        Returns:
            User: Usuario actualizado

        Raises:
            ValueError: Si hay campos protegidos o errores
            PermissionError: Si no tiene permisos
        """
        # Validar permisos
        if requesting_user != user and not requesting_user.is_staff:
            raise PermissionError("No tienes permiso para modificar este usuario")

        # Validar campos protegidos
        protected_fields = ["username", "email", "user_type"]
        for field in protected_fields:
            if field in data:
                raise ValueError(
                    f"El campo '{field}' no puede ser modificado. Usa el endpoint específico o contacta a un administrador."
                )

        # Actualizar campos permitidos
        for key, value in data.items():
            setattr(user, key, value)

        user.save()

        logger.info(f"Usuario {user.username} actualizado parcialmente")

        return user

    @staticmethod
    @transaction.atomic
    def delete_user(user, requesting_user):
        """
        Elimina (desactiva) un usuario con validaciones de negocio.

        Args:
            user: Usuario a eliminar
            requesting_user: Usuario que hace la petición

        Returns:
            User: Usuario desactivado

        Raises:
            ValueError: Si hay errores de validación
            PermissionError: Si no tiene permisos
        """
        # Validar que no es auto-eliminación
        if requesting_user == user:
            raise ValueError("No puedes eliminar tu propia cuenta")

        # Verificar inscripciones activas
        if user.enrollments.filter(is_active=True).exists():
            raise ValueError(
                "No se puede eliminar: el usuario tiene inscripciones activas. "
                "Primero debe darse de baja de las materias."
            )

        # Soft delete
        user.is_active = False
        user.save()

        logger.warning(
            f"Usuario {user.username} desactivado por {requesting_user.username}"
        )

        # Notificación opcional
        # from notifications.services import NotificationService
        # NotificationService.create_notification(
        #     user, "Cuenta desactivada", "Tu cuenta ha sido desactivada por un administrador"
        # )

        return user
