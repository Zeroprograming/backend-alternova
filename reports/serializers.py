"""Serializers para reportes."""

from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(
        source="generated_by.full_name", read_only=True
    )

    class Meta:
        model = Report
        fields = [
            "id",
            "title",
            "report_type",
            "status",
            "filters",
            "file",
            "generated_by",
            "generated_by_name",
            "created_at",
            "completed_at",
        ]
        read_only_fields = ["status", "completed_at", "generated_by"]


class ReportCreateSerializer(serializers.Serializer):
    """Serializer para crear reportes."""

    title = serializers.CharField(max_length=200)
    report_type = serializers.ChoiceField(choices=Report.REPORT_TYPES)
    filters = serializers.JSONField(default=dict, required=False)
