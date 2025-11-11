from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import mark_safe

from apps.accounts.managers.users import UserManager


class User(AbstractUser):
    first_name = None
    last_name = None

    name = models.CharField(max_length=150, blank=False, null=False)
    username = models.CharField(
        max_length=150,
        unique=True,
        error_messages={
            "unique": "A user with that username already exists.",
        },
    )
    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
        error_messages={
            "unique": "A user with that email already exists.",
        },
    )
    image = models.URLField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True, max_length=160)

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email", "name"]

    objects = UserManager()

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        self.username = self.username.lower()
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    @property
    def avatar(self):
        if self.image:
            return self.image
        initials = "".join(part[0].upper() for part in self.name.split()[:2] if part)
        return (
            f"https://ui-avatars.com/api/?name={initials}&background=random&bold=true"
        )

    @property
    def avatar_tag(self):
        img_url = self.avatar
        return mark_safe(
            f'<img src="{img_url}" width="40" height="40" style="border-radius:50%; object-fit: cover;" />'
        )
