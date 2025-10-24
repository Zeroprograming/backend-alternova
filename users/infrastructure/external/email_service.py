"""
Servicios externos para la capa de infraestructura.
Implementa servicios que interactúan con sistemas externos.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template import Template, Context
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio para envío de emails."""

    @staticmethod
    def send_email(
        to_email: str, subject: str, html_content: str, text_content: str = None
    ) -> bool:
        """
        Envía un email.

        Args:
            to_email: Email destinatario
            subject: Asunto del email
            html_content: Contenido HTML
            text_content: Contenido de texto plano

        Returns:
            bool: True si se envió exitosamente
        """
        try:
            if not text_content:
                text_content = "Please enable HTML to view this email."

            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[to_email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    @staticmethod
    def send_welcome_email(user_email: str, user_name: str, username: str) -> bool:
        """Envía email de bienvenida."""
        subject = "¡Bienvenido al Sistema Académico!"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Bienvenido</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ text-align: center; padding: 10px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>¡Bienvenido al Sistema Académico!</h1>
                </div>
                <div class="content">
                    <p>Hola {user_name},</p>
                    <p>Tu cuenta ha sido creada exitosamente en el Sistema Académico.</p>
                    <p><strong>Usuario:</strong> {username}</p>
                    <p><strong>Email:</strong> {user_email}</p>
                    <p>Puedes acceder al sistema usando tus credenciales.</p>
                    <p>Si tienes alguna pregunta, no dudes en contactar al administrador.</p>
                    <p>¡Bienvenido!</p>
                </div>
                <div class="footer">
                    <p>Sistema Académico</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        ¡Bienvenido al Sistema Académico!
        
        Hola {user_name},
        
        Tu cuenta ha sido creada exitosamente en el Sistema Académico.
        
        Usuario: {username}
        Email: {user_email}
        
        Puedes acceder al sistema usando tus credenciales.
        
        Si tienes alguna pregunta, no dudes en contactar al administrador.
        
        ¡Bienvenido!
        
        Sistema Académico
        """

        return EmailService.send_email(to_email, subject, html_content, text_content)

    @staticmethod
    def send_password_reset_email(
        user_email: str, user_name: str, reset_token: str
    ) -> bool:
        """Envía email de restablecimiento de contraseña."""
        subject = "Restablecimiento de Contraseña - Sistema Académico"

        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Restablecimiento de Contraseña</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #ff6b6b; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .button {{ display: inline-block; background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
                .footer {{ text-align: center; padding: 10px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Restablecimiento de Contraseña</h1>
                </div>
                <div class="content">
                    <p>Hola {user_name},</p>
                    <p>Has solicitado restablecer tu contraseña en el Sistema Académico.</p>
                    <p>Haz clic en el siguiente enlace para crear una nueva contraseña:</p>
                    <p><a href="{reset_url}" class="button">Restablecer Contraseña</a></p>
                    <p>Este enlace expirará en 24 horas.</p>
                    <p>Si no solicitaste este cambio, puedes ignorar este email.</p>
                </div>
                <div class="footer">
                    <p>Sistema Académico</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Restablecimiento de Contraseña - Sistema Académico
        
        Hola {user_name},
        
        Has solicitado restablecer tu contraseña en el Sistema Académico.
        
        Haz clic en el siguiente enlace para crear una nueva contraseña:
        {reset_url}
        
        Este enlace expirará en 24 horas.
        
        Si no solicitaste este cambio, puedes ignorar este email.
        
        Sistema Académico
        """

        return EmailService.send_email(user_email, subject, html_content, text_content)


class JWTService:
    """Servicio para manejo de tokens JWT."""

    @staticmethod
    def generate_tokens(user_id: int, username: str, user_type: str) -> Dict[str, str]:
        """
        Genera tokens JWT para un usuario.

        Args:
            user_id: ID del usuario
            username: Nombre de usuario
            user_type: Tipo de usuario

        Returns:
            Dict: Tokens de acceso y refresh
        """
        try:
            from rest_framework_simplejwt.tokens import RefreshToken

            # Crear token de refresh
            refresh = RefreshToken.for_user_id(user_id)

            # Agregar claims personalizados
            refresh["username"] = username
            refresh["user_type"] = user_type

            # Obtener token de acceso
            access = refresh.access_token
            access["username"] = username
            access["user_type"] = user_type

            return {"access": str(access), "refresh": str(refresh)}

        except Exception as e:
            logger.error(f"Failed to generate JWT tokens: {str(e)}")
            raise ValueError("Failed to generate tokens")

    @staticmethod
    def validate_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Valida un token JWT.

        Args:
            token: Token a validar

        Returns:
            Dict: Información del usuario o None si es inválido
        """
        try:
            from rest_framework_simplejwt.tokens import AccessToken

            access_token = AccessToken(token)

            return {
                "user_id": access_token["user_id"],
                "username": access_token.get("username"),
                "user_type": access_token.get("user_type"),
            }

        except Exception as e:
            logger.error(f"Failed to validate JWT token: {str(e)}")
            return None

    @staticmethod
    def refresh_token(refresh_token: str) -> Optional[Dict[str, str]]:
        """
        Refresca un token JWT.

        Args:
            refresh_token: Token de refresh

        Returns:
            Dict: Nuevos tokens o None si es inválido
        """
        try:
            from rest_framework_simplejwt.tokens import RefreshToken

            refresh = RefreshToken(refresh_token)
            access = refresh.access_token

            return {"access": str(access), "refresh": str(refresh)}

        except Exception as e:
            logger.error(f"Failed to refresh JWT token: {str(e)}")
            return None


class PasswordService:
    """Servicio para manejo de contraseñas."""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hashea una contraseña.

        Args:
            password: Contraseña en texto plano

        Returns:
            str: Contraseña hasheada
        """
        from django.contrib.auth.hashers import make_password

        return make_password(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verifica una contraseña.

        Args:
            password: Contraseña en texto plano
            hashed_password: Contraseña hasheada

        Returns:
            bool: True si la contraseña es correcta
        """
        from django.contrib.auth.hashers import check_password

        return check_password(password, hashed_password)

    @staticmethod
    def generate_reset_token() -> str:
        """
        Genera un token para restablecimiento de contraseña.

        Returns:
            str: Token único
        """
        import uuid

        return str(uuid.uuid4())

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """
        Valida la fortaleza de una contraseña.

        Args:
            password: Contraseña a validar

        Returns:
            Dict: Resultado de la validación
        """
        import re

        errors = []
        score = 0

        # Longitud mínima
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        else:
            score += 1

        # Contiene mayúsculas
        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")
        else:
            score += 1

        # Contiene minúsculas
        if not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")
        else:
            score += 1

        # Contiene números
        if not re.search(r"\d", password):
            errors.append("Password must contain at least one number")
        else:
            score += 1

        # Contiene caracteres especiales
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        else:
            score += 1

        # Determinar nivel de fortaleza
        if score <= 2:
            strength = "weak"
        elif score <= 4:
            strength = "medium"
        else:
            strength = "strong"

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "score": score,
            "strength": strength,
        }


class CacheService:
    """Servicio para manejo de caché."""

    @staticmethod
    def get(key: str) -> Optional[Any]:
        """
        Obtiene un valor del caché.

        Args:
            key: Clave del caché

        Returns:
            Any: Valor almacenado o None
        """
        try:
            from django.core.cache import cache

            return cache.get(key)
        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {str(e)}")
            return None

    @staticmethod
    def set(key: str, value: Any, timeout: int = 300) -> bool:
        """
        Almacena un valor en el caché.

        Args:
            key: Clave del caché
            value: Valor a almacenar
            timeout: Tiempo de expiración en segundos

        Returns:
            bool: True si se almacenó exitosamente
        """
        try:
            from django.core.cache import cache

            cache.set(key, value, timeout)
            return True
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {str(e)}")
            return False

    @staticmethod
    def delete(key: str) -> bool:
        """
        Elimina un valor del caché.

        Args:
            key: Clave del caché

        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            from django.core.cache import cache

            cache.delete(key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {str(e)}")
            return False

    @staticmethod
    def clear() -> bool:
        """
        Limpia todo el caché.

        Returns:
            bool: True si se limpió exitosamente
        """
        try:
            from django.core.cache import cache

            cache.clear()
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {str(e)}")
            return False

