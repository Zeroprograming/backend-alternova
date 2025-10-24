"""
Utilidades y funciones helper comunes.
"""

from django.utils import timezone
from datetime import datetime, timedelta
import random
import string


def generate_random_code(length=8, uppercase=True):
    """
    Genera un código aleatorio.

    Args:
        length: Longitud del código
        uppercase: Si debe ser en mayúsculas

    Returns:
        str: Código generado
    """
    characters = (
        string.ascii_uppercase + string.digits
        if uppercase
        else string.ascii_letters + string.digits
    )
    code = "".join(random.choice(characters) for _ in range(length))
    return code


def format_phone_number(phone):
    """
    Formatea un número de teléfono.

    Args:
        phone: Número de teléfono sin formato

    Returns:
        str: Número formateado
    """
    # Eliminar caracteres no numéricos
    digits = "".join(filter(str.isdigit, phone))

    # Formatear según longitud
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return digits


def calculate_age(birth_date):
    """
    Calcula la edad a partir de una fecha de nacimiento.

    Args:
        birth_date: Fecha de nacimiento

    Returns:
        int: Edad en años
    """
    today = timezone.now().date()
    return (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )


def get_date_range(range_type="week"):
    """
    Obtiene un rango de fechas según el tipo especificado.

    Args:
        range_type: 'today', 'week', 'month', 'year'

    Returns:
        tuple: (fecha_inicio, fecha_fin)
    """
    now = timezone.now()

    if range_type == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif range_type == "week":
        start = now - timedelta(days=now.weekday())
        end = now
    elif range_type == "month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif range_type == "year":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    else:
        start = now - timedelta(days=7)
        end = now

    return start, end


def truncate_text(text, max_length=100, suffix="..."):
    """
    Trunca un texto a una longitud máxima.

    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo a agregar si se trunca

    Returns:
        str: Texto truncado
    """
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + suffix


def clean_dict(data):
    """
    Limpia un diccionario eliminando valores None y cadenas vacías.

    Args:
        data: Diccionario a limpiar

    Returns:
        dict: Diccionario limpio
    """
    return {k: v for k, v in data.items() if v is not None and v != ""}


def get_client_ip(request):
    """
    Obtiene la IP del cliente desde el request.

    Args:
        request: Django request object

    Returns:
        str: IP del cliente
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def serialize_datetime(dt):
    """
    Serializa un objeto datetime a string ISO format.

    Args:
        dt: Objeto datetime

    Returns:
        str: Datetime en formato ISO
    """
    if dt:
        return dt.isoformat()
    return None


def parse_datetime(dt_string):
    """
    Parsea un string a objeto datetime.

    Args:
        dt_string: String en formato ISO

    Returns:
        datetime: Objeto datetime
    """
    try:
        return datetime.fromisoformat(dt_string)
    except (ValueError, AttributeError):
        return None


class QueryHelper:
    """
    Helper para construir queries complejas.
    """

    @staticmethod
    def build_filter_from_params(params, allowed_fields):
        """
        Construye un diccionario de filtros desde parámetros de query.

        Args:
            params: QueryDict con parámetros
            allowed_fields: Lista de campos permitidos para filtrar

        Returns:
            dict: Diccionario de filtros
        """
        filters = {}
        for field in allowed_fields:
            value = params.get(field)
            if value:
                filters[field] = value
        return filters

    @staticmethod
    def apply_search(queryset, search_term, search_fields):
        """
        Aplica búsqueda en múltiples campos.

        Args:
            queryset: QuerySet a filtrar
            search_term: Término de búsqueda
            search_fields: Lista de campos donde buscar

        Returns:
            QuerySet: QuerySet filtrado
        """
        from django.db.models import Q

        if not search_term:
            return queryset

        query = Q()
        for field in search_fields:
            query |= Q(**{f"{field}__icontains": search_term})

        return queryset.filter(query)
