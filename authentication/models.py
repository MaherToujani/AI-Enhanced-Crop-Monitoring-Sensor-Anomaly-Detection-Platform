from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with a simple role field.

    Roles are used for basic permissions:
    - farmer: can see their own farms/plots/data
    - admin: can see and manage everything
    """

    ROLE_FARMER = "farmer"
    ROLE_ADMIN = "admin"

    ROLE_CHOICES = [
        (ROLE_FARMER, "Farmer"),
        (ROLE_ADMIN, "Admin"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_FARMER,
    )

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"
