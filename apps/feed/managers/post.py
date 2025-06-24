from django.db import models


class PostQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(author=user)

    def with_comments(self):
        return self.prefetch_related("comments")

    def with_reactions(self):
        return self.prefetch_related("reactions")

    def original(self):
        return self.filter(parent__isnull=True)

    def reposts(self):
        return self.filter(parent__isnull=False, body__isnull=True)

    def quotes(self):
        return self.filter(parent__isnull=False).exclude(body__isnull=True)


class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def for_user(self, user):
        return self.get_queryset().for_user(user)

    def with_comments(self):
        return self.get_queryset().with_comments()

    def with_reactions(self):
        return self.get_queryset().with_reactions()

    def original(self):
        return self.get_queryset().original()

    def reposts(self):
        return self.get_queryset().reposts()

    def quotes(self):
        return self.get_queryset().quotes()
