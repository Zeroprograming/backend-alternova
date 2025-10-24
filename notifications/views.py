"""
Views para notificaciones.
SOLO enrutamiento - Toda la lógica en NotificationService.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Notification
from .serializers import NotificationSerializer
from .services import NotificationService
import logging

logger = logging.getLogger(__name__)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de notificaciones con JWT y validaciones.
    La lógica compleja está delegada en NotificationService.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Solo notificaciones del usuario actual."""
        return Notification.objects.filter(user=self.request.user, is_active=True)

    @extend_schema(
        summary="Listar notificaciones",
        description="Lista notificaciones del usuario actual (requiere JWT)",
        tags=["Notificaciones"],
        parameters=[
            OpenApiParameter(
                name="is_read",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filtrar por leídas (true) o no leídas (false)",
                required=False,
            ),
        ],
    )
    def list(self, request):
        """Enrutar a service para listar notificaciones."""
        is_read_param = request.query_params.get("is_read")

        # Convertir string a boolean
        is_read = None
        if is_read_param is not None:
            is_read = is_read_param.lower() == "true"

        queryset = NotificationService.list_notifications(request.user, is_read)

        page = self.paginate_queryset(queryset)
        if page:
            serializer = NotificationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = NotificationSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Obtener notificación",
        description="Obtiene detalles de una notificación (requiere JWT)",
        tags=["Notificaciones"],
    )
    def retrieve(self, request, pk=None):
        """Enrutar a service para obtener notificación."""
        try:
            notification = NotificationService.retrieve_notification(pk, request.user)
            serializer = NotificationSerializer(notification)
            return Response(serializer.data)

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Eliminar notificación",
        description="Elimina una notificación (requiere JWT)",
        tags=["Notificaciones"],
    )
    def destroy(self, request, pk=None):
        """Enrutar a service para eliminar notificación."""
        notification = self.get_object()

        try:
            NotificationService.delete_notification(notification, request.user)
            return Response(
                {"message": "Notificación eliminada"},
                status=status.HTTP_204_NO_CONTENT,
            )

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    # ========== Acciones personalizadas ==========

    @extend_schema(
        summary="Marcar como leída",
        description="Marca una notificación como leída (requiere JWT)",
        tags=["Notificaciones"],
    )
    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """Marca una notificación como leída."""
        notification = self.get_object()
        notification.mark_as_read()
        return Response(NotificationSerializer(notification).data)

    @extend_schema(
        summary="Marcar todas como leídas",
        description="Marca todas las notificaciones del usuario como leídas (requiere JWT)",
        tags=["Notificaciones"],
    )
    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """Marca todas las notificaciones como leídas."""
        count = NotificationService.mark_all_as_read(request.user)
        return Response({"marked": count})

    @extend_schema(
        summary="Contar no leídas",
        description="Obtiene el conteo de notificaciones no leídas (requiere JWT)",
        tags=["Notificaciones"],
    )
    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """Obtiene el conteo de notificaciones no leídas."""
        count = NotificationService.get_unread_count(request.user)
        return Response({"unread_count": count})

    @extend_schema(
        summary="Enviar notificación de prueba",
        description="Envía una notificación de prueba por email (requiere JWT)",
        tags=["Notificaciones"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Título de la notificación",
                    },
                    "message": {
                        "type": "string",
                        "description": "Mensaje de la notificación",
                    },
                    "notification_type": {
                        "type": "string",
                        "enum": ["info", "warning", "success", "error"],
                        "default": "info",
                    },
                },
                "required": ["title", "message"],
            }
        },
    )
    @action(detail=False, methods=["post"])
    def send_test_notification(self, request):
        """Envía una notificación de prueba al usuario actual."""
        try:
            title = request.data.get("title", "Notificación de prueba")
            message = request.data.get(
                "message", "Esta es una notificación de prueba del sistema."
            )
            notification_type = request.data.get("notification_type", "info")

            notification = NotificationService.create_notification(
                user=request.user,
                title=title,
                message=message,
                notification_type=notification_type,
                send_email=True,
            )

            serializer = NotificationSerializer(notification)
            return Response(
                {
                    "message": "Notificación de prueba enviada exitosamente",
                    "notification": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(f"Error enviando notificación de prueba: {str(e)}")
            return Response(
                {"error": "Error enviando notificación de prueba"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
