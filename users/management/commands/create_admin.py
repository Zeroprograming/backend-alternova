"""
Comando para crear usuarios administradores.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Crea un usuario administrador"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            help="Nombre de usuario",
            default="admin",
        )
        parser.add_argument(
            "--email",
            type=str,
            help="Correo electrónico",
            default="admin@alternova.com",
        )
        parser.add_argument(
            "--password",
            type=str,
            help="Contraseña",
            default="admin123",
        )
        parser.add_argument(
            "--first-name",
            type=str,
            help="Nombre",
            default="Administrador",
        )
        parser.add_argument(
            "--last-name",
            type=str,
            help="Apellido",
            default="Sistema",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options["password"]
        first_name = options["first_name"]
        last_name = options["last_name"]

        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"El usuario '{username}' ya existe"))
            return

        # Crear usuario administrador
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            user_type="admin",
            is_staff=True,
            is_superuser=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Usuario administrador '{username}' creado exitosamente"
            )
        )
        self.stdout.write(f"Email: {email}")
        self.stdout.write(f"Contraseña: {password}")
        self.stdout.write(
            self.style.WARNING(
                "¡IMPORTANTE! Cambia la contraseña después del primer login"
            )
        )
