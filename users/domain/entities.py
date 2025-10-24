"""
Entidades de dominio para usuarios.
Contiene la lógica de negocio pura sin dependencias externas.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class UserType(Enum):
    """Tipos de usuario en el sistema."""

    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class UserStatus(Enum):
    """Estados de usuario."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


@dataclass
class UserId:
    """Value Object para ID de usuario."""

    value: int

    def __post_init__(self):
        if not isinstance(self.value, int) or self.value <= 0:
            raise ValueError("User ID must be a positive integer")


@dataclass
class Email:
    """Value Object para email."""

    value: str

    def __post_init__(self):
        if not self.value or "@" not in self.value:
            raise ValueError("Invalid email format")
        self.value = self.value.lower().strip()


@dataclass
class Username:
    """Value Object para nombre de usuario."""

    value: str

    def __post_init__(self):
        if not self.value or len(self.value) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not self.value.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Username can only contain letters, numbers, hyphens and underscores"
            )


@dataclass
class AcademicInfo:
    """Value Object para información académica."""

    max_credits_per_semester: int
    current_semester_credits: int
    academic_year: str

    def __post_init__(self):
        if self.max_credits_per_semester < 0:
            raise ValueError("Max credits per semester must be positive")
        if self.current_semester_credits < 0:
            raise ValueError("Current semester credits must be positive")
        if self.current_semester_credits > self.max_credits_per_semester:
            raise ValueError("Current credits cannot exceed max credits per semester")


class User:
    """
    Entidad de dominio User.
    Contiene toda la lógica de negocio relacionada con usuarios.
    """

    def __init__(
        self,
        user_id: UserId,
        username: Username,
        email: Email,
        user_type: UserType,
        academic_info: Optional[AcademicInfo] = None,
        first_name: str = "",
        last_name: str = "",
        phone: str = "",
        status: UserStatus = UserStatus.ACTIVE,
    ):
        self._id = user_id
        self._username = username
        self._email = email
        self._user_type = user_type
        self._academic_info = academic_info
        self._first_name = first_name
        self._last_name = last_name
        self._phone = phone
        self._status = status

    @property
    def id(self) -> UserId:
        return self._id

    @property
    def username(self) -> Username:
        return self._username

    @property
    def email(self) -> Email:
        return self._email

    @property
    def user_type(self) -> UserType:
        return self._user_type

    @property
    def academic_info(self) -> Optional[AcademicInfo]:
        return self._academic_info

    @property
    def status(self) -> UserStatus:
        return self._status

    @property
    def full_name(self) -> str:
        """Retorna el nombre completo del usuario."""
        if self._first_name and self._last_name:
            return f"{self._first_name} {self._last_name}"
        return self._username.value

    @property
    def is_student(self) -> bool:
        """Verifica si el usuario es estudiante."""
        return self._user_type == UserType.STUDENT

    @property
    def is_teacher(self) -> bool:
        """Verifica si el usuario es profesor."""
        return self._user_type == UserType.TEACHER

    @property
    def is_admin(self) -> bool:
        """Verifica si el usuario es administrador."""
        return self._user_type == UserType.ADMIN

    @property
    def available_credits(self) -> int:
        """Calcula los créditos disponibles del estudiante."""
        if not self._academic_info or not self.is_student:
            return 0
        return (
            self._academic_info.max_credits_per_semester
            - self._academic_info.current_semester_credits
        )

    def can_enroll_subject(self, subject_credits: int) -> bool:
        """
        Verifica si el usuario puede inscribirse en una materia.

        Args:
            subject_credits: Créditos de la materia

        Returns:
            bool: True si puede inscribirse
        """
        if not self.is_student or self._status != UserStatus.ACTIVE:
            return False

        if not self._academic_info:
            return False

        return self.available_credits >= subject_credits

    def enroll_subject(self, subject_credits: int) -> None:
        """
        Inscribe al usuario en una materia.

        Args:
            subject_credits: Créditos de la materia

        Raises:
            ValueError: Si no puede inscribirse
        """
        if not self.can_enroll_subject(subject_credits):
            raise ValueError(
                "Cannot enroll in subject: insufficient credits or invalid status"
            )

        self._academic_info.current_semester_credits += subject_credits

    def change_user_type(self, new_type: UserType) -> None:
        """
        Cambia el tipo de usuario.

        Args:
            new_type: Nuevo tipo de usuario

        Raises:
            ValueError: Si el cambio no es válido
        """
        if self._user_type == new_type:
            return

        # Validar transiciones válidas
        valid_transitions = {
            UserType.STUDENT: [UserType.TEACHER, UserType.ADMIN],
            UserType.TEACHER: [UserType.ADMIN],
            UserType.ADMIN: [],  # Los admins no pueden cambiar de tipo
        }

        if new_type not in valid_transitions.get(self._user_type, []):
            raise ValueError(
                f"Cannot change from {self._user_type.value} to {new_type.value}"
            )

        self._user_type = new_type

    def activate(self) -> None:
        """Activa el usuario."""
        self._status = UserStatus.ACTIVE

    def deactivate(self) -> None:
        """Desactiva el usuario."""
        self._status = UserStatus.INACTIVE

    def suspend(self) -> None:
        """Suspende el usuario."""
        self._status = UserStatus.SUSPENDED

    def update_academic_info(self, academic_info: AcademicInfo) -> None:
        """
        Actualiza la información académica del usuario.

        Args:
            academic_info: Nueva información académica
        """
        if not self.is_student:
            raise ValueError("Only students can have academic information")

        self._academic_info = academic_info

    def get_academic_summary(self) -> dict:
        """
        Retorna un resumen académico del usuario.

        Returns:
            dict: Resumen académico
        """
        if not self.is_student or not self._academic_info:
            return {}

        return {
            "max_credits_per_semester": self._academic_info.max_credits_per_semester,
            "current_semester_credits": self._academic_info.current_semester_credits,
            "available_credits": self.available_credits,
            "academic_year": self._academic_info.academic_year,
            "can_enroll": self.available_credits > 0,
        }


class UserProfile:
    """
    Entidad de dominio UserProfile.
    Contiene información adicional del usuario.
    """

    def __init__(
        self,
        user: User,
        address: str = "",
        city: str = "",
        country: str = "",
        emergency_contact_name: str = "",
        emergency_contact_phone: str = "",
    ):
        self._user = user
        self._address = address
        self._city = city
        self._country = country
        self._emergency_contact_name = emergency_contact_name
        self._emergency_contact_phone = emergency_contact_phone

    @property
    def user(self) -> User:
        return self._user

    @property
    def address(self) -> str:
        return self._address

    @property
    def city(self) -> str:
        return self._city

    @property
    def country(self) -> str:
        return self._country

    @property
    def emergency_contact_name(self) -> str:
        return self._emergency_contact_name

    @property
    def emergency_contact_phone(self) -> str:
        return self._emergency_contact_phone

    def update_contact_info(
        self,
        address: str = "",
        city: str = "",
        country: str = "",
        emergency_contact_name: str = "",
        emergency_contact_phone: str = "",
    ) -> None:
        """Actualiza la información de contacto."""
        if address:
            self._address = address
        if city:
            self._city = city
        if country:
            self._country = country
        if emergency_contact_name:
            self._emergency_contact_name = emergency_contact_name
        if emergency_contact_phone:
            self._emergency_contact_phone = emergency_contact_phone

    def get_full_address(self) -> str:
        """Retorna la dirección completa."""
        parts = [self._address, self._city, self._country]
        return ", ".join(filter(None, parts))
