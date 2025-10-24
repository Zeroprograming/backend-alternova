"""
Permisos granulares por rol para el sistema de usuarios.
"""

from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permiso que solo permite acceso a usuarios administradores.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsTeacherUser(permissions.BasePermission):
    """
    Permiso que solo permite acceso a usuarios profesores.
    """

    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and request.user.is_teacher
        )


class IsStudentUser(permissions.BasePermission):
    """
    Permiso que solo permite acceso a usuarios estudiantes.
    """

    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and request.user.is_student
        )


class IsAdminOrTeacher(permissions.BasePermission):
    """
    Permiso que permite acceso a administradores y profesores.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_teacher)
        )


class IsAdminOrStudent(permissions.BasePermission):
    """
    Permiso que permite acceso a administradores y estudiantes.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_student)
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso que permite acceso al propietario del objeto o a administradores.
    """

    def has_object_permission(self, request, view, obj):
        # Administradores pueden acceder a todo
        if request.user.is_staff:
            return True

        # El propietario puede acceder a su propio objeto
        if hasattr(obj, "user"):
            return obj.user == request.user
        elif hasattr(obj, "student"):
            return obj.student == request.user
        elif hasattr(obj, "teacher"):
            return obj.teacher == request.user
        elif hasattr(obj, "generated_by"):
            return obj.generated_by == request.user

        return False


class IsTeacherOfSubject(permissions.BasePermission):
    """
    Permiso que permite acceso solo al profesor de la materia.
    """

    def has_object_permission(self, request, view, obj):
        # Administradores pueden acceder a todo
        if request.user.is_staff:
            return True

        # Solo el profesor de la materia puede acceder
        if hasattr(obj, "subject"):
            return obj.subject.teacher == request.user
        elif hasattr(obj, "teacher"):
            return obj.teacher == request.user

        return False


class CanManageRoles(permissions.BasePermission):
    """
    Permiso que permite gestionar roles de usuarios.
    Solo administradores pueden cambiar roles.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # Solo administradores pueden cambiar roles
        if not request.user.is_staff:
            return False

        # No se puede cambiar el rol de otro administrador
        if obj.is_staff and obj != request.user:
            return False

        return True


class CanAssignGrades(permissions.BasePermission):
    """
    Permiso que permite asignar calificaciones.
    Solo profesores de la materia o administradores.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_teacher)
        )

    def has_object_permission(self, request, view, obj):
        # Administradores pueden asignar calificaciones
        if request.user.is_staff:
            return True

        # Solo el profesor de la materia puede asignar calificaciones
        if hasattr(obj, "subject"):
            return obj.subject.teacher == request.user

        return False


class CanEnrollStudents(permissions.BasePermission):
    """
    Permiso que permite inscribir estudiantes.
    Estudiantes pueden inscribirse a sí mismos, administradores pueden inscribir a cualquiera.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_student)
        )

    def has_object_permission(self, request, view, obj):
        # Administradores pueden inscribir a cualquiera
        if request.user.is_staff:
            return True

        # Estudiantes solo pueden inscribirse a sí mismos
        if hasattr(obj, "student"):
            return obj.student == request.user

        return False


class CanViewAcademicInfo(permissions.BasePermission):
    """
    Permiso que permite ver información académica.
    Estudiantes ven su propia info, profesores ven info de sus materias, admins ven todo.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.user_type in ["student", "teacher", "admin"]
        )

    def has_object_permission(self, request, view, obj):
        # Administradores pueden ver todo
        if request.user.is_staff:
            return True

        # Estudiantes pueden ver su propia información
        if request.user.is_student:
            if hasattr(obj, "student"):
                return obj.student == request.user
            elif hasattr(obj, "user"):
                return obj.user == request.user

        # Profesores pueden ver información de sus materias
        if request.user.is_teacher:
            if hasattr(obj, "subject"):
                return obj.subject.teacher == request.user
            elif hasattr(obj, "teacher"):
                return obj.teacher == request.user

        return False
