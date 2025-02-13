from django.contrib.auth.models import AbstractUser
from django.db import models

class UserRole(models.TextChoices):
    ADMIN = "Admin", "Admin"
    OWNER = "Owner", "Owner"
    USER = "User", "User"

class CustomUser(AbstractUser):
    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.USER  # Default role is "User"
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
