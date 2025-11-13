from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import mark_safe

from apps.accounts.managers.users import UserManager
from apps.core.models import TimeStampedModel


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


class Follow(TimeStampedModel):
    follower = models.ForeignKey(
        User,
        related_name="following",
        on_delete=models.CASCADE,
        help_text="User who is following another user.",
    )
    followed = models.ForeignKey(
        User,
        related_name="followers",
        on_delete=models.CASCADE,
        help_text="User who is being followed.",
    )

    class Meta:
        verbose_name = "Follow"
        verbose_name_plural = "Follows"
        ordering = ["-created_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "followed"], name="unique_follow"
            )
        ]
        indexes = [
            models.Index(fields=["follower", "-created_date"]),
            models.Index(fields=["followed", "-created_date"]),
        ]

    def __str__(self):
        return f"@{self.follower} follows @{self.followed}"

    def clean(self):
        if self.follower == self.followed:
            raise ValidationError("Users cannot follow themselves.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
