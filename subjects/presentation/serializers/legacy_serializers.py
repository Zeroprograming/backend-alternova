"""
Serializers para materias.
"""

from rest_framework import serializers
from ...infrastructure.models import Subject, Enrollment


class SubjectSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)

    class Meta:
        model = Subject
        fields = [
            "id",
            "code",
            "name",
            "description",
            "credits",
            "teacher",
            "teacher_name",
            "semester",
            "created_at",
            "updated_at",
            "is_active",
        ]
        read_only_fields = ["created_at", "updated_at"]


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student",
            "student_name",
            "subject",
            "subject_name",
            "enrolled_at",
            "final_grade",
            "is_active",
        ]
        read_only_fields = ["enrolled_at"]
