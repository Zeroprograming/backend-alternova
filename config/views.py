from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection
from drf_spectacular.utils import extend_schema
import sys


@extend_schema(
    summary="Health Check",
    description="Endpoint para verificar el estado de salud de la API",
    tags=["Health"],
    responses={
        200: {
            "type": "object",
            "properties": {
                "status": {"type": "string", "example": "healthy"},
                "message": {"type": "string", "example": "API is running"},
                "version": {"type": "string", "example": "1.0.0"},
                "database": {"type": "string", "example": "connected"},
                "python_version": {"type": "string", "example": "3.12.0"},
            },
        }
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint para verificar que la API está funcionando correctamente.
    """

    # Verificar conexión a la base de datos
    try:
        connection.ensure_connection()
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return Response(
        {
            "status": "healthy",
            "message": "Alternova API is running",
            "version": "1.0.0",
            "database": db_status,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        }
    )
