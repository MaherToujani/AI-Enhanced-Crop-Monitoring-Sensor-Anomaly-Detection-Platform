from django.contrib import admin

from .models import FarmProfile, FieldPlot


@admin.register(FarmProfile)
class FarmProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "location", "size_hectares", "crop_type", "created_at")
    list_filter = ("crop_type", "location", "owner")
    search_fields = ("name", "owner__username", "location", "crop_type")


@admin.register(FieldPlot)
class FieldPlotAdmin(admin.ModelAdmin):
    list_display = ("name", "farm", "crop_variety", "area_hectares", "created_at")
    list_filter = ("farm", "crop_variety")
    search_fields = ("name", "farm__name", "crop_variety")
