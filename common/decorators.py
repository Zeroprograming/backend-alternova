"""
Decoradores personalizados para validaciones y funcionalidades específicas.
"""

import functools
import logging
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from .models import TimeStampedModel
from .audit_services import AuditService

User = get_user_model()
logger = logging.getLogger(__name__)


def validate_prerequisites(func):
    """
    Decorador para validar prerrequisitos de inscripción.

    Valida que el estudiante cumpla con todos los prerrequisitos
    antes de permitir la inscripción en una materia.

    Args:
        func: Función que maneja la inscripción

    Returns:
        Response: Respuesta con error si no cumple prerrequisitos
    """

    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        # Solo aplicar a estudiantes
        if not request.user.is_student:
            return func(self, request, *args, **kwargs)

        # Obtener el subject_id de la URL o request
        subject_id = kwargs.get("pk") or request.data.get("subject_id")

        if not subject_id:
            return Response(
                {"error": "ID de materia requerido para validar prerrequisitos"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from subjects.models import Subject, Prerequisite, Enrollment

            # Obtener la materia
            subject = Subject.objects.get(id=subject_id, is_active=True)

            # Verificar prerrequisitos
            prerequisites = Prerequisite.objects.filter(
                subject=subject, is_active=True
            ).select_related("prerequisite_subject")

            missing_prerequisites = []

            for prereq in prerequisites:
                # Verificar si el estudiante aprobó el prerrequisito
                approved_enrollment = Enrollment.objects.filter(
                    student=request.user,
                    subject=prereq.prerequisite_subject,
                    is_active=True,
                    final_grade__gte=3.0,  # Nota aprobatoria
                ).exists()

                if not approved_enrollment:
                    missing_prerequisites.append(
                        {
                            "subject_code": prereq.prerequisite_subject.code,
                            "subject_name": prereq.prerequisite_subject.name,
                            "credits": prereq.prerequisite_subject.credits,
                        }
                    )

            if missing_prerequisites:
                # Log de intento de inscripción sin prerrequisitos
                AuditService.log_action(
                    user=request.user,
                    action_type="enrollment_prerequisite_failed",
                    description=f"Intento de inscripción en {subject.code} sin prerrequisitos",
                    content_object=subject,
                    extra_data={
                        "missing_prerequisites": missing_prerequisites,
                        "subject_code": subject.code,
                    },
                )

                return Response(
                    {
                        "error": "No cumple con los prerrequisitos requeridos",
                        "missing_prerequisites": missing_prerequisites,
                        "subject_code": subject.code,
                        "subject_name": subject.name,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Log de validación exitosa
            AuditService.log_action(
                user=request.user,
                action_type="prerequisite_validation_success",
                description=f"Prerrequisitos validados para {subject.code}",
                content_object=subject,
                extra_data={"subject_code": subject.code},
            )

            logger.info(
                f"Prerrequisitos validados para {request.user.username} en {subject.code}"
            )

        except Subject.DoesNotExist:
            return Response(
                {"error": "Materia no encontrada"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error validando prerrequisitos: {e}")
            return Response(
                {"error": "Error interno validando prerrequisitos"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Si todo está bien, ejecutar la función original
        return func(self, request, *args, **kwargs)

    return wrapper


def validate_credits_limit(func):
    """
    Decorador para validar límite de créditos del estudiante.

    Valida que el estudiante no exceda su límite de créditos
    antes de permitir la inscripción.

    Args:
        func: Función que maneja la inscripción

    Returns:
        Response: Respuesta con error si excede límite de créditos
    """

    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        # Solo aplicar a estudiantes
        if not request.user.is_student:
            return func(self, request, *args, **kwargs)

        # Obtener el subject_id de la URL o request
        subject_id = kwargs.get("pk") or request.data.get("subject_id")

        if not subject_id:
            return func(self, request, *args, **kwargs)

        try:
            from subjects.models import Subject

            # Obtener la materia
            subject = Subject.objects.get(id=subject_id, is_active=True)

            # Verificar límite de créditos
            student = request.user
            available_credits = student.available_credits

            if subject.credits > available_credits:
                # Log de intento de inscripción excediendo créditos
                AuditService.log_action(
                    user=request.user,
                    action_type="enrollment_credits_exceeded",
                    description=f"Intento de inscripción excediendo créditos en {subject.code}",
                    content_object=subject,
                    extra_data={
                        "required_credits": subject.credits,
                        "available_credits": available_credits,
                        "max_credits": student.max_credits_per_semester,
                        "current_credits": student.current_semester_credits,
                    },
                )

                return Response(
                    {
                        "error": "Créditos insuficientes para inscribirse",
                        "required_credits": subject.credits,
                        "available_credits": available_credits,
                        "max_credits_per_semester": student.max_credits_per_semester,
                        "current_semester_credits": student.current_semester_credits,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            logger.info(
                f"Límite de créditos validado para {request.user.username} en {subject.code}"
            )

        except Subject.DoesNotExist:
            return Response(
                {"error": "Materia no encontrada"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error validando límite de créditos: {e}")
            return Response(
                {"error": "Error interno validando límite de créditos"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Si todo está bien, ejecutar la función original
        return func(self, request, *args, **kwargs)

    return wrapper


def validate_grade_range(func):
    """
    Decorador para validar rango de calificaciones.

    Valida que la calificación esté en el rango válido (0.0 - 5.0)
    antes de permitir la asignación de nota.

    Args:
        func: Función que maneja la asignación de calificaciones

    Returns:
        Response: Respuesta con error si la calificación no es válida
    """

    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        # Solo aplicar a profesores y administradores
        if not (request.user.is_teacher or request.user.is_staff):
            return func(self, request, *args, **kwargs)

        # Obtener la calificación del request
        grade = request.data.get("grade")

        if grade is not None:
            try:
                grade_float = float(grade)

                if grade_float < 0.0 or grade_float > 5.0:
                    # Log de intento de calificación inválida
                    AuditService.log_action(
                        user=request.user,
                        action_type="invalid_grade_attempt",
                        description=f"Intento de asignar calificación inválida: {grade_float}",
                        extra_data={
                            "attempted_grade": grade_float,
                            "valid_range": "0.0 - 5.0",
                        },
                    )

                    return Response(
                        {
                            "error": "La calificación debe estar entre 0.0 y 5.0",
                            "provided_grade": grade_float,
                            "valid_range": "0.0 - 5.0",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                logger.info(
                    f"Rango de calificación validado: {grade_float} por {request.user.username}"
                )

            except (ValueError, TypeError):
                return Response(
                    {"error": "La calificación debe ser un número válido"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Si todo está bien, ejecutar la función original
        return func(self, request, *args, **kwargs)

    return wrapper


def log_action(action_type, description=None):
    """
    Decorador para registrar acciones específicas en el sistema de auditoría.

    Args:
        action_type: Tipo de acción a registrar
        description: Descripción personalizada de la acción

    Returns:
        Decorador que registra la acción
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, *args, **kwargs):
            try:
                # Ejecutar la función original
                response = func(self, request, *args, **kwargs)

                # Registrar la acción si fue exitosa (status 2xx)
                if (
                    hasattr(response, "status_code")
                    and 200 <= response.status_code < 300
                ):
                    AuditService.log_action(
                        user=request.user,
                        action_type=action_type,
                        description=description or f"Acción {action_type} ejecutada",
                        extra_data={
                            "endpoint": request.path,
                            "method": request.method,
                            "status_code": response.status_code,
                        },
                    )

                return response

            except Exception as e:
                # Registrar error si ocurre
                AuditService.log_action(
                    user=request.user,
                    action_type=f"{action_type}_error",
                    description=f"Error en {action_type}: {str(e)}",
                    extra_data={
                        "endpoint": request.path,
                        "method": request.method,
                        "error": str(e),
                    },
                )
                raise

        return wrapper

    return decorator
