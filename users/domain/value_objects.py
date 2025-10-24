"""
Value Objects para el dominio de usuarios.
Objetos inmutables que representan conceptos del dominio.
"""

from dataclasses import dataclass
from typing import Optional
import re
from datetime import date


@dataclass(frozen=True)
class Password:
    """Value Object para contraseñas."""

    value: str

    def __post_init__(self):
        if not self.value or len(self.value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", self.value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", self.value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", self.value):
            raise ValueError("Password must contain at least one digit")


@dataclass(frozen=True)
class PhoneNumber:
    """Value Object para números de teléfono."""

    value: str

    def __post_init__(self):
        if not self.value:
            return  # Phone is optional

        # Remove all non-digit characters
        digits_only = re.sub(r"\D", "", self.value)

        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError("Phone number must be between 10 and 15 digits")

        # Store the cleaned version
        object.__setattr__(self, "value", digits_only)

    def format_phone(self) -> str:
        """Formatea el número de teléfono para mostrar."""
        if len(self.value) == 10:
            return f"({self.value[:3]}) {self.value[3:6]}-{self.value[6:]}"
        elif len(self.value) == 11:
            return f"+{self.value[0]} ({self.value[1:4]}) {self.value[4:7]}-{self.value[7:]}"
        return self.value


@dataclass(frozen=True)
class BirthDate:
    """Value Object para fechas de nacimiento."""

    value: date

    def __post_init__(self):
        today = date.today()
        age = (
            today.year
            - self.value.year
            - ((today.month, today.day) < (self.value.month, self.value.day))
        )

        if age < 13:
            raise ValueError("User must be at least 13 years old")
        if age > 120:
            raise ValueError("Invalid birth date")

    @property
    def age(self) -> int:
        """Calcula la edad del usuario."""
        today = date.today()
        return (
            today.year
            - self.value.year
            - ((today.month, today.day) < (self.value.month, self.value.day))
        )


@dataclass(frozen=True)
class AcademicYear:
    """Value Object para años académicos."""

    value: str

    def __post_init__(self):
        # Format: YYYY-S (e.g., 2024-1, 2024-2)
        if not re.match(r"^\d{4}-[12]$", self.value):
            raise ValueError("Academic year must be in format YYYY-S (e.g., 2024-1)")

        year, semester = self.value.split("-")
        year_int = int(year)
        semester_int = int(semester)

        if year_int < 2020 or year_int > 2030:
            raise ValueError("Academic year must be between 2020 and 2030")
        if semester_int not in [1, 2]:
            raise ValueError("Semester must be 1 or 2")

    @property
    def year(self) -> int:
        """Retorna el año."""
        return int(self.value.split("-")[0])

    @property
    def semester(self) -> int:
        """Retorna el semestre."""
        return int(self.value.split("-")[1])

    def next_semester(self) -> "AcademicYear":
        """Retorna el siguiente semestre académico."""
        year, semester = self.value.split("-")
        year_int = int(year)
        semester_int = int(semester)

        if semester_int == 1:
            return AcademicYear(f"{year_int}-2")
        else:
            return AcademicYear(f"{year_int + 1}-1")


@dataclass(frozen=True)
class Credits:
    """Value Object para créditos académicos."""

    value: int

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Credits cannot be negative")
        if self.value > 30:
            raise ValueError("Credits cannot exceed 30 per semester")

    def __add__(self, other: "Credits") -> "Credits":
        """Suma créditos."""
        return Credits(self.value + other.value)

    def __sub__(self, other: "Credits") -> "Credits":
        """Resta créditos."""
        return Credits(self.value - other.value)

    def __lt__(self, other: "Credits") -> bool:
        """Compara si es menor."""
        return self.value < other.value

    def __le__(self, other: "Credits") -> bool:
        """Compara si es menor o igual."""
        return self.value <= other.value

    def __gt__(self, other: "Credits") -> bool:
        """Compara si es mayor."""
        return self.value > other.value

    def __ge__(self, other: "Credits") -> bool:
        """Compara si es mayor o igual."""
        return self.value >= other.value


@dataclass(frozen=True)
class Grade:
    """Value Object para calificaciones."""

    value: float

    def __post_init__(self):
        if not 0.0 <= self.value <= 5.0:
            raise ValueError("Grade must be between 0.0 and 5.0")

    @property
    def is_passing(self) -> bool:
        """Verifica si la calificación es aprobatoria."""
        return self.value >= 3.0

    @property
    def letter_grade(self) -> str:
        """Retorna la calificación en letras."""
        if self.value >= 4.5:
            return "A"
        elif self.value >= 4.0:
            return "B"
        elif self.value >= 3.5:
            return "C"
        elif self.value >= 3.0:
            return "D"
        else:
            return "F"

    def __str__(self) -> str:
        return f"{self.value:.1f}"


@dataclass(frozen=True)
class UserSession:
    """Value Object para sesiones de usuario."""

    session_id: str
    user_id: int
    ip_address: str
    user_agent: str
    created_at: date
    last_activity: date
    is_active: bool = True

    def __post_init__(self):
        if not self.session_id:
            raise ValueError("Session ID cannot be empty")
        if self.user_id <= 0:
            raise ValueError("User ID must be positive")
        if not self.ip_address:
            raise ValueError("IP address cannot be empty")

    def is_expired(self, max_inactivity_hours: int = 24) -> bool:
        """Verifica si la sesión ha expirado."""
        from datetime import datetime, timedelta

        now = datetime.now()
        last_activity = datetime.combine(self.last_activity, datetime.min.time())
        return (now - last_activity).total_seconds() > max_inactivity_hours * 3600

    def extend_session(self) -> "UserSession":
        """Extiende la sesión con nueva actividad."""
        from datetime import date

        return UserSession(
            session_id=self.session_id,
            user_id=self.user_id,
            ip_address=self.ip_address,
            user_agent=self.user_agent,
            created_at=self.created_at,
            last_activity=date.today(),
            is_active=True,
        )
