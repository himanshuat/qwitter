from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides a created_date field
    and default ordering by most recently created first.
    """

    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ["-created_date"]


class ExtendedTimeStampedModel(TimeStampedModel):
    """
    Abstract base model that extends TimeStampedModel by adding
    an edited_date field which updates automatically on save.
    """

    edited_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
