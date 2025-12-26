from django.conf import settings
from django.db import models


class FarmProfile(models.Model):
    """
    Represents a farm owned by a user.

    Kept simple and extensible so we can add more fields later
    (e.g. region, irrigation_type) without breaking the core design.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="farms",
    )
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True)
    size_hectares = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Approximate farm size in hectares.",
    )
    crop_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="Main crop type grown on this farm (e.g. Wheat, Corn).",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.owner.username})"


class FieldPlot(models.Model):
    """
    Represents a specific plot/field within a farm.

    Sensors and readings are attached to plots, not entire farms.
    """

    farm = models.ForeignKey(
        FarmProfile,
        on_delete=models.CASCADE,
        related_name="plots",
    )
    name = models.CharField(max_length=100)
    crop_variety = models.CharField(
        max_length=100,
        blank=True,
        help_text="Specific crop variety planted in this plot.",
    )
    area_hectares = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Plot size in hectares.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["farm", "name"]
        unique_together = ("farm", "name")

    def __str__(self) -> str:
        return f"{self.name} - {self.farm.name}"
