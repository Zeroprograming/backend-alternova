"""
Views para materias.
SOLO enrutamiento - Toda la lógica en SubjectService.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from ...infrastructure.models import Subject, Enrollment
from ..serializers.legacy_serializers import SubjectSerializer, EnrollmentSerializer
from ...application.services.legacy_services import SubjectService
from ..permissions.permissions import IsTeacherOfSubject
from common.infrastructure.external.decorators import (
    validate_prerequisites,
    validate_credits_limit,
    validate_grade_range,
    log_action,
)
import logging

logger = logging.getLogger(__name__)


class SubjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de materias con JWT y validaciones.
    La lógica compleja está delegada en SubjectService.
    """

    queryset = Subject.objects.filter(is_active=True)
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Permisos personalizados por acción."""
        if self.action in ["create", "destroy"]:
            # Solo admin puede crear/eliminar materias
            return [IsAuthenticated(), IsAdminUser()]
        elif self.action in ["update", "partial_update"]:
            # Admin o profesor de la materia
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        """Queryset según tipo de usuario."""
        user = self.request.user

        if user.is_staff:
            return Subject.objects.filter(is_active=True)
        elif user.is_teacher:
            return Subject.objects.filter(teacher=user, is_active=True)
        elif user.is_student:
            return Subject.objects.filter(
                enrollments__student=user, enrollments__is_active=True
            ).distinct()
        return Subject.objects.none()

    @extend_schema(
        summary="Listar materias",
        description="Lista materias según el rol del usuario (requiere JWT)",
        tags=["Materias"],
        parameters=[
            OpenApiParameter(
                name="semester",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filtrar por semestre",
                required=False,
            ),
            OpenApiParameter(
                name="teacher",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filtrar por ID del profesor",
                required=False,
            ),
        ],
    )
    def list(self, request):
        """Enrutar a service para listar materias."""
        semester = request.query_params.get("semester")
        teacher_id = request.query_params.get("teacher")

        # Delegar a service
        queryset = SubjectService.list_subjects(request.user, semester, teacher_id)

        # Paginación
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubjectSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = SubjectSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Obtener materia",
        description="Obtiene detalles de una materia (requiere JWT)",
        tags=["Materias"],
    )
    def retrieve(self, request, pk=None):
        """Enrutar a service para obtener materia."""
        try:
            # Delegar a service (incluye validación de permisos)
            subject = SubjectService.retrieve_subject(pk, request.user)
            serializer = SubjectSerializer(subject)
            return Response(serializer.data)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Crear materia",
        description="Crea una nueva materia (solo admin, requiere JWT)",
        tags=["Materias"],
        examples=[
            OpenApiExample(
                "Ejemplo de materia",
                value={
                    "code": "MAT101",
                    "name": "Matemáticas I",
                    "description": "Introducción al cálculo",
                    "credits": 3,
                    "teacher": 1,
                    "semester": 1,
                },
                request_only=True,
            ),
        ],
    )
    def create(self, request):
        """Enrutar a service para crear materia."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Delegar a service
            subject = SubjectService.create_subject(
                requesting_user=request.user, **serializer.validated_data
            )
            return Response(
                SubjectSerializer(subject).data, status=status.HTTP_201_CREATED
            )

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Actualizar materia",
        description="Actualiza una materia (profesor o admin, requiere JWT)",
        tags=["Materias"],
    )
    def update(self, request, pk=None):
        """Enrutar a service para actualizar materia."""
        subject = self.get_object()
        serializer = SubjectSerializer(subject, data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated_subject = SubjectService.update_subject(
                subject, serializer.validated_data, request.user
            )
            return Response(SubjectSerializer(updated_subject).data)

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    @extend_schema(
        summary="Actualizar materia parcial",
        description="Actualiza campos específicos de una materia (requiere JWT)",
        tags=["Materias"],
    )
    def partial_update(self, request, pk=None):
        """Enrutar a service para actualización parcial."""
        subject = self.get_object()
        serializer = SubjectSerializer(subject, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            updated_subject = SubjectService.update_subject(
                subject, serializer.validated_data, request.user
            )
            return Response(SubjectSerializer(updated_subject).data)

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    @extend_schema(
        summary="Eliminar materia",
        description="Elimina una materia (solo admin, requiere JWT)",
        tags=["Materias"],
    )
    def destroy(self, request, pk=None):
        """Enrutar a service para eliminar materia."""
        subject = self.get_object()

        try:
            SubjectService.delete_subject(subject, request.user)
            return Response(
                {"message": "Materia eliminada exitosamente"},
                status=status.HTTP_204_NO_CONTENT,
            )

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ========== Acciones personalizadas ==========

    @extend_schema(
        summary="Inscribir estudiante",
        description="Inscribe al usuario actual en la materia (requiere JWT)",
        tags=["Materias"],
    )
    @action(detail=True, methods=["post"])
    @validate_prerequisites
    @validate_credits_limit
    @log_action("student_enrollment", "Estudiante se inscribió en materia")
    def enroll(self, request, pk=None):
        """Enrutar a service para inscribir estudiante."""
        subject = self.get_object()
        student = request.user

        try:
            enrollment = SubjectService.enroll_student(student, subject)
            return Response(
                EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Asignar nota",
        description="Asigna nota a un estudiante (solo profesor de la materia, requiere JWT)",
        tags=["Materias"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "enrollment_id": {"type": "integer"},
                    "grade": {"type": "number", "minimum": 0, "maximum": 5},
                },
                "required": ["enrollment_id", "grade"],
            }
        },
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    @validate_grade_range
    @log_action("grade_assignment", "Profesor asignó calificación")
    def assign_grade(self, request, pk=None):
        """Enrutar a service para asignar nota."""
        subject = self.get_object()
        enrollment_id = request.data.get("enrollment_id")
        grade = request.data.get("grade")

        if not enrollment_id or grade is None:
            return Response(
                {"error": "enrollment_id y grade son requeridos"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            enrollment = Enrollment.objects.get(id=enrollment_id, subject=subject)
            updated_enrollment = SubjectService.assign_grade(
                enrollment, float(grade), request.user
            )
            return Response(EnrollmentSerializer(updated_enrollment).data)

        except Enrollment.DoesNotExist:
            return Response(
                {"error": "Inscripción no encontrada"}, status=status.HTTP_404_NOT_FOUND
            )
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de inscripciones con JWT.
    """

    queryset = Enrollment.objects.filter(is_active=True)
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtrar por usuario actual si es estudiante."""
        user = self.request.user

        if user.is_staff:
            return self.queryset
        elif user.is_teacher:
            # Profesor ve inscripciones de sus materias
            return self.queryset.filter(subject__teacher=user)
        elif user.is_student:
            # Estudiante solo ve sus inscripciones
            return self.queryset.filter(student=user)
        return Enrollment.objects.none()

    @extend_schema(
        summary="Listar inscripciones",
        description="Lista inscripciones según el rol (requiere JWT)",
        tags=["Inscripciones"],
        parameters=[
            OpenApiParameter(
                name="subject",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filtrar por ID de materia",
                required=False,
            ),
            OpenApiParameter(
                name="student",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filtrar por ID de estudiante",
                required=False,
            ),
        ],
    )
    def list(self, request):
        """Enrutar a service para listar inscripciones."""
        from .enrollment_services import EnrollmentService

        subject_id = request.query_params.get("subject")
        student_id = request.query_params.get("student")

        queryset = EnrollmentService.list_enrollments(
            request.user, subject_id, student_id
        )

        page = self.paginate_queryset(queryset)
        if page:
            serializer = EnrollmentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = EnrollmentSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Obtener inscripción",
        description="Obtiene detalles de una inscripción (requiere JWT)",
        tags=["Inscripciones"],
    )
    def retrieve(self, request, pk=None):
        """Enrutar a service para obtener inscripción."""
        from .enrollment_services import EnrollmentService

        try:
            enrollment = EnrollmentService.retrieve_enrollment(pk, request.user)
            serializer = EnrollmentSerializer(enrollment)
            return Response(serializer.data)

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Crear inscripción",
        description="Crea una nueva inscripción (requiere JWT)",
        tags=["Inscripciones"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "student": {"type": "integer", "description": "ID del estudiante"},
                    "subject": {"type": "integer", "description": "ID de la materia"},
                },
                "required": ["student", "subject"],
            }
        },
    )
    def create(self, request):
        """Enrutar a service para crear inscripción."""
        from .enrollment_services import EnrollmentService
        from .models import Subject
        from users.models import User

        # Validar datos requeridos
        student_id = request.data.get("student")
        subject_id = request.data.get("subject")

        if not student_id or not subject_id:
            return Response(
                {"error": "Se requieren student y subject"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Obtener objetos
            student = User.objects.get(id=student_id, is_active=True)
            subject = Subject.objects.get(id=subject_id, is_active=True)

            # Crear inscripción
            enrollment = EnrollmentService.create_enrollment(
                student, subject, request.user
            )

            return Response(
                EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED
            )

        except User.DoesNotExist:
            return Response(
                {"error": "Estudiante no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )
        except Subject.DoesNotExist:
            return Response(
                {"error": "Materia no encontrada"}, status=status.HTTP_404_NOT_FOUND
            )
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Actualizar inscripción",
        description="Actualiza una inscripción (solo profesor, requiere JWT)",
        tags=["Inscripciones"],
    )
    def update(self, request, pk=None):
        """Enrutar a service para actualizar."""
        from .enrollment_services import EnrollmentService

        enrollment = self.get_object()
        serializer = EnrollmentSerializer(enrollment, data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated = EnrollmentService.update_enrollment(
                enrollment, serializer.validated_data, request.user
            )
            return Response(EnrollmentSerializer(updated).data)

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    @extend_schema(
        summary="Actualizar inscripción parcial",
        description="Actualiza campos específicos (requiere JWT)",
        tags=["Inscripciones"],
    )
    def partial_update(self, request, pk=None):
        """Enrutar a service para actualización parcial."""
        from .enrollment_services import EnrollmentService

        enrollment = self.get_object()
        serializer = EnrollmentSerializer(enrollment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            updated = EnrollmentService.update_enrollment(
                enrollment, serializer.validated_data, request.user
            )
            return Response(EnrollmentSerializer(updated).data)

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    @extend_schema(
        summary="Eliminar inscripción",
        description="Elimina una inscripción (requiere JWT)",
        tags=["Inscripciones"],
    )
    def destroy(self, request, pk=None):
        """Enrutar a service para eliminar inscripción."""
        from .enrollment_services import EnrollmentService

        enrollment = self.get_object()

        try:
            EnrollmentService.delete_enrollment(enrollment, request.user)
            return Response(
                {"message": "Inscripción eliminada"}, status=status.HTTP_204_NO_CONTENT
            )

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Des-inscribirse",
        description="Des-inscribe al estudiante de la materia (requiere JWT)",
        tags=["Inscripciones"],
    )
    @action(detail=True, methods=["post"])
    def unenroll(self, request, pk=None):
        """Enrutar a service para des-inscribir."""
        enrollment = self.get_object()

        try:
            SubjectService.unenroll_student(enrollment, request.user)
            return Response(
                {"message": "Des-inscripción exitosa"}, status=status.HTTP_200_OK
            )

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
