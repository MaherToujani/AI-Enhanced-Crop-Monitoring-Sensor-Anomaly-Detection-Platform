from django.contrib import admin

from .models import SensorReading


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ("plot", "sensor_type", "value", "timestamp", "source")
    list_filter = ("sensor_type", "source", "plot__farm")
    search_fields = ("plot__name", "plot__farm__name")
    date_hierarchy = "timestamp"
