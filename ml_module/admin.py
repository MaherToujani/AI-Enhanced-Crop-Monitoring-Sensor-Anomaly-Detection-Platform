from django.contrib import admin

from .models import AnomalyEvent


@admin.register(AnomalyEvent)
class AnomalyEventAdmin(admin.ModelAdmin):
    list_display = ("plot", "anomaly_type", "severity", "model_confidence", "timestamp")
    list_filter = ("anomaly_type", "severity", "plot__farm")
    search_fields = ("plot__name", "plot__farm__name")
    date_hierarchy = "timestamp"
