from django.contrib import admin

from .models import AgentRecommendation


@admin.register(AgentRecommendation)
class AgentRecommendationAdmin(admin.ModelAdmin):
    list_display = ("anomaly_event", "recommended_action", "confidence", "timestamp")
    list_filter = ("confidence", "anomaly_event__anomaly_type", "anomaly_event__severity")
    search_fields = ("recommended_action", "anomaly_event__plot__name")
